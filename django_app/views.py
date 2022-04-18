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
import pickle

from django.db import IntegrityError
from typing_extensions import Final
import rpyc #type: ignore[import]
from typing import Optional

from allsembly.config import Config, Limits
from allsembly.speech_act import ArgueSpeechAct, Argument, Premise, Bid, \
    UnconcededPosition, ProposeSpeechAct, InitialPosition, ProOrCon

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django_app.models import RegistrationComment


# Create your views here.
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from django_app.forms import LoginForm, ProposeForm, ArgueForm, RegistrationForm

SERVER_PORT_NUMBER: Final[int] = Config.rpyc_server_default_port
SUPPORT: Final[str] = 'Pro'
OPPOSE: Final[str] = 'Con'


@require_http_methods(["GET", "POST"])
def login_view(request):
    form = LoginForm()
    context = {'form': form}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse(demo))
        else:
            context.update({'auth_failed': True})
    return render(request, 'django_app/login.html', context)


@require_http_methods(["GET", "POST"])
def registration_view(request):
    context = {}
    limits = Limits() # TODO: using the default Allsembly limits;
                      #  in future, make this configurable
    if User.objects.count() < limits.max_users:
        if request.method == 'POST':
            form = RegistrationForm(request.POST)
            context.update({'form': form})
            if form.is_valid():
                # check that passwords match
                password = form.cleaned_data['password']
                password_again = form.cleaned_data['password_again']
                if not (password and password_again and
                        password == password_again):
                    context.update({'passwords_mismatched_or_missing': True})
                else:
                    username = form.cleaned_data['username']
                    email_address = form.cleaned_data['email_address']
                    realname = form.cleaned_data['name']
                    comment = form.cleaned_data['comment']
                    try:
                        User.objects.create_user(username=username,
                                                 password=password)
                        if comment and comment != '':
                            reg_comment_entry = RegistrationComment(username=username,
                                                                    real_name=realname,
                                                                    email_address=email_address,
                                                                    comment=comment)
                            reg_comment_entry.save()
                        user = authenticate(request, username=username, password=password)
                        if user is not None:
                            login(request, user)
                            return HttpResponseRedirect(reverse(demo))
                        else:
                            context.update({'auth_failed': True})
                    except IntegrityError:
                        context.update({'error_nonunique_userid': True})
        else: # GET request
            form = RegistrationForm()
            context.update({'form': form})
    else: # maximum number of users reached
        context.update({'user_limit_reached': True})
    return render(request, 'django_app/registration.html', context)


def logout_view(request):
    logout(request)
    return render(request, 'django_app/logout_success.html')


@login_required(login_url='login')
def demo(request):
    propose_form = ProposeForm()
    argue_form = ArgueForm()
    context = {'propose_form': propose_form, 'argue_form': argue_form}
    return render(request, 'django_app/demo.html', context)

@login_required
@require_http_methods(["POST"])
def argue(request):
    form = ArgueForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': 1, 'error_text': 'Invalid input.' })

    argument_is_PRO: Final[bool] = form.cleaned_data['pro_or_con'] == SUPPORT
    first_premise: Final[str] = form.cleaned_data['first_premise']
    target_position_text: Final[str] = form.cleaned_data['target_position_text']
    inf_premise_from_form: Final[Optional[str]] = form.cleaned_data['inf_premise']
    inf_premise: Final[str] = inf_premise_from_form \
        if inf_premise_from_form is not None and inf_premise_from_form != "" \
        else "IF " + first_premise \
			 + "\nTHEN " \
		     + ("" if argument_is_PRO else "NOT ") \
             + target_position_text

    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    my_argue_speech_act = ArgueSpeechAct(
      Argument(
        ProOrCon.PRO if
          argument_is_PRO
          else ProOrCon.CON,
        Premise(
          first_premise,
          Bid(min(100.0-1e-9,
                  max(1e-9, form.cleaned_data['bid_on_first_premise'])
                  ),
              50.0,
              1)
        ),
        UnconcededPosition(form.cleaned_data['target_position']),
        None, #allsembly.Bid(0, 0, 0), #bid on target is currently ignored
        None,
        [(Premise(
          inf_premise,
          Bid(min(100.0-1e-9,
                  max(1e-9, form.cleaned_data['bid_on_inf_premise'])
                  ),
              50.0,
              1)
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
    ret = client.root.get_user_services(
        bytes(request.user.username, 'utf-8')
        ).argue(0, "", pickle.dumps(my_argue_speech_act))
    client.close()
    return JsonResponse({'success': ret, 'error' : 0 if ret else 1})

@login_required
@require_http_methods(["POST"])
def propose(request):
    form = ProposeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': 1, 'error_text': 'Invalid input.' })

    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    my_propose_speech_act = ProposeSpeechAct(
                         InitialPosition(form.cleaned_data['position_text'],
                                         [(Premise("premise", Bid(50,50,10)
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
    client.root.get_user_services(
        bytes(request.user.username, 'utf-8')
        ).propose(0, "", pickle.dumps(my_propose_speech_act))
    client.close()
    return JsonResponse({'success': True, 'error' : 0})


@login_required
@require_http_methods(["GET"])
def get_arg_graph(request):
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    my_graph: Final[str] = client.root.get_user_services(
        bytes(request.user.username, 'utf-8')
        ).get_arg_graph(0)
    client.close()
    return HttpResponse(my_graph)


@login_required
@require_http_methods(["GET"])
def get_position_details(request):
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    my_pos: Final[Optional[str]] = client.root.get_user_services(bytes(request.user.username, 'utf-8'))\
        .get_position_details(0, int(request.GET['id'])) \
        if 'id' in request.GET \
        else None
    client.close()
    if my_pos is not None:
        return JsonResponse({'success': True, 'error': 0, 'result': my_pos})
    else:
        return JsonResponse({'success': False, 'error': 1, 'error_text': 'Missing position id.'})


@login_required
@require_http_methods(["GET"])
def clear_graph(request):
    client = rpyc.connect("::1", SERVER_PORT_NUMBER, config = {"allow_public_attrs": True, "sync_request_timeout": None}, ipv6=True)
    #Trying lambda method of invoking services without the
    # posibility of exceptions. This might not eliminate the risk
    # of exceptions.  (See comment under get_position_details, above.)
    #Delete issue if authenticated; otherwise,
    # client.root.get_user_services_noexcept
    # returns None and the lambda returns False.
    client.root.get_user_services(bytes(request.user.username, 'utf-8'))\
        .delete_issue(0)
    client.close()
    return JsonResponse({'success': True, 'error': 0})