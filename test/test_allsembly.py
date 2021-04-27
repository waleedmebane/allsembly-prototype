# Copyright © 2021 Waleed H. Mebane
#
#   This file is part of Allsembly™ Prototype.
#
#   Allsembly™ Prototype is free software: you can redistribute it and/or
#   modify it under the terms of the Lesser GNU General Public License,
#   version 3, as published by the Free Software Foundation and the
#   additional terms directly below this notice.
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
#   Additional terms:
#
#   Without his or her specific prior written permission, neither may the names
#   of any author of or contributor to this software be used to endorse products
#   derived from this software nor may his or her names, image, or likeness be
#   used to promote products derived from this software.
#
#   Nothing in this license shall be interpreted as granting any license to
#   any of the trademarks of any of the authors of or contributors to this
#   software.
#

import pickle

import transaction
import ZODB, ZODB.FileStorage
import hashlib
import os
import tempfile
from collections import deque

from argon2 import PasswordHasher

from allsembly.CONSTANTS import UserPasswordType
from allsembly.allsembly import OrderQueue, GraphUpdateArgQueue, GraphUpdatePosQueue, process_one_position_from_queue
from allsembly.betting_exchange import BettingExchange
from allsembly.argument_graph import Issues
from allsembly.rpyc_server import IssueQueue, _UserAuthenticator, GraphRequest, LedgerRequest, \
    AllsemblyServices, AuthCredentialsStr
from allsembly.speech_act import ProposeSpeechAct, InitialPosition, Bid, Premise
from allsembly.user import add_user
from allsembly.config import Config


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

        #instance of a class that defers opening its databases until
                #they are needed to authenticate a user
                #this is done so that the database will get a thread local
                #transaction manager
        user_authenticator = _UserAuthenticator(
                                                    os.path.join(tmpdirname, "allsembly_test_authdb"),
                                                    os.path.join(tmpdirname, "allsembly_test_userdb"),
                                                   )
        server = AllsemblyServices(
                                                   order_queue,
                                                   graph_arg_queue,
                                                   graph_pos_queue,
                                                       issue_queue,
                                                   GraphRequest(issues),
                                                   LedgerRequest(),
                                                       user_authenticator
                        )
        #test adding a user
        userid = "testuser"
        password = "test123"
        authdb_storage = ZODB.FileStorage.FileStorage(os.path.join(tmpdirname, "allsembly_test_authdb"))
        authdb = ZODB.DB(authdb_storage)
        authdb_conn = authdb.open()

        add_user(userid, password, authdb_conn)
        #test that transaction was committed;
        #otherwise, this will cause changed to get rolled back
        transaction.abort()
        authdb_root = authdb_conn.root()
        assert hasattr(authdb_root, "userid_salt")
        print(authdb_root.userid_salt)
        assert hasattr(authdb_root, "passwords")
        userid_scrypt = bytes(userid, 'utf-8')
        assert authdb_root.passwords.has_key(userid_scrypt)
        print(authdb_root.passwords[userid_scrypt])
        if Config.user_password_type == UserPasswordType.pbkdf2_hmac_sha512:
            password_salt = authdb_root.passwords[userid_scrypt].pwd_salt
            password_scrypt = hashlib.pbkdf2_hmac('sha512',
                                              bytes(password, 'utf-8'),
                                              password_salt,
                                              200000)
            assert authdb_root.passwords[userid_scrypt].password_hashed == password_scrypt
        elif Config.user_password_type == UserPasswordType.argon2id:
            assert PasswordHasher().\
                verify(authdb_root.passwords[userid_scrypt].password_hashed,
                       password)
        #connections need to be closed here so that the
        #auth database can be used by the AllsemblyServices instance (server)
        #to authenticate the user (i.e., check whether the userid exists
        #in the database with the hashed password
        #only one non-read-only connection can be open to the database
        #at a time
        authdb_conn.close()
        authdb.close()
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
        my_user_services = server.exposed_get_user_services_noexcept(AuthCredentialsStr(
            userid=userid,
            password=password
        ))
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

