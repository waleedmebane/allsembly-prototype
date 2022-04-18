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

""" Globally available config settings
"""

from allsembly import CONSTANTS
from allsembly.CONSTANTS import UserPasswordType


class Limits:
    """ These are arbitrary limits to decrease the likelihood
        of server overload.
    """
    max_contrib_per_user_per_issue = 10000
    max_total_nodes_per_issue = 25000
    max_issues_per_user = 2500
    max_total_issues = 25000
    max_queue_items = 100000
    max_subusers_per_user = 1000
    max_text_input_string_chars = 4000
    max_users = 500


def set_limits(
        max_contrib_per_user_per_issue: int = Limits.max_contrib_per_user_per_issue,
        max_total_nodes_per_issue: int = Limits.max_total_nodes_per_issue,
        max_issues_per_user: int = Limits.max_issues_per_user,
        max_total_issues: int = Limits.max_total_issues,
        max_queue_items: int = Limits.max_queue_items,
        max_subusers_per_user: int = Limits.max_subusers_per_user,
        max_users: int = Limits.max_users
) -> None:
    Limits.max_contrib_per_user_per_issue = \
        max_contrib_per_user_per_issue
    Limits.max_total_nodes_per_issue = max_total_nodes_per_issue
    Limits.max_issues_per_user = max_issues_per_user
    Limits.max_total_issues = max_total_issues
    Limits.max_queue_items = max_queue_items
    Limits.max_subusers_per_user = max_subusers_per_user
    Limits.max_users = max_users


class Config:
    rpyc_server_default_port = 10888
    # TODO: address and ipv6 are currently hard-coded in allsembly_demo.py
    #  and allsembly.AllsemblyServer.server_main_loop(...). maybe change this
    #  in the future.
    rpyc_server_default_address = '::1'
    rpyc_server_default_ipv6: bool = True
    time_msec_for_one_iter_of_order_processing = 100
    time_msec_for_one_iter_of_graph_updating = 100
    pbkdf2_hash_iterations = CONSTANTS.TWO_HUNDRED_THOUSAND
    argon2id_hash_iterations = 2 #currently not used
    # TODO: implement and use SRP 6a as the default
    user_password_type = UserPasswordType.argon2id
    number_of_threadpool_threads = 6
    #whether to store userid as plaintext or as a secure hash of the userid
    store_userid_as_hashed_userid = True #currently not used


def set_config(
        time_msec_for_one_iter_of_order_processing: int =
        Config.time_msec_for_one_iter_of_order_processing,
        time_msec_for_one_iter_of_graph_updating: int =
        Config.time_msec_for_one_iter_of_graph_updating,
        pbkdf2_hash_iterations: int =
        Config.pbkdf2_hash_iterations,
        number_of_threadpool_threads: int =
        Config.number_of_threadpool_threads,
        store_userid_as_hashed_userid: bool = Config.store_userid_as_hashed_userid,
        argon2id_hash_iterations: int = Config.argon2id_hash_iterations,
        user_password_type: UserPasswordType = Config.user_password_type,
        rpyc_server_default_port: int = Config.rpyc_server_default_port,
        rpyc_server_default_address: str = Config.rpyc_server_default_address,
        rpyc_server_default_ipv6: bool = Config.rpyc_server_default_ipv6
) -> None:
    Config.time_msec_for_one_iter_of_order_processing = \
        time_msec_for_one_iter_of_order_processing
    Config.time_msec_for_one_iter_of_graph_updating = \
        time_msec_for_one_iter_of_graph_updating
    Config.pbkdf2_hash_iterations = \
        pbkdf2_hash_iterations
    Config.number_of_threadpool_threads = \
        number_of_threadpool_threads
    Config.store_userid_as_hashed_userid = \
        store_userid_as_hashed_userid
    Config.argon2id_hash_iterations = argon2id_hash_iterations
    Config.user_password_type = user_password_type
    Config.rpyc_server_default_port = rpyc_server_default_port
    Config.rpyc_server_default_address = rpyc_server_default_address
    Config.rpyc_server_default_ipv6 = rpyc_server_default_ipv6