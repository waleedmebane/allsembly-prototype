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
""" Contains functions for handling web requests and a function
"application(...)" that implements the CGI backend for the web services
as a WSGI application.

See allsembly_demo.py for an example of its use.

Look in the files "allsembly-prototype/web/allsembly_demo.xsl"
and "allsembly-prototype/web/allsembly_demo_login.xsl" to see the
requests that are sent in the current implementation.
"""

import pickle


from typing_extensions import Final
from werkzeug.wrappers import Request, Response
from jsonrpc import JSONRPCResponseManager #type: ignore[import]
from jsonrpc import dispatcher
import rpyc #type: ignore[import]
from typing import Optional, Any

from allsembly.config import Config
from allsembly.rpyc_server import AuthCredentialsStr, AllsemblyServices
from allsembly.speech_act import ArgueSpeechAct, Argument, Premise, Bid, UnconcededPosition, ProposeSpeechAct, \
    InitialPosition, ProOrCon

AUTHENTICATION_CREDENTIALS_FROM_COOKIE: bytes = b''
SERVER_PORT_NUMBER: Final[int] = Config.rpyc_server_default_port

@dispatcher.add_method #type: ignore[misc]
def argue(issue: int,
          subuser: str,
          arg_is_support_arg: bool,
          target_position: int,
          bid_on_target: Optional[float],
          bid_amount_on_target: int,
          first_premise: str,
          bid_on_first_premise: float,
          bid_amount_on_first_premise: int,
          inf_premise: str,
          bid_on_inf_premise: float,
          bid_amount_on_inf_premise: int) -> bool:
    #TODO: check types of data coming in from JSON-RPC
    # convert if possible; otherwise, fail on incompatible types
    issue #temporarily unused
    bid_on_target #temporarily unused
    bid_amount_on_target #temporarily unused
    bid_amount_on_first_premise #temporarily unused
    bid_amount_on_inf_premise #temporarily unused
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    my_argue_speech_act = ArgueSpeechAct(
      Argument(
        ProOrCon.PRO if
          arg_is_support_arg
          else ProOrCon.CON,
        Premise(
          first_premise,
          Bid(min(99.0, bid_on_first_premise), 50.0, 1)
        ),
        UnconcededPosition(target_position),
        None, #allsembly.Bid(0, 0, 0), #bid on target is currently ignored
        None,
        [(Premise(
          inf_premise,
          Bid(min(99.0, bid_on_inf_premise), 50.0, 1)
          ),
          None
         )
        ]
      )
    )
    #I'm picking the my_argue_speech_act object because it will otherwise
    #be passed by reference (as a "netref") by RPyC.
    #Maybe it would also work to arrange it so the variable goes out of
    #scope before client.close() or is unbound.  I haven't tried it, and I
    #also imagine it could create a race condition.  It might work to
    #to not use a variable at all, but would make the call harder to read.
    ret: bool = True
    try:
        client.root.get_user_services(
            AUTHENTICATION_CREDENTIALS_FROM_COOKIE
            ).argue(0, subuser, pickle.dumps(my_argue_speech_act))
    except AllsemblyServices.NotAuthenticated:
        ret = False
    client.close()
    return ret


@dispatcher.add_method #type: ignore[misc]
def propose(issue: int,
            subuser: str,
            position_text: str) -> bool:
    issue #temporarily unused
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    my_propose_speech_act = ProposeSpeechAct(
                         InitialPosition(position_text, [(Premise("premise", Bid(50,50,10)
                                                                ), None
                                                        )]
                                        )
                           )
    #I'm picking the my_propose_speech_act object because it will otherwise
    #be passed by reference (as a "netref") by RPyC.
    #Maybe it would also work to arrange it so the variable goes out of
    #scope before client.close() or is unbound.  I haven't tried it, and I
    #also imagine it could create a race condition.  It might work to
    #to not use a variable at all, but would make the call harder to read.
    ret: bool = True
    try:
        client.root.get_user_services(
            AUTHENTICATION_CREDENTIALS_FROM_COOKIE
            ).propose(0, subuser, pickle.dumps(my_propose_speech_act))
    except AllsemblyServices.NotAuthenticated:
        ret = False
    client.close()
    return ret

@dispatcher.add_method #type: ignore[misc]
def get_arg_graph(issue: int) -> Optional[str]:
    issue #temporarily unused
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)

    try:
        my_graph: Optional[str] = client.root.get_user_services(
            AUTHENTICATION_CREDENTIALS_FROM_COOKIE
            ).get_arg_graph(0)
    except:
        my_graph = None
    client.close()
    return my_graph

@dispatcher.add_method #type: ignore[misc]
def get_position_details(issue: int, pos_id: int) -> Optional[str]:
    issue #temporarily unused
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    #Trying lambda method of invoking services without the
    # posibility of exceptions; the problem is that an exception
    # might still be able to be raised by RPyC if a netref is
    # bound to a variable when the connection is closed. E.g.,
    # if a later programmer changes this code to something like:
    # server = client.root.get_user_services_noexcept(
    #      AUTHENTICATION_CREDENTIALS_FROM_COOKIE
    #     )
    # my_pos = server.get_position_details(0, pos_id)
    # client.close() # here "server" is still bound to an RPyC netref
    # return my_pos
    # I haven't tested whether code like that causes RPyC to
    # raise an exception.
    #UPDATE: I may have found a library to do this in a more
    # natural way: github.com/dry-python/returns.
    #Get position's full text if authenticated; otherwise,
    # client.root.get_user_services_noexcept
    # returns None and the lambda returns None.
    my_pos: Final[Optional[str]] = \
        (lambda server: server.get_position_details(0, pos_id)
           if server is not None #get_user_services_noexcept returns
                                 # None if authentication fails
           else None
        )(client.root.get_user_services_noexcept(
          AUTHENTICATION_CREDENTIALS_FROM_COOKIE
         )
        )
    client.close()
    return my_pos

@dispatcher.add_method #type: ignore[misc]
def clear_graph() -> bool:
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    #Trying lambda method of invoking services without the
    # posibility of exceptions. This might not eliminate the risk
    # of exceptions.  (See comment under get_position_details, above.)
    #Delete issue if authenticated; otherwise,
    # client.root.get_user_services_noexcept
    # returns None and the lambda returns False.
    ret: Final[bool] = (lambda server: server.delete_issue(0)
                                  is None #delete_issue always returns None,
                                          # so this branch always returns True
                           if server is not None #get_user_services_noexcept returns
                                                 # None if authentication fails
                           else False
                       )(client.root.get_user_services_noexcept(
                          AUTHENTICATION_CREDENTIALS_FROM_COOKIE
                         )
                        )
    client.close()
    return ret

def login(request: Any) -> Any:
    """ Only for use within the application(...) function.
    Implements the login page as part of a WSGI application.
    """
    # TODO: set a limit on the lengths of these inputs
    userid: Final[str] = request.form['userid']
    password: Final[str] = request.form['password']
    client: Final = rpyc.connect("::1", SERVER_PORT_NUMBER,
                                 config={"allow_public_attrs": True, "sync_request_timeout": None},
                                 ipv6=True)
    encrypted_credentials_or_none = client.root.authenticate_user(
        AuthCredentialsStr(userid,
                           password)
    )
    if encrypted_credentials_or_none is None:
        response = Response(
            """<?xml version="1.0" encoding="UTF-8"?>
            <?xml-stylesheet href="/allsembly/allsembly_demo_login.xsl" type="text/xsl" ?>
            <BadAuth />
            """, mimetype="text/xml")
    else:
        response = Response(
            """<?xml version="1.0" encoding="UTF-8"?>
            <?xml-stylesheet href="/allsembly/allsembly_demo.xsl" type="text/xsl" ?>
            <RootElement />
            """, mimetype="text/xml")
        # set the login cookie, which contains the encrypted login credentials
        # special prefix "__Host-" causes behavior in some browsers that
        # mitigates against "session fixation" attacks
        response.set_cookie("__Host-login",
                            encrypted_credentials_or_none.decode('utf-8'),
                            secure=True,
                            httponly=True,
                            samesite="Strict")
    client.close()
    return response


def application(environ: Any, start_response: Any) -> Any:
    """ A WSGI application implementing the connection between
    the web and the Allsembly server and providing the web
    services.
    """
    # In the case of GET requests, it loads either the main
    #  Allsembly demo page or the login page, depending on whether
    #  a login cookie has already been stored and contains
    #  authentic login credentials.
    # In the case of POST requests, if it is a form that is POSTed,
    #  it treats that as a login attempt.
    # Otherwise, it must be an XmlHttpRequest.  It processes those
    #  through the jsonrpc package's tools.  The JSONRPCResponseManager
    #  dispatches the JSON-RPC request sent through the POST to
    #  one of the handler functions above, in this file, and then
    #  takes the function's return value of and packages it into
    #  a valid JSOM-RPC reply that can be sent as the body of an
    #  HTTP response.
    # The handler functions send corresponding requests to the
    #  Allsembly server using RPyC (python to python RPC).
    request = Request(environ)

    if request.mimetype == 'application/x-www-form-urlencoded'\
            or request.mimetype == 'multipart/form-data':
        if request.method == 'POST':
            if "userid" not in request.form or request.form['userid'] == "":
                response = Response(
                    """<?xml version="1.0" encoding="UTF-8"?>
                    <?xml-stylesheet href="/allsembly/allsembly_demo_login.xsl" type="text/xsl" ?>
                    <MissingUserId />
                    """, mimetype="text/xml")
            elif "password" not in request.form or request.form['password'] == "":
                response = Response(
                    """<?xml version="1.0" encoding="UTF-8"?>
                    <?xml-stylesheet href="/allsembly/allsembly_demo_login.xsl" type="text/xsl" ?>
                    <MissingPassword />
                    """, mimetype="text/xml")
            else:  # check the credentials
                response = login(request)
        else:  # initial page load
            response = Response(
                """<?xml version="1.0" encoding="UTF-8"?>
                <?xml-stylesheet href="/allsembly/allsembly_demo_login.xsl" type="text/xsl" ?>
                <RootElement />
                """, mimetype="text/xml")
    else:
        #check for a login cookie
        if "__Host-login" in request.cookies:
            client: Final = rpyc.connect("::1", SERVER_PORT_NUMBER, config={"allow_public_attrs": True, "sync_request_timeout": None},
                                         ipv6=True)
            encrypted_credentials_or_none = client.root.authenticate_user(
                request.cookies["__Host-login"].encode('utf-8')
            )
            if encrypted_credentials_or_none is None:
                if request.method == 'POST': #arrived here via XmlHttpRequest
                    response = Response(status=401) #Error, Unauthenticated
                else: #load login page
                    response = Response(
                    """<?xml version="1.0" encoding="UTF-8"?>
                    <?xml-stylesheet href="/allsembly/allsembly_demo_login.xsl" type="text/xsl" ?>
                    <RootElement />
                    """, mimetype="text/xml")
            else:
                if request.method == 'POST': #arrived here via XmlHttpRequest
                    global AUTHENTICATION_CREDENTIALS_FROM_COOKIE
                    AUTHENTICATION_CREDENTIALS_FROM_COOKIE = encrypted_credentials_or_none
                    json_response = JSONRPCResponseManager.handle(
                        request.data, dispatcher)
                    response = Response(json_response.json, mimetype='application/json')
                else: #initial page load
                    response = Response(
                    """<?xml version="1.0" encoding="UTF-8"?>
                    <?xml-stylesheet href="/allsembly/allsembly_demo.xsl" type="text/xsl" ?>
                    <RootElement />
                    """, mimetype="text/xml")
        else:
            if request.method == 'POST':  # arrived here via XmlHttpRequest
                response = Response(status=401)  # Error, Unauthenticated
            else:  # load login page
                response = Response(
                """<?xml version="1.0" encoding="UTF-8"?>
                <?xml-stylesheet href="/allsembly/allsembly_demo_login.xsl" type="text/xsl" ?>
                <RootElement />
                """, mimetype="text/xml")

    return response(environ, start_response)