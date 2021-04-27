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

from argon2 import PasswordHasher

import multiprocessing as mp
import rpyc
import io
import signal
import time

from typing_extensions import Final

from allsembly.CONSTANTS import UserPasswordType
from allsembly.allsembly import ServerControl, AllsemblyServer
from allsembly.config import Config
from allsembly.rpyc_server import AuthCredentialsStr
from allsembly.speech_act import ProposeSpeechAct, InitialPosition, Premise, Bid
from allsembly.user import add_user

SERVER_PORT_NUMBER: Final[int] = 10888

def start_service():
    print("start_service function called")
    server_control = ServerControl()

    def handle_sigterm(signum, stackframe):
        #pdb.set_trace()
        if signal.SIGTERM == signum:
            server_control.set_should_exit()

    def handle_sigalrm(signum, stackframe):
        #pdb.set_trace()
        if signal.SIGALRM == signum:
            server_control.set_should_exit()
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.alarm(10) #cause the server to exit after 10 seconds -- should be enough time

    with tempfile.TemporaryDirectory() as tmpdirname:
        #first we need to add a user
        userid = "testuser"
        password = "test123"
        authdb_filename = os.path.join(tmpdirname, "allsembly_test_authdb")
        authdb_storage = ZODB.FileStorage.FileStorage(authdb_filename)
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

        userdb_filename = os.path.join(tmpdirname, "allsembly_test_userdb")
        argdb_filename = os.path.join(tmpdirname, "allsembly_test_argdb")
        notification_textio = io.StringIO("test")
        print("starting server")
        AllsemblyServer(authdb_filename,
                       userdb_filename,
                       argdb_filename).server_main_loop(
                       notification_textio,
                       server_control,
                       SERVER_PORT_NUMBER
                          )
        #server has exited
        print("server has exited")
        print(os.listdir(tmpdirname))
        print(notification_textio.getvalue())
        notification_textio.close()

def test_server():
    #pdb.set_trace()
    #start server in another process
    p = mp.Process(target=start_service)
    p.start()
    #wait a little while for the server to be ready
    time.sleep(2)
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True}, ipv6=True)
    #print(client.root.add_issue("testuser", "test123", "my issue"))
    my_propose_speech_act = ProposeSpeechAct(
                         InitialPosition("conclusion", [(Premise("premise", Bid(50,50,10)
                                                                ), None
                                                        )]
                                        )	
                           )

    def _():
        my_user_services = client.root.get_user_services_noexcept(AuthCredentialsStr(
            userid="testuser",
            password="test123"
        ))
        assert my_user_services is not None
        print(my_user_services.propose(0, "subuser1", pickle.dumps(my_propose_speech_act)))

    _()
    print(client.root.get_user_services(AuthCredentialsStr(
            userid="testuser",
            password="test123"
        )).get_arg_graph(0))
    p.terminate()
    p.join()
