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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registration/', views.registration_view, name='registration'),
    path('logged_out/', views.logout_view, name='logged_out'),
    path('demo/', views.demo, name='demo'),
    path('argue/', views.argue, name='argue'),
    path('propose/', views.propose, name='propose'),
    path('get_arg_graph/', views.get_arg_graph, name='get_arg_graph'),
    path('get_position_details/', views.get_position_details, name='get_position_details'),
    path('clear_graph/', views.clear_graph, name='clear_graph'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
