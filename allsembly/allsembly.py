# Copyright © 2021 Waleed H. Mebane
#
#   This file is part of Allsembly™ Prototype.
#
#   Allsembly™ Prototype is free software: you can redistribute it and/or
#   modify it under the terms of the Lesser GNU General Public License,
#   version 3, as published by the Free Software Foundation and the
#   additional terms found in the accompanying file named "LICENSE.txt".
#
#   Allsembly™ Prototype is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   Lesser GNU General Public License for more details.
#
#   You should have received a copy of the Lesser GNU General Public
#   License along with Allsembly™ Prototype.  If not, see
#   <https://www.gnu.org/licenses/>.
#

""" allsembly.py
Module for building the Allsembly™ server

The server will be a script that reads
in the configuration and then calls
the server main loop function in this
module.  (See scripts/allsembly-server.py)

Overview:
Allow users to contribute to an unfolding policy deliberation 
and obtain updates of the changes made by others.

Users contribute *arguments*, which are sets of statements
that support or rebut other statements added earlier.

Comprehending subjective beliefs in statements as evidence
of their truth, the software estimates the truth of statements
using a Bayesian network that is constructed implicitly using
the Problog module (a probabilistic logic programming
language).

In order to obtain the prior probabilities, the software needs
to aggregate the judgements of the users, and it does that
using betting markets.  A betting market elicits something close
to the true belief in the truth value of the statement being
bet on because, if the user is rational, they adjust their 
risk to their beliefs.  (Although, of course, different users
may have different risk tolerances.)
NOTE: The betting market code is not fully implemented, and it
is not used by the current server.  Instead the server serves
a client in a single user ("sandboxed") mode and accepts whatever
their bid is as the price.  So the user can manually simulate
what would happen if the price were thus and so.

The software will implement a betting exchange containing one
market for every set of statements that is separately 
contestable.  The markets use limit order books implemented
as pairs of priority queues.  More details will be in the
external documentation, and some details can be found in the
docstrings of the betting_exchange module.

This implements a server that provides the following services:
User's may connect to the server and:
Contribute new statements and policy proposals
Attempt to buy (bid on) betting contracts
Get updates on the current state of the deliberation,
  including new contributions, current prices, and estimates
  of the truth value of sets of statements.
"""
import logging
from logging import Logger

import transaction #type: ignore[import]
import ZODB, ZODB.FileStorage #type: ignore[import]
import rpyc #type: ignore[import]

from typing import TextIO, Dict
#from queue import Queue
import time
from time import thread_time_ns
from typing import Optional
from typing import List
from typing import Any
#from typing import BinaryIO
from rpyc.utils.helpers import classpartial #type: ignore[import]
from typing_extensions import Final

from allsembly.argument_graph import Issues, IssuesDBAccessor, build_ArgumentNode, build_PositionNode, ArgumentGraph
from allsembly.speech_act import IndependentBid, MarketLocator
from allsembly.betting_exchange import BettingMarket
from allsembly.common import FinalVar
from allsembly.config import Config
from allsembly.config import Limits
from allsembly import CONSTANTS
import threading
from threading import Event

from allsembly.rpyc_server import AllsemblyServices, GraphRequest, LedgerRequest, GraphUpdatePosQueue, \
    OrderQueue, IssueQueue, GraphUpdateArgQueue, IssueDeleteDirective
from allsembly.speech_act import ProOrCon, UnconcededPosition

logger: Logger = logging.getLogger(__name__)

# class PicklableAtomicLong(AtomicLong):
#    """ AtomicLong is a module
#    written in C, and so is not picklable.
#    Use this class instead when serialization using Pickle is
#    required, such as with ZODB persistence.
#    """
    #This class is a wrapper implementing __getstate__
    # and __setstate__ so that an AtomicLong object may be pickled.
#
#    def __init__(self, initial_value: Optional[int] = None):
#        super().__init__(initial_value)
#
#    def __getstate__(self) -> Any:
#        return {'value': super().value}
#
#    def __setstate__(self, state: Dict[Any, Any]) -> None:
#        super().__init__(0)
#        super().get_and_set(state['value'])


class ServerControl:
    """Use this to tell the server_main_loop to exit,
       by setting "should_exit" by calling set_should_exit().
       If you run server_main_loop from a separate thread,
       use ServerControlThreadSafe instead.
       If you re-run a server after it exits, you may need
       to reset "should_exit" first by calling
       reset_should_exit().  That is not currently necessary in
       AllsemblyServer.server_main_loop(...).
       A server should call should_exit() periodically, such as in
       a main while loop, to check whether it should exit.
    """
    def __init__(self) -> None:
        self._should_exit: int = 0
        self._event_obj: Event = Event()

    def set_should_exit(self) -> None:
        self._should_exit = 1
        self._event_obj.set()

    def reset_should_exit(self) -> None:
        self._should_exit = 0

    def should_exit(self) -> bool:
        return bool(self._should_exit)

    def get_event_obj(self) -> Event:
        return self._event_obj

# class ServerControlThreadSafe(ServerControl):
#    """Thread safe version of ServerControl
#       Use this to tell the server_main_loop to exit,
#       by setting "should_exit".
#    """
    # Replace integer used in ServerControl
    # with thread-safe atomic integer
    # noinspection PyMissingConstructor
#    def __init__(self) -> None:
#        self._should_exit: AtomicLong = AtomicLong(0)


def process_one_argument_from_queue(issues: Issues,
    graph_arg_queue: GraphUpdateArgQueue,
    order_queue: OrderQueue) -> bool:
    """ Return true if graph_arg_queue is not empty
        after processing one item from the queue;
        False otherwise
    """
    if graph_arg_queue:
        current_update = graph_arg_queue.popleft()
        updating_user_userid = current_update[0]
        update_issue = current_update[2]
        new_arg = current_update[3]

        new_arg_node = build_ArgumentNode(updating_user_userid,
                         new_arg.pro_or_con is ProOrCon.PRO,
                         new_arg.target_position.pos_id
                         )

        if issues.graphs.has_key(update_issue):
            for i, p in enumerate(new_arg.premises):
                same_as_list: List[int]
                statement: str
                if isinstance(p, UnconcededPosition):
                    existing_position = issues.graphs[update_issue]\
                                              .get_position_copy(
                                                  p.pos_id
                                               )
                    same_as_list = list(existing_position.same_as)
                    same_as_list.append(p.pos_id)
                    statement = existing_position.statement
                else:
                    same_as_list = []
                    statement = p.statement

                pos_id = issues.graphs[update_issue].add_position(
                               build_PositionNode(
                                 updating_user_userid,
                                 statement,
                                 same_as_list)
                               )
                new_arg_node.premises_ids.append(pos_id)
                #put new premise bids on order queue
                order_queue.append((current_update[0],
                                   current_update[1],
                                   IndependentBid(p.bid.max_price,
                                     p.bid.min_price,
                                     MarketLocator(update_issue[1],
                                       pos_id),
                                     ProOrCon.PRO
                                   )
                                  )
                                )
                process_one_order_from_queue(issues, order_queue)

            issues.graphs[update_issue].add_argument(new_arg_node)

            #put new argument bid on order queue
            if new_arg.bid_on_target is not None:
                order_queue.append((current_update[0],
                                    current_update[1],
                                   IndependentBid(
                                     new_arg.bid_on_target.max_price,
                                     new_arg.bid_on_target.min_price,
                                     MarketLocator(update_issue[1],
                                       new_arg_node.conclusion_id),
                                     new_arg.pro_or_con
                                   )
                                  )
                                )

    return bool(graph_arg_queue)


def process_one_position_from_queue(issues: Issues,
      graph_pos_queue: GraphUpdatePosQueue) -> bool:
    """ Return true if graph_pos_queue is not empty
        after processing one item from the queue;
        False otherwise
    """
    if graph_pos_queue:
        current_update = graph_pos_queue.popleft()
        updating_user_userid = current_update[0]
        update_issue = current_update[2]
        new_pos = current_update[3]
        #ignore premises
        #TODO: fix: initial position should not have premises;
        #  they can be added later as an argument
        logger.debug(update_issue)
        if not issues.graphs.has_key(update_issue) and \
               update_issue[1] < Limits.max_total_issues:
            issues.graphs[update_issue] = ArgumentGraph("")
            logger.debug("inside not has_key")
        if issues.graphs.has_key(update_issue):
            logger.debug("inside has_key")
            new_pos_id: int  = issues.graphs[update_issue].add_position(
                       build_PositionNode(
                         updating_user_userid,
                         new_pos.conclusion)
                       )
    return bool(graph_pos_queue)

def process_one_order_from_queue(issues: Issues,
                                 order_queue: OrderQueue) -> bool:
    """ Return true if order_queue is not empty
        after processing one item from the queue;
        False otherwise
    """
    if order_queue:
        current_order = order_queue.popleft()
        bidding_user_userid = current_order[0]
        bidding_subuser = current_order[1]
        issue_id = current_order[2].market_locator.issue_id
        market_id = current_order[2].market_locator.position_id
        pro_or_con = current_order[2].pro_or_con
        new_bid = current_order[2]
        if issues.graphs.has_key((bidding_user_userid, issue_id)):
            #temporarily accept the max price given
            #order book is not implemented, yet
            if not issues.graphs[(bidding_user_userid, issue_id)].betting_exchange\
                .markets.has_key(market_id):
                issues.graphs[(bidding_user_userid, issue_id)].betting_exchange\
                .markets[market_id] = BettingMarket()
            issues.graphs[(bidding_user_userid, issue_id)].betting_exchange\
                .markets[market_id].last_support_price = \
                new_bid.max_price if pro_or_con is ProOrCon.PRO \
                    else 1.0 - new_bid.min_price
    return bool(order_queue)


def process_one_issue_from_queue(issues: Issues, 
                                 issue_queue: IssueQueue) -> bool:
    """ Return true if issue_queue is not empty after
        processing one item from the queue;
        False otherwise
    """
    if issue_queue.queue:
        issue_queue_item: Final = issue_queue.queue.popleft()
        if isinstance(issue_queue_item, IssueDeleteDirective):
            issue_id_to_delete: Final = issue_queue_item.id_to_delete
            if issues.graphs.has_key(issue_id_to_delete):
                del issues.graphs[issue_id_to_delete]
        else: #if isinstance(issue_queue_item, IssueAddDirective):
            issue_to_add: Final = issue_queue_item
            issue_id = issue_to_add[0]
            issue_name = issue_to_add[1]
            if not issues.graphs.has_key(issue_to_add[0]):
                issues.graphs[issue_id] = ArgumentGraph(issue_name)
            else: # rename issue
                issues.graphs[issue_id].issue_name = issue_name
    return bool(issue_queue.queue)


class AllsemblyServer:
    """ server_main_loop function starts the server
        I put it in a class so that its data can be saved
        to be inspected after the server exits.
        It could also be inspected while the server is
        running if the caller is in a separate thread and
        uses locks to synchronize access
    """
    def __init__(self,
                         user_dbfilename: str,
                         arg_dbfilename: str
                ):
        #open database for: orderbook, ledger, & arg_graph
        #TODO: check for errors; exit if can't open DB
        self.argumentdb_storage = ZODB.FileStorage.FileStorage(arg_dbfilename)
        self.argumentdb = ZODB.DB(self.argumentdb_storage)
        self.argdb_conn = self.argumentdb.open()
        #create the queues: order_queue, graph_update_queue
        #create separate queues for guests?
        #TODO: additions to the queue, when they are full will just get
        #  discarded without notice.  That is not the behavoir I prefer.
        #  Attend to that in a future version.
        self.order_queue: OrderQueue = OrderQueue()
        self.graph_arg_queue: GraphUpdateArgQueue = GraphUpdateArgQueue()
        self.graph_pos_queue: GraphUpdatePosQueue = GraphUpdatePosQueue()

        #Load the data into BettingExchange and ArgumentGraph
        #  instances &
        #  use the ArgumentGraph data to draw an initial arg diagram
        #  and to create or load an initial problog_model
        #otherwise create new empty instances
        self.dbroot = self.argdb_conn.root()
        #gets "issues" from database if it exists; otherwise adds it
        #TODO: store path in database to "issues" somehow in CONSTANTS
        if not hasattr(self.dbroot, "issues"):
            self.dbroot.issues = Issues()
        transaction.commit()
        self.issues = self.dbroot.issues
        self.issue_queue = IssueQueue(self.issues)


    @classmethod
    def check_timeout(cls,
                      timeout_msec: Optional[int],
                      start_time_msec: int,
                      end_time_msec: int) -> bool:
        """Convenience function:
        Return true if the difference between end_time_msec
        and start_time_msec is greater than or equal to timeout_msec
        indicating that the timeout has expired;
        Otherwise, return false.
        """
        if timeout_msec is None:
            return False

        if end_time_msec - start_time_msec < timeout_msec:
            return False
        else:
            return True

    @classmethod
    def check_should_exit(cls, server_control: Optional[ServerControl]
                          ) -> bool:
        if server_control is None:
            return False
        return server_control.should_exit()

    def process_all_issues_from_queue(self,
                                      timeout_msecs: Optional[int],
                                      loop_sentinel_ref: Optional[ServerControl]
                                      ) -> None:
        start_time = thread_time_ns()
        current_time = start_time
        while not AllsemblyServer.check_should_exit(loop_sentinel_ref) and \
            not AllsemblyServer.check_timeout(
                timeout_msecs,
                int(start_time / CONSTANTS.MILLION),
                int(current_time / CONSTANTS.MILLION)
            ):
            queue_is_empty = FinalVar[bool](not process_one_issue_from_queue(
                self.issues,
                self.issue_queue))
            # logger.debug("inside loop for process_one_issue_from_queue")
            transaction.commit()
            if queue_is_empty.get():
                break
            current_time = thread_time_ns()
            # logger.debug((current_time - start_time) / CONSTANTS.MILLION)

    def process_all_orders_from_queue(self,
                                      timeout_msecs: Optional[int],
                                      loop_sentinel_ref: Optional[ServerControl]
                                      ) -> None:
        start_time = thread_time_ns()
        current_time = start_time
        #logger.debug(bool(self.order_queue))
        while not AllsemblyServer.check_should_exit(loop_sentinel_ref) and \
            not AllsemblyServer.check_timeout(
                timeout_msecs,
                int(start_time / CONSTANTS.MILLION),
                int(current_time / CONSTANTS.MILLION)):
            queue_is_empty = FinalVar[bool](not process_one_order_from_queue(
            self.issues,
            self.order_queue))
            # logger.debug("inside loop for process_one_order_from_queue")
            # commit the transaction after each order is processed
            transaction.commit()
            if queue_is_empty.get():
                break
            # set time for elapsed time check
            current_time = thread_time_ns()
            # logger.debug((current_time - start_time) / CONSTANTS.MILLION)

    def process_all_positions_from_queue(self,
                                         timeout_msecs: Optional[int],
                                         loop_sentinel_ref: Optional[ServerControl]
                                         ) -> None:
        start_time = thread_time_ns()
        current_time = start_time
        #logger.debug(list(self.graph_pos_queue))
        #logger.debug(bool(self.graph_pos_queue))
        while not AllsemblyServer.check_should_exit(loop_sentinel_ref) and \
            not AllsemblyServer.check_timeout(
                timeout_msecs,
                int(start_time / CONSTANTS.MILLION),
                int(current_time / CONSTANTS.MILLION)
                                              ):
            queue_is_empty = FinalVar[bool](not process_one_position_from_queue(
                self.issues,
                self.graph_pos_queue))
            # logger.debug("inside loop for process_one_position_from_queue")
            # no bids need processing, so transaction is complete
            transaction.commit()
            if queue_is_empty.get():
                break
            # set time for elapsed time check
            current_time = thread_time_ns()
            # logger.debug((current_time - start_time) / CONSTANTS.MILLION)

    def process_all_arguments_from_queue(self,
                                         timeout_msecs: Optional[int],
                                         loop_sentinel_ref: Optional[ServerControl]
                                         ) -> None:

        start_time = thread_time_ns()
        current_time = start_time
        #logger.debug(bool(self.graph_arg_queue))
        while process_one_argument_from_queue(
                self.issues,
                self.graph_arg_queue,
                self.order_queue) and \
            not AllsemblyServer.check_should_exit(loop_sentinel_ref) and \
            not AllsemblyServer.check_timeout(
                timeout_msecs,
                int(start_time / CONSTANTS.MILLION),
                int(current_time / CONSTANTS.MILLION)
                                              ):
            #There is an ordering issue here: an argument has orders
            # (bids) associated with it that should be committed into the
            # database as part of the same transaction.  That suggests we
            # should wait to call transaction.commit() until after the orders
            # queue has been processed.
            #In a future version send all requests on a single queue to
            # eliminate order sensitive processing problems like this.
            #For now, process_one_argument_from_queue appends each of its orders
            # associated with its argument to the order queue then immediately
            # calls process_one_order_from_queue.
            #This works without problems because all of the queue processing
            # happens in a single thread.
            transaction.commit()
            current_time = thread_time_ns()

    def process_all_items_from_all_queues(self,
                                         timeout_msecs: Optional[int],
                                         loop_sentinel_ref: Optional[ServerControl]
                                         ) -> None:
        #Order is important.
        # The ArgumentGraph methods push new orders onto
        # the order queue for processing.
        # So, the order queue should be processed after
        # the argument queue.
        # (But currently this is a non-issue because I am
        # calling process_one_order_from_queue from within
        # process_one_argument_from_queue to avoid data
        # integrity problems.)
        # It also makes sense to process creation of
        # new issues before arguments or positions
        # and the creation of new positions before
        # arguments.  In some cases each might
        # be needed by the next.
        # In the future, make these all use one queue.

        self.process_all_issues_from_queue(timeout_msecs,
                                           loop_sentinel_ref)
        self.process_all_positions_from_queue(timeout_msecs,
                                              loop_sentinel_ref)
        self.process_all_arguments_from_queue(timeout_msecs,
                                              loop_sentinel_ref)
        self.process_all_orders_from_queue(timeout_msecs,
                                           loop_sentinel_ref)

    def cleanup(self) -> None:
#        try:
#            self.argdb_conn.close()
#        except ConnectionStateError as e:
#            logging.exception(e)
        transaction.abort()
        self.argdb_conn.close()
        self.argumentdb.close()

    def process_all_items_of_one_request(self,
                          # it might be better to use BinaryIO
                          # since it could be updated in place without needing
                          # to truncate first; the data is the same binary
                          # size each time
                          update_nofication_fileobj: TextIO,  # file-like object
                          server_control: Optional[ServerControl],
                          ) -> int:
        try:
            self.process_all_items_from_all_queues(Config\
                                                   .time_msec_for_one_iter_of_order_processing,
                                                   server_control)
            update_nofication_fileobj.truncate(0)
            update_nofication_fileobj.write(str(time.time()))
        except Exception as e:
            #If there are uncommited transactions
            #  it could be an indication of a bug
            logger.exception(e)
        finally:
            self.cleanup()
        return 0

    def server_main_loop(self,
                         #it might be better to use BinaryIO
                         #since it could be updated in place without needing
                         #to truncate first; the data is the same binary
                         #size each time
                         update_nofication_fileobj: TextIO,#file-like object
                         #caller should maintain a reference
                         server_control: Optional[ServerControl],
                         listen_port: int,
                         #default use case is to listen for connections
                         #from an fcgi script on the same host
                         listen_address: str = "::1", #default is ipv6
                                                      #node-local (loopback)
                         #some OSes implement ipv6 node-local as zero copy
                         #which would make this potentially more efficient
                         #than ipv4, and I believe it has a stronger
                         #guarantee about traffic not leaving the host
                         ipv6: bool = True,
                        ) -> int: #return zero on success
        """ Call this function to start the server.
            Starts an RPyC (Python to Python RPC) service.
            Loops, processing requests, until calling process
              signals it to stop by setting server_control._should_exit.
        """
        if server_control is not None:
            server_control.reset_should_exit() #this could cause a race
                                               #condition but is convenient
                                               #and pretty benign
        event_obj: Event = server_control.get_event_obj() \
                           if server_control is not None \
                           else Event()
        self.order_queue.set_event_object(event_obj)
        self.graph_arg_queue.set_event_object(event_obj)
        self.graph_pos_queue.set_event_object(event_obj)
        self.issue_queue.set_event_object(event_obj)

        #start RPyC threaded server; pass:
        #  order_queue and graph_update_queue (FIFOs)
        #  authenticator that can provide a UserInfo object
        #  on successful authentication
        rpyc_server = rpyc.ThreadPoolServer(classpartial(AllsemblyServices,
                                                       self.order_queue,
                                                       self.graph_arg_queue,
                                                       self.graph_pos_queue,
                                                       self.issue_queue,
                                                       GraphRequest(IssuesDBAccessor(self.argumentdb, read_only=True),
                                                                    self.issues),
                                                       LedgerRequest()
                                                       ),
                                          hostname = listen_address,
                                          ipv6 = ipv6,
                                          port = listen_port,
                                          protocol_config =
                                            {"allow_public_attrs" : True,
                                             "sync_request_timeout": None},
                                          nbThreads =
                                              Config
                                              .number_of_threadpool_threads
                                              )

        rpyc_server_loop_sentinel = ServerControl()

        def rpyc_server_start() -> None:
            while not rpyc_server_loop_sentinel.should_exit():
                try:
                    rpyc_server.start()
                # RPyC servers raise EOFError if the client
                # closes its connection early, but I want
                # the server to continue.
                except EOFError:
                    logger.exception("EOFError from RPyC server")

        try:
            rpyc_thread = threading.Thread(target=rpyc_server_start)
            rpyc_thread.start()

            logger.debug("before main loop")

            #start main loop in main thread
            while not AllsemblyServer.check_should_exit(server_control):
                #logger.debug("starting main loop")
                # wait for an item to be added to any queue
                event_obj.wait()
                event_obj.clear()
                self.process_all_items_from_all_queues(
                    Config.time_msec_for_one_iter_of_graph_updating,
                    server_control)

                #TODO: if anything has changed
                #  add new nodes to the problog_model
                #  start problog in separate thread to update posteriors
                #  wait a little while for problog
                #  if problog hasn't finished
                #    THEN: get cached values
                #  NEXT: update arg diagram
                #  NEXT: set new timestamp in file indicating update is available
                #  (need to get filename in as an argument to this function)
                #  *
                #  *
                #  *Currently all of this updating, except updating of the
                #  file is handled in the ArgumentGraph class by the add_argument(...)
                #  and add_position(...) functions.
                #  *
                #  *Updating the file is not yet necessary because the
                #  graphs are currently single-user, so no users have to
                #  be updated about changes made to the graph by other users.
                update_nofication_fileobj.truncate(0)
                update_nofication_fileobj.write(str(time.time()))

            #end of looping
            rpyc_server_loop_sentinel.set_should_exit()
            rpyc_server.close()
        finally:
            transaction.abort()
            self.cleanup()
    #		rpyc_thread.join()
            #stop any running problog thread
            logger.info("server stopping")
            rpyc_server_loop_sentinel.set_should_exit()
            rpyc_server.close()
        return 0
    #end of server_main_loop(...)


