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
""" Classes containing user data and authentication data and
a function, "add_user(...)", for adding a user to the authentication
database.
"""
import os
import ZODB  #type: ignore[import]
import persistent  #type: ignore[import]
import transaction  #type: ignore[import]
from BTrees.OOBTree import OOBTree #type: ignore[import]
from persistent.mapping import PersistentMapping  #type: ignore[import]
from typing import List

from allsembly.config import Config
from allsembly.CONSTANTS import UserPasswordType

if UserPasswordType.pbkdf2_hmac_sha512 == Config.user_password_type:
    import hashlib
elif UserPasswordType.argon2id == Config.user_password_type:
    from argon2 import PasswordHasher #type: ignore[import]

class UserAuth(persistent.Persistent):
    """ User's stored authentication credentials
    """
    def __init__(self,
                 userid: bytes,
                 pwd: bytes,
                 pwd_salt: bytes):
        self.userid_hashed = userid
        self.password_hashed = pwd
        self.pwd_salt = pwd_salt

class UserClientSettings(persistent.Persistent):
    """ Future place for storing a user's web client
    settings.
    """
    #example of what could be stored here
    language_preferences: List[str]     # e.g., ["en-US", "fr-CA"],
                                        # a list of language-region
                                        # specifiers in order of preference


class UserInfo(persistent.Persistent):
    def __init__(self) -> None:
        self.userid_hashed = b''
        self.last_login = int()
        self.current_issue = int()
        self.current_subuser = ""
        # In a future version, a user could have multiple "subusers" to use
        # trying out the demo system in a single-user "sandbox".  In other
        # words, a single user would switch between subusers manually
        # simulating what would happen with multiple users, without actually
        # interacting with any other real person users.
        self.subusers = PersistentMapping()
        self.client_settings = UserClientSettings()


def add_user(userid: str, pwd: str,
             authdb_conn: ZODB.Connection.Connection) -> bool:
    """Return False if user already exists
    """
    authdb_root = authdb_conn.root()
    if not hasattr(authdb_root, "userid_salt"):
        authdb_root.userid_salt = 0 #os.urandom(16)
    if not hasattr(authdb_root, "passwords"):
        authdb_root.passwords = OOBTree()

    #userid_hashed = hashlib.scrypt(bytes(userid, 'utf-8'),
    #				  salt=authdb_root.userid_salt,
    #				  n=16384,
    #				  r = 8,
    #				  p = 1)
    #store userid as plaintext for now
    userid_hashed = bytes(userid, 'utf-8')
    if authdb_root.passwords.has_key(userid_hashed):
        return False
    else:
        pwd_salt = os.urandom(16)
        authdb_root.passwords[userid_hashed] = UserAuth(
            userid_hashed,
#			hashlib.scrypt(bytes(pwd, 'utf-8'),
#					  salt=pwd_salt,
#					  n=16384,
#					  r = 8,
#					  p = 1),
# using pbkdf2 instead of scrypt for now, to avoid requiring
# OpenSSL version 1.1.1
            #TODO: store the password hash type and hash parameters in the database
            # in case they change.  (The parameters are probably embedded in the
            # digest--i.e. included in the hashed password string.)
            hashlib.pbkdf2_hmac('sha512',
                      bytes(pwd, 'utf-8'),
                      pwd_salt,
                      Config.pbkdf2_hash_iterations
                      ) \
                if UserPasswordType.pbkdf2_hmac_sha512 == Config.user_password_type \
                else PasswordHasher().hash(pwd).encode('utf-8'),
            pwd_salt
        )
        transaction.commit()
        return True

