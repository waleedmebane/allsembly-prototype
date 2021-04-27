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
""" Starts a development web server running the Allsembly application.
"""

import argparse

from typing_extensions import Final
from werkzeug import run_simple
from allsembly.demo import application
from allsembly.demo_default_settings import dev_host, dev_port_number, dev_ssl_cert_path, dev_allsembly_http_path, \
    dev_web_static_files_path

parser: Final = argparse.ArgumentParser()
parser.add_argument("-s", "--host",
                    help="""name or ip address that the server should 
                    serve pages from; defaults to 'localhost'.""",
                    default=dev_host)
parser.add_argument("-p", "--port",
                    help="""port number for the web server to serve its 
                    pages from; defaults to 8443""",
                    type=int,
                    default=dev_port_number)
parser.add_argument("-c", "--ssl_cert_path",
                    help="path to the SSL certificate and key files that the "
                         "server should use.",
                    default=dev_ssl_cert_path)
parser.add_argument("-w", "--web_static_files_path",
                    help="path on disk to the static web files; "
                         "defaults to /var/www/html/allsembly.",
                    default=dev_web_static_files_path)
parser.add_argument("--allsembly_http_path",
                    help="path to direct a browser to; "
                         "defaults to '/allsembly'. "
                         "This means the location of the static web files will be: "
                         "https://localhost:8443/allsembly by default."
                         "It is not necessary to change this since the dev server "
                         "will serve the application from every path."
                         "It only affects the http location of static files.",
                    default=dev_allsembly_http_path)
args: Final = parser.parse_args()
run_simple(args.host, args.port, application,
           ssl_context=(args.ssl_cert_path + '.crt',
                        args.ssl_cert_path + '.key'),
           static_files={args.allsembly_http_path:
                         args.web_static_files_path}
           )
