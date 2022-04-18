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
""" Classes containing user data, currently unused.
"""
import persistent  #type: ignore[import]
from persistent.mapping import PersistentMapping  #type: ignore[import]
from typing import List


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