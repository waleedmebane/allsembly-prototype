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
""" Provides the Allsembly services via RPC.
The AllsemblyServices class is an RPyC (RPC server) which can be
 started to provide the services.
And it needs to be provided with queues onto which to place
 the requests that will be handled elsewhere.
 (See the module "allsembly".)
The caller maintains its own reference to the queues and reads
 off each request to handle it.
Some requests directly get information; These are mediated through
 GraphRequest and LedgerRequest instances and IssuesQueue, which should
 perhaps be renamed to IssuesRequest.  Only GraphRequest and IssuesQueue
 are currently implemented.  A GraphRequest object can provide a drawn
 graph and the full text of a position.  In addition to adding an issue
 to the queue, the IssueQueue can provide the id of the next issue that
 will be used to identify it in the database and for any other requests
 referencing it.
The RPyC server is threaded, so multiple threads might try to access
 information at the same time.  That is the reasond for mediation of
 the requests through thread safe queues and request objects.
"""
import pickle
import logging
import threading
from threading import Event
from logging import Logger
from collections import deque
from typing import Tuple, Optional, cast, Any, Deque, Union, NamedTuple, Dict
from typing_extensions import Final

import rpyc  #type: ignore[import]

from allsembly.argument_graph import Issues, ArgumentGraph, IssuesDBAccessor
from allsembly.config import Config, Limits
from allsembly.speech_act import IndependentBid, Argument, InitialPosition
from allsembly.user import UserInfo

logger: Logger = logging.getLogger(__name__)

#TODO: Use just one queue for posting all requests.  Use a Union type.
# And probably use classes instead of type aliases for each Union member type.

#TODO: In future, don't use the userid to index orders.  Instead, use an
# anonymous identifier that is unique for each user, argument pair.
# Store all of a user's anonymous identifiers in their UserInfo object
# and encrypt that UserInfo object at rest using the user's login password
# with a different hash than the one stored to encrypt the database entry
# encryption key.  That way it can only be
# accessed by the user providing their password.  In case the user's activity
# needs to be de-anonymized, also encrypt a copy of the database entry key
# with the admins' public keys (in addition to encrypting with the user's
# hashed password). The admins should store their private keys
# passphrase-encrypted and elsewhere than on the server.

OrderQueueElement = Tuple[bytes,  # (hashed) userid
                         str,  # subuser
                         IndependentBid
]

_OrderQueue = Deque[OrderQueueElement
]

class OrderQueue:
    """ wraps a deque allowing us to pass an optional Event object to
        notify another thread when items have been added and are,
        therefore, ready for processing."""
    def __init__(self, event_obj: Optional[Event] = None):
        self.queue: _OrderQueue = deque([], Limits.max_queue_items)
        self.event_obj = event_obj

    def __bool__(self) -> bool:
        return True if self.queue else False

    def append(self, item: OrderQueueElement) -> None:
        self.queue.append(item)
        if self.event_obj is not None:
            self.event_obj.set()

    def popleft(self) -> OrderQueueElement:
        return self.queue.popleft()

    def set_event_object(self, event_obj: Event) -> None:
        self.event_obj = event_obj


GraphUpdateArgQueueElement = Tuple[bytes,  # (hashed) userid
                                  str,  # subuser
                                  Tuple[bytes, int],  # issue id
                                  Argument
]

_GraphUpdateArgQueue = Deque[GraphUpdateArgQueueElement
]

class GraphUpdateArgQueue:
    """ wraps a deque allowing us to pass an optional Event object to
        notify another thread when items have been added and are,
        therefore, ready for processing."""
    def __init__(self, event_obj: Optional[Event] = None):
        self.queue: _GraphUpdateArgQueue = deque([], Limits.max_queue_items)
        self.event_obj = event_obj

    def __bool__(self) -> bool:
        return True if self.queue else False

    def append(self, item: GraphUpdateArgQueueElement) -> None:
        self.queue.append(item)
        if self.event_obj is not None:
            self.event_obj.set()

    def popleft(self) -> GraphUpdateArgQueueElement:
        return self.queue.popleft()

    def set_event_object(self, event_obj: Event) -> None:
        self.event_obj = event_obj


GraphUpdatePosQueueElement = Tuple[bytes,  # (hashed) userid
                                  str,  # subuser
                                  Tuple[bytes, int],  # issue id
                                  InitialPosition
]
_GraphUpdatePosQueue = Deque[GraphUpdatePosQueueElement
]

class GraphUpdatePosQueue:
    """ wraps a deque allowing us to pass an optional Event object to
        notify another thread when items have been added and are,
        therefore, ready for processing."""
    def __init__(self, event_obj: Optional[Event] = None):
        self.queue: _GraphUpdatePosQueue = deque([], Limits.max_queue_items)
        self.event_obj = event_obj

    def __bool__(self) -> bool:
        return True if self.queue else False

    def append(self, item: GraphUpdatePosQueueElement) -> None:
        self.queue.append(item)
        if self.event_obj is not None:
            self.event_obj.set()

    def popleft(self) -> GraphUpdatePosQueueElement:
        return self.queue.popleft()

    def set_event_object(self, event_obj: Event) -> None:
        self.event_obj = event_obj


class IssueDeleteDirective:
    def __init__(self, issue_id: Tuple[bytes, int]) -> None:
        self.id_to_delete = issue_id


# tuple contains the issue id and the issue name
IssueAddDirective = Tuple[int, str]
IssueUpdateQueue = Deque[Union[IssueAddDirective, IssueDeleteDirective]]


class IssueQueue:
    def __init__(self, issues: 'Issues', event_obj: Optional[Event] = None):
        self.issues = issues
        self.queue: IssueUpdateQueue = deque([], Limits.max_queue_items)
        self.event_obj = event_obj

    def add_issue(self, issue_name: str) -> Optional[int]:
        """ return new issue number """
        #commented out code is to set the issue number atomically
        # since it could possibly be set as well from a different thread.
        # I will reinstate that code in a future version.  I had a problem
        # with using AtomicLong with Persistent that I believe is fixed,
        # now, but I need change other places in the code and test.
        if Limits.max_total_issues >= self.issues.next_issue_id:  # .value:
            #			issue_id = self.issues.next_issue_id.get_and_set(
            #										 self.issues.next_issue_id.value + 1
            #										 )
            # Actually enqueuing the new issue is unnecessary in this version
            # since only one issue is used in the client and its name is
            # not shown anywhere.  However, it might work.  It will have to
            # be tested.
            # If an issue doesn't exist, it is created in
            # allsembly.process_one_position_from_queue() as long as its
            # id number is less than next_issue_id.
            #			self.queue.append((issue_id, issue_name))
            issue_id = self.issues.next_issue_id
            self.issues.next_issue_id += 1
            return issue_id
        else:
            return None

    def delete_issue(self, issue_id: Tuple[bytes, int]) -> None:
        self.queue.append(IssueDeleteDirective(issue_id))
        if self.event_obj is not None:
            self.event_obj.set()

    def set_event_object(self, event_obj: Event) -> None:
        self.event_obj = event_obj


class GraphRequest:
    """ Provides a thread-safe way to get data from the argument
        graph.
        In particular, use this to draw the SVG representation
        of the graph or get the pre-drawn SVG.
    """
    # This seems no longer really to be needed since the read-lock
    # is taken out in the ArgumentGraph class instance itself and not here
    def __init__(self,
                 issues_from_db: IssuesDBAccessor,
                 issues_obj_not_safe_to_write: Issues) -> None:
        self._issues_accessor: Final[IssuesDBAccessor] = issues_from_db
        self._issues_not_safe_to_write: Final[Issues] = issues_obj_not_safe_to_write

    def draw(self, issue: Tuple[bytes, int]) -> str:
        # Each thread needs its own context (provided by its own IssuesAccessor copy).
        #issues_accessor = copy.copy(self._issues_accessor)
        with self._issues_accessor.get_context() as issues:
            if issues.graphs.has_key(issue):
                graph_ref: Final[ArgumentGraph] = issues.graphs[issue]
                return graph_ref.get_drawn_graph()
        return ""

    def get_next_graph(self,
                       issue: Tuple[bytes, int],
                       last_received_graph_revision_number: int) -> Union[int, None]:
        if self._issues_not_safe_to_write.graphs.has_key(issue):
            graph_ref: Final[ArgumentGraph] = self._issues_not_safe_to_write.graphs[issue]
            if last_received_graph_revision_number >= graph_ref.get_revision_number():
                graph_ref.get_update_graph_event_obj().wait()
            return graph_ref.get_revision_number()
        return None

    def get_position_details(self, issue: Tuple[bytes, int],
                             pos_id: int) -> str:
        # Each thread needs its own context (provided by its own IssuesAccessor copy).
        #issues_accessor = copy.copy(self._issues_accessor)
        with self._issues_accessor.get_context() as issues:
            if issues.graphs.has_key(issue):
                graph_ref: Final[ArgumentGraph] = issues.graphs[issue]
                position: Final = graph_ref.get_position_copy(pos_id)
                return position.statement
        return ""

class LedgerRequest:
    """ Provides a thread-safe way to get ledger data from the
        betting exchange.
        The ledger contains all previous bets and bids.
        Use this to get a user's commitment store (bets and bids).
        Gets a read lock on the ledger data.
    """
    pass


latest_thread_for_user: Final[Dict[bytes, int]] = {}

class AuthCredentialsStr(NamedTuple):
    userid: str
    password: str


class AuthCredentials(NamedTuple):
    userid: bytes
    password: bytes

    @classmethod
    def build_from_str(cls, credentials_str: AuthCredentialsStr
                       ) -> 'AuthCredentials':
        return AuthCredentials(credentials_str.userid.encode('utf-8'),
                               credentials_str.password.encode('utf-8'))

class UserInfoAndCookie(NamedTuple):
    user_settings: UserInfo
    encrypted_cookie: bytes


class AllsemblyServices(rpyc.Service):
    """ Provides a user with the services through
        remote procedure calls (RPC)
    """
    #	Every remotely callable method requires
    #    a userid and a password in this version.
    #    A future version could take advantage of
    #    the Authenticator feature of RPyC to
    #    just do authentication once when the
    #    connection is established.  It doesn't
    #    make much of a difference, for now, since
    #    this implements a web service (which is
    #    stateless).

    class NotAuthenticated(Exception):
        pass

    class UserServices:
        """ Provide services requiring user authentication.
        An instance can only be created by providing authentic
        credentials.  Otherwise, the exception
        "AllsemblyServices.NotAuthenticated" is raised.
        """
        def __init__(self,
                     services: 'AllsemblyServices',
                     userid: bytes
                     # credentials: Union[AuthCredentialsStr, bytes]
                    ) -> None:
            self._services: Final = services
            #user_or_none = self._services.user_auth.authenticate_user(credentials)
            #if user_or_none is not None:
            #    self._userid_hashed = user_or_none.user_settings.userid_hashed
            #else:
            #    raise AllsemblyServices.NotAuthenticated

            self._userid_hashed = userid


        def check_commitments_for_consistency(
        self
        ) -> bool:
            #stub
            return True

        def delete_issue(self,
                                 issue: int
                                 #subuser: str,
                                 ) -> None:
            """ attempt to delete a presumably existing issue.
            No feedback given regarding failure or success.
            This function just puts the request on the queue.
            """
            self._services.issue_queue.delete_issue((self._userid_hashed, issue))

        def argue(self,
                          issue: int,
                          subuser: str,
                          argument: bytes  # ArgueSpeechAct
                          ) -> bool:
            """Always returns True.
            Just puts the request on the queue.
            """
            issue #mentioning variable so it isn't considered unused
                  #but it is not used currently; it is here for later
            # in this version users will be in their own sandbox
            # and will have only one issue, not shared with others
            my_argument = pickle.loads(argument)
            logger.debug(my_argument.argument.pro_or_con)
            self._services.graph_arg_queue.append((self._userid_hashed,
                                         subuser,
                                         (self._userid_hashed, 0),  # ignore issue number
                                         my_argument.argument)
                                        )
            return True


        def propose(self,
                            issue: int,
                            subuser: str,
                            proposal: bytes  # ProposeSpeechAct
                            ) -> bool:
            """Always returns True.
            Just puts the request on the queue.
            """
            issue  # mentioning variable so it isn't considered unused
                   # but it is not used currently; it is here for later
            self._services.graph_pos_queue.append((self._userid_hashed,
                                             subuser,
                                             (self._userid_hashed, 0),  # issue,
                                             pickle.loads(proposal).position)
                                            )
            return True


        #	def expose_bid(self, userid, password, position: ExistingPosition, bid: IndependentBid)
        #		self.user_ref = user_auth.authenticate_user(userid, password)

        #	def expose_ask(self, userid, password, position: ExistingPosition, ask: Ask)
        #		self.user_ref = user_auth.authenticate_user(userid, password)

        def get_arg_graph(self,
                                  issue: int,
                                  #subuser: str
                                  ) -> str:
            """Returns the argument graph as a string.
            Currently that is a Graphviz produced graph in SVG format.
            See ArgumentGraph.draw_graph(...) in the argument_graph
            module, called via GraphRequest.
            """
            return self._services.graph_req.draw((self._userid_hashed, issue))

        def get_next_arg_graph(self,
                               issue: int,
                               # user: str,
                               last_graph_revision_number: int) -> Union[Tuple[str, int], None]:
            my_thread_id: Final[int] = threading.get_ident()
            latest_thread_for_user[self._userid_hashed] = my_thread_id
            available_graph: Final[Union[int, None]] = self._services.graph_req.get_next_graph(
                (self._userid_hashed, issue),
                last_graph_revision_number
            )
            if available_graph is not None:
                if latest_thread_for_user[self._userid_hashed] == my_thread_id:
                    return (
                        self.get_arg_graph(issue),
                        available_graph
                    )
            return None


        def get_position_details(self,
                                         issue: int,
                                         pos_id: int
                                         ) -> str:
            """ Returns the full text of a position.
            """
            return self._services.graph_req.get_position_details(
                (self._userid_hashed, issue),
                pos_id
            )

    # NOT IMPLEMENTED YET
    #	def exposed_get_commitments(self, userid, password, issue, subuser):
    #		user_or_none = user_auth.authenticate_user(userid, password)
    #		if user_or_none is not None:
    #			user_or_none.last_login = time.time()
    #			user_or_none.current_issue = issue
    #			user_or_none.current_subuser = subuser
    #			transaction.commit()
    #			return ledger_ref.get_items(issue,
    #			                            user_or_none.userid_hashed,
    #			                            subuser
    #			                            )

    def __init__(self,
                 order_queue: OrderQueue,
                 graph_arg_queue: GraphUpdateArgQueue,
                 graph_pos_queue: GraphUpdatePosQueue,
                 issue_queue: IssueQueue,
                 graph_req: GraphRequest,
                 ledger_req: LedgerRequest):
        self.order_queue = order_queue
        self.graph_arg_queue = graph_arg_queue
        self.graph_pos_queue = graph_pos_queue
        self.graph_req = graph_req
        self.ledger_req = ledger_req
        self.issue_queue = issue_queue

    def on_connect(self, conn: Any) -> None:
        #RPyC boilerplate
        pass

    def on_disconnect(self, conn: Any) -> None:
        #RPyC boilerplate
        pass


    def exposed_get_user_services(self,
                                  userid: bytes
                                  # credentials: Union[AuthCredentialsStr, bytes]
                                  ) -> 'AllsemblyServices.UserServices':
        return AllsemblyServices.UserServices(self, userid)

    def _add_issue(self,
                   issue_name: str) -> Optional[int]:
        """ creates a new issue, allocating an arg graph for it
            and returns its issue number.
        """
        return self.issue_queue.add_issue(issue_name)