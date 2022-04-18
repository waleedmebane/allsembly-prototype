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
""" Globally available constants collected in one place
"""

from typing_extensions import Final
from enum import Enum, auto

MILLION: Final[float] = 1000000.0
HALF_MILLION: Final[int] = 500000
TWO_HUNDRED_THOUSAND: Final[int] = 200000

class UserPasswordType(Enum):
    """ Options for user password authentication hashes
        or "Password Authenticated Key Exchange" (SRP6a)
    """
    argon2id: Final[int] = auto()
    pbkdf2_hmac_sha512: Final[int] = auto()
    #scrypt is not currently available because I haven't installed
    #version 1.1.1 of openssl, which is needed to use/test it
    #scrypt = auto
    #authentication with SRP 6a is not implemented, yet, but is
    #intended to be the default and the preferred method.
    #I am not an expert in cryptography or security, but as
    #I understand it, SRP 6a does not require the storage of
    #any password equivalent material on the server--i.e., the
    #stored information on the server is not by itself sufficient
    #for someone to recover the password by any means
    #srp6a = auto