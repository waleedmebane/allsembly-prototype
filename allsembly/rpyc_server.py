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
""" Provides the Allsembly services via RPC.
The AllsemblyServices class is an RPyC (RPC server) which can be
 started to provide the services.
It needs to be provided with an _UserAutheticator object that
 enables it to authenticate a user from the credentials stored
 in a database.
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
import copy
import time
import logging
from logging import Logger
from collections import deque
from typing import Tuple, Optional, cast, Any, Deque, Union, NamedTuple
from typing_extensions import Final

import ZODB  #type: ignore[import]
from ZODB.FileStorage import FileStorage #type: ignore[import]
from ZODB.Connection import Connection #type: ignore[import]
from ZODB.POSException import ConflictError #type: ignore[import]
import rpyc  #type: ignore[import]
import transaction  #type: ignore[import]
from BTrees.OOBTree import OOBTree #type: ignore [import]
from cryptography.fernet import Fernet

from allsembly.argument_graph import Issues, ArgumentGraph
from allsembly.common import FinalVar
from allsembly.config import Config, Limits
from allsembly.speech_act import IndependentBid, Argument, InitialPosition
from allsembly.user import UserInfo
from allsembly.config import Config
from allsembly.CONSTANTS import UserPasswordType

logger: Logger = logging.getLogger(__name__)

if UserPasswordType.pbkdf2_hmac_sha512 == Config.user_password_type:
    import hashlib
elif UserPasswordType.argon2id == Config.user_password_type:
    from argon2 import PasswordHasher #type: ignore[import]
    from argon2.exceptions import VerificationError #type: ignore[import]
    from argon2.exceptions import VerifyMismatchError, InvalidHash

# some type aliases
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
# From my investigation, the SQLCipher library seems to be a good
# DBMS for the task since it can encrypt an entire database including
# the database's metadata.  E.g., put only a table containing all of
# the anonymous identifies for one user in each database, encrypt it
# and store the encryption key and the name of the file in an encrypted
# field of the UserAuth object in the separate authentication database
# (the same database as used now for storing authentication information).
OrderQueue = Deque[Tuple[bytes,  # (hashed) userid
                         str,  # subuser
                         IndependentBid
]
]

GraphUpdateArgQueue = Deque[Tuple[bytes,  # (hashed) userid
                                  str,  # subuser
                                  Tuple[bytes, int],  # issue id
                                  Argument
]
]

GraphUpdatePosQueue = Deque[Tuple[bytes,  # (hashed) userid
                                  str,  # subuser
                                  Tuple[bytes, int],  # issue id
                                  InitialPosition
]
]

class IssueDeleteDirective:
    def __init__(self, issue_id: Tuple[bytes, int]) -> None:
        self.id_to_delete = issue_id


# tuple contains the issue id and the issue name
IssueAddDirective = Tuple[int, str]
IssueUpdateQueue = Deque[Union[IssueAddDirective, IssueDeleteDirective]]


class IssueQueue:
    def __init__(self, issues: 'Issues'):
        self.issues = issues
        self.queue: IssueUpdateQueue = deque([], Limits.max_queue_items)

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



class GraphRequest:
    """ Provides a thread-safe way to get data from the argument
        graph.
        In particular, use this to draw the SVG representation
        of the graph or get the pre-drawn SVG.
    """
    # This seems no longer really to be needed since the read-lock
    # is taken out in the ArgumentGraph class instance itself and not here
    def __init__(self, issues: Issues) -> None:
        self.issues: Final[Issues] = issues #read-only

    def draw(self, issue: Tuple[bytes, int]) -> str:
        if self.issues.graphs.has_key(issue):
            issue_ref: Final[ArgumentGraph] = self.issues.graphs[issue]
            #with issue_ref.arg_graph._v_my_rwlock.gen_rlock():
            return issue_ref.draw_graph()
        return ""

    def get_position_details(self, issue: Tuple[bytes, int],
                             pos_id: int) -> str:
        if self.issues.graphs.has_key(issue):
            issue_ref: Final[ArgumentGraph] = self.issues.graphs[issue]
            position: Final = issue_ref.get_position_copy(pos_id)
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

class _UserAuthenticator:
    """ User authentication takes place in a different thread
    per connection (because the RPyC service uses threads).
    This class is initialized with all of the information needed to
    open and connect to the database, but defers those actions
    until it is used in the appropriate thread.  This is so that
    each thread gets its own database connection.
    Method "authenticate_user" opens and connects to a database
    if necessary and then tries to authenticate the user.
    This class is not the same as an RPyC "authenticator".
    """
    authdb_storage: ZODB.FileStorage.FileStorage
    userdb_storage: ZODB.FileStorage.FileStorage
    authdb: ZODB.DB
    userdb: ZODB.DB
    authdb_conn: ZODB.Connection.Connection
    userdb_conn: ZODB.Connection.Connection
    # As far as I can tell, the class name of a ZODB root node
    # is not documented in its API documentation so could change
    # authdb_root: Any
    # userdb_root: Any
    userid_salt: bytes

    def __init__(self, userauth_dbfilename: str,
                 user_dbfilename: str) -> None:
        self.userauth_dbfilename = userauth_dbfilename
        self.user_dbfilename = user_dbfilename

        #Instance initialization takes place in a single-thread
        #context, so we are free to write to the database here,
        #but we have to close it afterward since we want to
        #later use a different, read-only, database object.
        authdb_storage = ZODB.FileStorage.FileStorage(
                self.userauth_dbfilename, read_only=False)
        authdb = ZODB.DB(authdb_storage)
        authdb_conn = authdb.open()
        authdb_root = authdb_conn.root()
        if not hasattr(authdb_root, "cookie_encryption_key"):
            authdb_root.cookie_encryption_key = Fernet.generate_key()
        transaction.commit()
        authdb_conn.close()
        authdb.close()

    def authenticate_user(self,
                          credentials: Union[AuthCredentialsStr, bytes]
                          ) -> Optional[UserInfoAndCookie]:
        """ If the userid is in the auth database
        and the password is correct, then return
        that user's UserInfo object from the
        users database together with an encrypted version
        of the userid and password that can be used to set
        a cookie;
        Otherwise, return "None".
        """
        if not hasattr(self, "authdb_storage"):
            self.authdb_storage = ZODB.FileStorage.FileStorage(
                self.userauth_dbfilename, read_only=True)
        if not hasattr(self, "authdb"):
            self.authdb = ZODB.DB(self.authdb_storage)
        if not hasattr(self, "authdb_conn"):
            self.authdb_conn = self.authdb.open()
        if not hasattr(self, "authdb_root"):
            self.authdb_root = self.authdb_conn.root()
            if not hasattr(self.authdb_root, "passwords"):
                self.authdb_root.passwords = OOBTree()
        if not hasattr(self, "_fernet_cryptor"):
            if hasattr(self.authdb_root, "cookie_encryption_key"):
                self._fernet_cryptor = Fernet(
                    self.authdb_root.cookie_encryption_key)
            else:
                logger.error("No cookie encryption key!")

        #Need a separate database connection per thread
        #so don't use instance ("self") variables
        #Instance variables are fine for the auth db because
        #it is being used read-only.
        userdb_storage = ZODB.FileStorage.FileStorage(
            self.user_dbfilename)
        userdb: Final = ZODB.DB(userdb_storage)
        userdb_conn: Final = userdb.open()
        userdb_root: Final = userdb_conn.root()
        decrypted_credentials: Optional[FinalVar[AuthCredentials]] = None
        if isinstance(credentials, bytes):
            # encryption object needed to encrypt data with the
            # encryption key that was previously stored when
            # creating the auth database (see __init__)
            if not hasattr(self, "_fernet_cryptor"):
                return None
            decrypted_credentials = FinalVar[AuthCredentials](pickle.loads(
                self._fernet_cryptor.decrypt(credentials)))
            userid_hashed = FinalVar[bytes](decrypted_credentials.get().userid)
        else:
            if not hasattr(self, "userid_salt"):
                # no salt means there are no users
                if not hasattr(self.authdb_root, "userid_salt"):
                    # self.authdb_root.userid_salt = os.urandom(16)
                    return None
                self.userid_salt = self.authdb_root.userid_salt
            #		userid_hashed = hashlib.scrypt(bytes(userid, 'utf-8'),
            #						  salt=self.userid_salt,
            #						  n=16384,
            #						  r = 8,
            #						  p = 1)
            # store userid as plaintext for now
            userid_hashed = FinalVar[bytes](credentials.userid.encode('utf-8'))

        if self.authdb_root.passwords.has_key(userid_hashed.get()):
            pwd_record = self.authdb_root.passwords[userid_hashed.get()]
            #			if hashlib.scrypt(bytes(pwd, 'utf-8'),
            #						  salt=pwd_record.salt,
            #						  n=16384,
            #						  r = 8,
            #						  p = 1) == pwd_record.password:
            # using pbkdf2 instead of scrypt for now, to avoid requiring
            # OpenSSL version 1.1.1
            #TODO: store the password hash type and hash parameters in the database
            # in case they change.  (The parameters are probably embedded in the
            # digest--i.e. included in the hashed password string.)
            try:
                #TODO: refactor this if statement into a separate function
                # without so many boolean connectives
                if (isinstance(credentials, bytes) and
                     decrypted_credentials is not None and
                     decrypted_credentials.get().password ==
                     pwd_record.password_hashed
                   ) or \
                   (isinstance(credentials, AuthCredentialsStr) and
                    (
                     (UserPasswordType.pbkdf2_hmac_sha512 == Config.user_password_type and
                       hashlib.pbkdf2_hmac('sha512',
                                   bytes(credentials.password, 'utf-8'),
                                   pwd_record.pwd_salt,
                                   Config.pbkdf2_hash_iterations
                                   ) == pwd_record.password_hashed
                     ) or
                     (UserPasswordType.argon2id == Config.user_password_type and
                       PasswordHasher().verify(pwd_record.password_hashed,
                                               credentials.password)
                     )
                    )
                ):
                    #TODO: put a creation time in the cookie to expire a
                    # cookie (e.g., if its creation time is earlier than
                    # the last login time or the last logout time once
                    # logouts are implemented) to avoid replay attacks
                    # (i.e., so that an attacker who gets hold of the
                    # cookie may not use it after it expires or after the
                    # user logs out.  But this also means a user could not
                    # have multiple sessions active on different devices;
                    # alternatively, store active session tokens in the
                    # cookies and in the database, with expiration times.
                    if isinstance(credentials, AuthCredentialsStr):
                        encrypted_credentials = FinalVar[bytes](
                            self._fernet_cryptor.encrypt(
                                pickle.dumps(
                                    AuthCredentials(
                                        userid=pwd_record.userid_hashed,
                                        password=pwd_record.password_hashed
                                    )
                                )
                            )
                        )
                    else:
                        encrypted_credentials = FinalVar[bytes](credentials)

                    #writing into the database is not thread safe, so for
                    #now just return a per thread UserInfo object
                    #TODO: fix, maybe using Python's context manager and returning
                    # a separate per thread object containing an open UserInfo
                    # DB connection, that will close after being used.
                    # Code below tries one time to update UserInfo, otherwise
                    # aborts the transaction, leaving the UserInfo object as is.
                    # This would happen when some other thread is trying to update it
                    # and got started first.
                    #@transaction.manager.run(1) #type: ignore[misc]
                    #def _get_corresponding_user_settings() -> UserInfo:
                    if not hasattr(userdb_root, "users"):
                        userdb_root.users = OOBTree()
                    if not userdb_root.users.has_key(userid_hashed.get()):
                        userdb_root.users[userid_hashed.get()] = UserInfo()
                    user_ref: Final = cast(UserInfo, userdb_root.users[userid_hashed.get()])
                    #user_ref.userid_hashed = userid_hashed
                    if not user_ref.userid_hashed or \
                            user_ref.userid_hashed == b'':
                        user_ref.userid_hashed = userid_hashed.get()
                    user_ref.last_login = int(time.time())
                    #return copy.deepcopy(user_ref)
                    try:
                        transaction.commit()
                        user_settings = FinalVar[UserInfo](copy.deepcopy(user_ref))
                        userdb_conn.close()
                        userdb.close()
                        return UserInfoAndCookie(
                            user_settings=user_settings.get(),
                            encrypted_cookie=encrypted_credentials.get()
                        )
                    except ConflictError:
                        transaction.abort()
                        user_settings = FinalVar[UserInfo](UserInfo())
                        userdb_conn.close()
                        userdb.close()
                        return UserInfoAndCookie(
                            user_settings=user_settings.get(),
                            encrypted_cookie=encrypted_credentials.get()
                        )
                    #user_settings: Final = cast(UserInfo, _user_settings)
    #                userdb_conn.close()
    #                userdb.close()
    #                return user_settings
            except VerifyMismatchError:
                pass
            except (InvalidHash, VerificationError) as e:
                #this probably means you've tried to change hash functions,
                #but the hashed password in the database is still
                #using the old hash type.
                logger.exception(e)
        userdb_conn.close()
        userdb.close()
        return None


    def close_databases(self) -> None:
        if hasattr(self, "authdb_conn"):
            transaction.abort()
            self.authdb_conn.close()
        if hasattr(self, "authdb"):
            self.authdb.close()


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
                     credentials: Union[AuthCredentialsStr, bytes]) -> None:
            self._services: Final = services
            user_or_none = self._services.user_auth.authenticate_user(credentials)
            if user_or_none is not None:
                self._userid_hashed = user_or_none.user_settings.userid_hashed
            else:
                raise AllsemblyServices.NotAuthenticated

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
                 ledger_req: LedgerRequest,
                 user_auth: _UserAuthenticator):
        self.order_queue = order_queue
        self.graph_arg_queue = graph_arg_queue
        self.graph_pos_queue = graph_pos_queue
        self.user_auth = user_auth
        self.graph_req = graph_req
        self.ledger_req = ledger_req
        self.issue_queue = issue_queue

    def on_connect(self, conn: Any) -> None:
        #RPyC boilerplate
        pass

    def on_disconnect(self, conn: Any) -> None:
        #RPyC boilerplate
        pass

    def exposed_get_user_services_noexcept(self,
                                  credentials: Union[AuthCredentialsStr, bytes]
                                  ) -> Optional['AllsemblyServices.UserServices']:
        """If authentication with the provided credentials is successful,
        Returns a class instance that provides the services that require
        authentication.
        Otherwise, returns None.
        """
        try:
            my_userv = AllsemblyServices.UserServices(self, credentials)
            return my_userv
        except AllsemblyServices.NotAuthenticated:
            return None

    def exposed_get_user_services(self,
                                  credentials: Union[AuthCredentialsStr, bytes]
                                  ) -> 'AllsemblyServices.UserServices':
        """If authentication with the provided credentials is successful,
        Returns a class instance that provides the services that require
        authentication.
        Otherwise, UserServices will raise an exception,
        "AllsemblyServices.NotAuthenticated" that should be handled by
        the caller.
        """
        return AllsemblyServices.UserServices(self, credentials)

    def exposed_authenticate_user(self,
                                  credentials: Union[AuthCredentialsStr, bytes]
                                  ) -> Optional[bytes]:
        """Returns encrypted cookie if userid exists in the database
           and password matches; None, otherwise
        """
        user_or_none: Final = self.user_auth.authenticate_user(credentials)
        if user_or_none is not None:
            user_or_none.user_settings.last_login = int(time.time())
            transaction.commit()
            return user_or_none.encrypted_cookie
        return None

    def _add_issue(self,
                   issue_name: str) -> Optional[int]:
        """ creates a new issue, allocating an arg graph for it
            and returns its issue number.
        """
        return self.issue_queue.add_issue(issue_name)