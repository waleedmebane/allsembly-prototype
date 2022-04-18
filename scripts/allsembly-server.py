#!/usr/local/bin/python3

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
"""Starts the Allsembly server.
Run with -h to see descriptions of available command line options.

To test,
 Run like: ./allsembly-server.py

Ctrl-C exits

To run as a daemon on Linux or Unix, add the flag:
 --daemon

Sending SIGTERM or SIGINT, e.g. using the Unix "kill"
 command from a terminal, will cause it to exit
 gracefully.

To run at startup, reference this script from a systemd
 or initd startup script or add a command like the following
 to your /etc/rc.local file:
 <path-to-script>/allsembly-server.py --daemon --user <unprivileged-system-user>

This server start script is written for and tested with Linux, but
 it might work with Windows if you don't use the
 --daemon or --user command line options and you set
 Windows style path names for the locations of the database
 files using the --userdb_filename and --argdb_filename command line options.
"""
import argparse
import io
import signal
import logging
import os
import pwd
from contextlib import nullcontext

import daemon
from logging import Logger

from typing import TextIO, Optional
from typing_extensions import Final

from allsembly.allsembly import ServerControl, AllsemblyServer
from allsembly.common import FinalVar
from allsembly.config import Config

logger: Logger = logging.getLogger(__name__)

def start_service(daemonize: bool = False) -> None:
	logger.info("start_service function called")
	server_control = ServerControl()

	def handle_sigterm(signum, _):
		if signal.SIGTERM == signum\
			or signal.SIGINT == signum:
			server_control.set_should_exit()

	if not daemonize:
		signal.signal(signal.SIGINT, handle_sigterm)
		signal.signal(signal.SIGTERM, handle_sigterm)

	try:
		notification_fileno = FinalVar[Optional[int]](NOTIFICATION_FILEOBJ.fileno())
	except OSError:
		notification_fileno = FinalVar[Optional[int]](None)

	with nullcontext() if not daemonize else \
			daemon.DaemonContext(
				signal_map={signal.SIGTERM: handle_sigterm,
							signal.SIGINT: handle_sigterm},
				files_preserve=[notification_fileno.get()],
				uid=RUNAS_UID,
				gid=RUNAS_GID
			):
		logger.info("starting server")
		AllsemblyServer(
					   USERDB_FILENAME,
					   ARGDB_FILENAME).server_main_loop(
					   NOTIFICATION_FILEOBJ,
					   server_control,
					   SERVER_PORT_NUMBER
						  )
		#server has exited
		logger.info("server has exited")
		#logger.debug(notification_textio.getvalue())
		NOTIFICATION_FILEOBJ.close()


parser: Final = argparse.ArgumentParser()
parser.add_argument("-p", "--port",
                    help="""port number for providing RPC services to 
                    the FastCGI scripts; defaults to """ \
						 + str(Config.rpyc_server_default_port),
                    type=int,
                    default=Config.rpyc_server_default_port)
parser.add_argument("-d", "--daemon",
					help="start the server as a daemon.",
					action="store_true"),
parser.add_argument("-u", "--user",
					help="user to run as when using the --daemon option",
					type=str,
					default=None)
parser.add_argument("--userdb_filename",
                    help="path to the database that stores user "
						 "info other than login credentials"
					     "defaults to: /var/allsembly-prototype/data/userdb",
                    default="/var/allsembly-prototype/data/userdb")
parser.add_argument("--argdb_filename",
                    help="path the the database that stores the issues, "
						 "argument graphs, bids, and bets."
						 "defaults to: /var/allsembly-prototype/data/argdb",
                    default="/var/allsembly-prototype/data/argdb")

args: Final = parser.parse_args()

USERDB_FILENAME: Final = args.userdb_filename
ARGDB_FILENAME: Final = args.argdb_filename
SERVER_PORT_NUMBER: Final = args.port
try:
	RUNAS_UID: Final[int] = pwd.getpwnam(args.user).pw_uid if args.user is not None \
		else os.getuid()
	RUNAS_GID: Final[int] = pwd.getpwnam(args.user).pw_gid if args.user is not None \
		else os.getgid()
	#this is not really important in the current version
	NOTIFICATION_FILEOBJ: Final[TextIO] = io.StringIO("test")

	start_service(daemonize=args.daemon)
except KeyError:
	# expected exception from pwd.getpwnam() if the username
	# given is not in the passwords file/database
	logging.error("NO SUCH USER\n\n")
	raise

