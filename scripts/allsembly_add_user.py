#!/usr/local/bin/python3

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
""" Convenience script for adding a new user.
Do this when the server is not running, since ZODB is not
 a multi-process database.
"""
# In a future version, I can create a new UserAuth object and
#  wrap it in a (yet to be written) add, update, or delete
#  request object, pickle it and write it to disk in a special
#  folder.  Then send SIGHUP to the server, which would
#  instruct it to load the requests from disk.
#  It would have to get a write lock on the database so that
#  it writes the new users when no service threads are trying
#  to use the database for authentication.  Then it would
#  update the database and release the lock.
#  Updates could also include changes, such as to passwords, or
#  to temporarily suspend a user, in addition to additions.

import ZODB
from ZODB.FileStorage import FileStorage
from allsembly.user import add_user
from server_config import AUTHDB_FILENAME

userid = input("UserId: ")
password = input("Password: ")
storage = FileStorage(AUTHDB_FILENAME)
db = ZODB.DB(storage)
conn = db.open()
add_user(userid, password, conn)
conn.close()
db.close()