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

import pickle

import transaction
import ZODB, ZODB.FileStorage
import os
import tempfile
from collections import deque

from allsembly.allsembly import OrderQueue, GraphUpdateArgQueue, GraphUpdatePosQueue, process_one_position_from_queue
from allsembly.betting_exchange import BettingExchange
from allsembly.argument_graph import Issues, IssuesDBAccessor
from allsembly.rpyc_server import IssueQueue, GraphRequest, LedgerRequest, \
    AllsemblyServices
from allsembly.speech_act import ProposeSpeechAct, InitialPosition, Bid, Premise


def test_allsembly():
    with tempfile.TemporaryDirectory() as tmpdirname:
        print("Temporary directory name: " + tmpdirname)
        argumentdb_storage = ZODB.FileStorage.FileStorage(os.path.join(tmpdirname, "allsembly_test_argdb"))
        argumentdb = ZODB.DB(argumentdb_storage)
        argdb_conn = argumentdb.open()
        order_queue: OrderQueue = deque()
        graph_arg_queue: GraphUpdateArgQueue = deque()
        graph_pos_queue: GraphUpdatePosQueue = deque()

        #test setting up the databases with
        #the pre-defined structures
        dbroot = argdb_conn.root()
        #issues: Dict[str, (BettingExchange, ArgumentGraph)]
        assert not hasattr(dbroot, "issues")
        if not hasattr(dbroot, "issues"):
            dbroot.issues = Issues()
            assert hasattr(dbroot, "issues")
        assert not hasattr(dbroot, "betxch")
        if not hasattr(dbroot, "betxch"):
            dbroot.betxch = BettingExchange()
            assert hasattr(dbroot, "betxch")
        issues = dbroot.issues
        betting_exchange = dbroot.betxch
        issue_queue = IssueQueue(issues)

        server = AllsemblyServices(order_queue, graph_arg_queue, graph_pos_queue, issue_queue,
                                   GraphRequest(IssuesDBAccessor(argumentdb, read_only=True)), LedgerRequest())
        userid = "testuser"

        assert not issue_queue.queue #nothing on the queue
        #assert server.exposed_add_issue(username, password, "my_issue") == 0
        #assert issue_queue.queue
        #assert not allsembly.process_one_issue_from_queue(issues, issue_queue)
        #assert not issue_queue.queue

        #add an initial prosition to the graph from the services API
        #the result should be an item on the graph_pos_queue
        #which will be processed later
        #(in the actual allsembly program it will be processed
        # in another thread).
        assert not graph_pos_queue #nothing on the queue
        my_user_services = server.exposed_get_user_services(bytes(userid, 'utf-8'))
        assert my_user_services is not None
        assert my_user_services.propose(0, "",
                                        pickle.dumps(ProposeSpeechAct(
                                                         InitialPosition("my proposal")
                                        )
                                    )
                                )
                       
        assert graph_pos_queue #something on the queue, now
        current_update = graph_pos_queue[0]
        print(current_update)
        updating_user_userid = current_update[0]
        update_issue = current_update[2]
        new_pos = current_update[3]
        #mimic what the allsembly program does, but for just one iteration
        assert not process_one_position_from_queue(issues, graph_pos_queue)
        assert not graph_pos_queue
        assert issues.graphs.has_key(update_issue)
        print(issues.graphs[update_issue].pos_node_index.values())
        print(issues.graphs[update_issue].get_position_copy(0))

        #caller is responsible for committing the transation
        #in this case, so don't need to test that here
        #transaction.abort()
        transaction.commit()
        transaction.abort()
        assert issues.graphs.has_key(update_issue)
        print(issues.graphs[update_issue].pos_node_index.values())
        print(issues.graphs[update_issue].get_position_copy(0))
        print(my_user_services.get_arg_graph(0))
        print(os.listdir(tmpdirname))

