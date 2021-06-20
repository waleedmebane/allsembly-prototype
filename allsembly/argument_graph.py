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
""" Contains classes and functions for building arguments and for
representing them in a graph, and also for representing a graph visually
(currently by using GraphViz to produce an scalable vector graphics string).
These classes and functions are used by the allsembly module.
The functions to build arguments and insert them into the graph are
 called in the allsembly module in response to requests made by users
 through the RPC module, "rpyc_server", which in turn come through
 the WSGI server in the demo module, which in turn come through the
 web server initiated by the client code in the web directory of this package,
 "web/allsembly_demo.xsl".
"""

import copy
import time
import logging

import persistent #type: ignore[import]
from persistent.list import PersistentList #type: ignore[import]
from persistent.mapping import PersistentMapping #type: ignore[import]
from readerwriterlock import rwlock
import heapq
import pygraphviz as pgv #type: ignore[import]
import re
from BTrees.OOBTree import OOBTree #type: ignore[import]
from typing import List, Dict, Set, Any, Optional, cast
from typing_extensions import Final

from allsembly.betting_exchange import BettingExchange
from allsembly.common import FinalVar
from allsembly.config import Limits
from allsembly.prob_logic import ProblogModel

logger: logging.Logger = logging.getLogger(__name__)

class ArgumentNode(persistent.Persistent):
    """An argument which has as its conclusion either that its
       parent is true (when self.supports_conclusion is true) or
       that its parent is false
    """
    def __init__(self) -> None:
        self.arg_id = int()
        self.supports_conclusion = bool() #otherwise opposes
        self.premises_ids = PersistentList()
        self.conclusion_id = int()
        #reference to inferential premise in premises list
        #self.scheme = InferentialPremiseSubNode()
        self.creation_time = int()
        self.creator = bytes()

def build_ArgumentNode(creator: bytes,
                      supports_conclusion: bool,
                      conclusion_id: int = int(),
                      premise_ids: PersistentList = PersistentList(),
                      creation_time: int = int(time.time()),
                      arg_id: int = int()) -> ArgumentNode:
    new_arg_node = ArgumentNode()
    new_arg_node.arg_id = arg_id
    new_arg_node.supports_conclusion = supports_conclusion
    new_arg_node.premise_ids = premise_ids
    new_arg_node.conclusion_id = conclusion_id
    new_arg_node.creation_time = creation_time
    new_arg_node.creator = creator
    return new_arg_node

class PositionNode(persistent.Persistent):
    """A premise or a conclusion of an argument"""
    def __init__(self) -> None:
        self.pos_id = int()
        self.statement = str()
        #other positions that this is a duplicate of
        #same nodes are duplicated so that the graph remains a tree
        #(i.e., without cycles)
        self.same_as = PersistentList()
        self.creation_time = int()
        self.creator = bytes()
        # used by the Problog model; leaf nodes are virtual evidence
        # set to False when an argument has this node as its conclusion
        self.node_is_leaf_node = True
        self.arguments_pro_and_con_ids: Set[int] = set()

def build_PositionNode(creator: bytes,
                       statement: str,
                       same_as: PersistentList = PersistentList(),
                       creation_time: int = int(time.time()),
                       node_is_leaf_node: bool = True
                       ) -> PositionNode:
    new_pos_node = PositionNode()
    new_pos_node.creation_time = creation_time
    new_pos_node.creator = creator
    new_pos_node.statement = statement
    new_pos_node.node_is_leaf_node = node_is_leaf_node
    return new_pos_node

class ArgumentGraph(persistent.Persistent):
    """Stores all of the arguments for an *issue* and generates
       the visual representation of the graph using PyGraphViz
       and the probabilistic logic program representation using
       Problog.
    """
    _v_my_rwlock = rwlock.RWLockWrite()

    def __init__(self, issue_name: str):
        self.issue_name = issue_name
        self.arg_node_index = PersistentMapping()
        self.pos_node_index = PersistentMapping()
        self.betting_exchange = BettingExchange()
        self.problog_model: ProblogModel = ProblogModel()
        self._v_my_wlock = ArgumentGraph._v_my_rwlock.gen_wlock()
        self._v_my_rlock = ArgumentGraph._v_my_rwlock.gen_rlock()
        self.next_arg_id = int(0) #PicklableAtomicLong(0)
        self.next_pos_id = int(0) #PicklableAtomicLong(0)
        self._v_gv_graph = pgv.AGraph(strict=False, directed=True)
        self._v_gv_graph.graph_attr["rankdir"] = "LR"
        self._v_gv_graph.graph_attr["splines"] = "line"
        self._v_gv_graph.graph_attr["clusterrank"] = "local"
        self._v_gv_graph.graph_attr["compound"] = "true"
        self._v_gv_graph.graph_attr["color"] = "gray"
        self._v_gv_graph.graph_attr["packmode"] = "clust"
        self._v_my_g_svg: List[str] = ["", ""]
        self._build_initial_gv_graph()
        self.read_buffer_index = 0
        self.write_buffer_index = 1
        self.my_problog_prog = str()


    def __setstate__(self, state: Dict[Any, Any]) -> None:
        self.__dict__ = state
        self._v_my_wlock = ArgumentGraph._v_my_rwlock.gen_wlock()
        self._v_my_rlock = ArgumentGraph._v_my_rwlock.gen_rlock()
        self._v_gv_graph = pgv.AGraph(strict=False, directed=True)
        self._v_gv_graph.graph_attr["rankdir"] = "LR"
        self._v_gv_graph.graph_attr["splines"] = "line"
        self._v_gv_graph.graph_attr["clusterrank"] = "local"
        self._v_gv_graph.graph_attr["compound"] = "true"
        self._v_gv_graph.graph_attr["color"] = "gray"
        self._v_gv_graph.graph_attr["packmode"] = "clust"
        self._v_my_g_svg = ["", ""]
        self._build_initial_gv_graph()


    def _add_position_to_gv_graph(self, pos_id: int, pos: PositionNode) -> None:
        p_key = pos_id
        p_value = pos
        price: Final[Optional[float]] = \
            self.betting_exchange \
                                 .markets[p_key] \
                                 .last_support_price \
            if self.betting_exchange.markets.has_key(p_key) \
            else None

        probabilities = self.problog_model.get_problog_query_results()
        prob_string = '{:.1f}'.format(probabilities[p_key] * 100.0) if p_key in probabilities\
            else "50.0"
        #avoid injection and also limit short version of text to 140 characters
        #replacing '\n' with '<br />' causes graphviz to keep newlines
        position_text: Final[str] = re.sub(r'<!\[CDATA\[', r'',
                                           re.sub(r'\]\]>', r'',
                                                  re.sub(r'\n', r'<br />',
                                                         p_value.statement[:140])
                                                  )
                                           )
        label: str = ('<<table border="0" cellborder="0" cellspacing="0" cellpadding="0">'
                      '<tr ><td>')
        label += str(price) + "¢" if price is not None else ""
        label += "</td><td>"
        label += prob_string
        label += ('%</td></tr>'
                  '<tr><td colspan="2" border="1" port="here" cellpadding="5">')
        label += position_text
        label += "</td></tr></table>>"
        self._v_gv_graph.add_node(str(p_key),
                                  label=label,
                                  shape="Mrecord"
                                  )
        self._prepare_graph()

    def _add_argument_to_gv_graph(self, arg_id: int, arg: ArgumentNode) -> None:
        a_key = arg_id
        a_value = arg

        #add arg node containing plus or minus sign
        labeltext: Final[str] = "+" \
                                    if a_value.supports_conclusion \
                                    else "-"
        self._v_gv_graph.add_node("a" + str(a_key),
                                  label=labeltext,
                                  shape="circle"
                                  )

        #add edge from arg node to conclusion
        self._v_gv_graph.add_edge( str(a_value.conclusion_id),
                                   "a" + str(a_key),
                                   arrowsize=0.5
                                   ,dir="back"
                                  )
        #add premises into subgraph
        subgraph_bunch = []
        for p_key in a_value.premises_ids:
            subgraph_bunch.append(p_key)
        self._v_gv_graph.add_subgraph(subgraph_bunch, name="cluster_a" + str(a_key))

        #add edges to arg node
        for p_key in a_value.premises_ids:
            p_value = self.pos_node_index[p_key]
            self._v_gv_graph.add_edge("a" + str(a_key),
                                      str(p_key),
                                      arrowhead="none"
                                      )
        #update premises' prices and probabilities
        for p_key in a_value.premises_ids:
            self._add_position_to_gv_graph(p_key,
                                           self.pos_node_index[
                                               p_key
                                           ])
        if a_value.conclusion_id in self.pos_node_index:
            self._add_position_to_gv_graph(a_value.conclusion_id,
                                           self.pos_node_index[
                                               a_value.conclusion_id
                                           ])
        else:
            self._prepare_graph()
        #done

    def _update_gv_graph_nodes(self) -> None:
        for p_key, p_value in self.pos_node_index.items():
            logger.debug("key " + str(p_key))
            self._add_position_to_gv_graph(p_key, p_value)

    def _build_initial_gv_graph(self) -> None:
        self._update_gv_graph_nodes()
        for a_key, a_value in self.arg_node_index.items():
            self._add_argument_to_gv_graph(a_key, a_value)

    def _add_clause_to_problog_program(self, a_key: int,
                                       a_value: ArgumentNode) -> None:

        term_base: Final[str] = "n" + str(a_value.conclusion_id)
        branch_index_term: str = term_base
        for p in a_value.premises_ids:
            branch_index_term += "_" + str(p)
        evidence_term: Final[str] = branch_index_term + "_ev"
        conclusion_term: Final[str] = branch_index_term
        prior = term_base + "_pri"
        # "Prior" here doesn't mean the same thing as in Bayesian Confirmation Theory.
        # In that case the prior represents belief prior to seeing the evidence,
        #  and generally the evidence is the result of some experiment or the
        #  observation of a future event, so the evidence could not be part of
        #  the prior belief.
        # In this case, belief in the evidence might be included or partly included
        #  in the prior, especially since participants can revise their bets in
        #  light of the evidence.
        # So, "prior" here means the last price as a representation of aggregated
        #  belief.
        # I think that suggests that evidence should not increase belief unless it
        #  is believed to a greater degree than the prior.  The current code does
        #  not behave that way and will probably be updated in the future.
        # The existing model is: (pro evidence AND NOT prior) OR
        #  (NOT con evidence AND prior).
        # If there is no con evidence then it is (pro AND NOT prior) OR prior.
        # In other words, if the pro evidence is true, it adds to the belief
        #  by the amount not included in prior belief; if it is false, it defaults
        #  to the prior.  For example, if prior is 0.5, then, if the evidence is
        #  false, the conclusion is just as likely to be true as false.
        #  If the con evidence is true then it subtracts from belief in the
        #  conclusion by the amount not excluded from prior belief.  If the
        #  con evidence is false it does not effect the result.
        # It is also an assumption that evidence in sibling arguments is
        #  independent.  Thus, if the prior is small, negative evidence won't
        #  make much difference unless it is evidence applied as a con
        #  argument against some pro argument for the conclusion.  E.g.,
        #  conclusion <-- argument for conclusion <-- argument against argument
        #  for conclusion; instead of:
        #  conclusion <-- argument for conclusion
        #             <-- argument against conclusion
        # If you don't want the bet price to influence the calculated probability,
        #  just change prior to a constant value, e.g., 0.5, in the function,
        #  _add_term_and_query_to_problog_program(), below.
        conjuncts = str()
        for p in a_value.premises_ids:
            prem_term = FinalVar[str]("n" + str(p) + "(t)")
            if conjuncts:
                conjuncts += ","
            conjuncts += prem_term.get()
        self.my_problog_prog += evidence_term + " :- " + conjuncts + ".\n"
        if a_value.supports_conclusion:
            self.my_problog_prog += conclusion_term + " :- "
            self.my_problog_prog += evidence_term + ", \\+ " + prior + ".\n"


    def _add_virtual_evidence_to_problog_program(self,
                                                 p_key: int,
                                                 p_value: PositionNode
                                                 ) -> None:
        # I'm not sure that virtual evidence is necessary
        # Problog seems to produce the same results without it, but
        # I haven't investigated it deeply.
        if self.betting_exchange.markets.has_key(p_key):
            prob: float = self.betting_exchange\
                                     .markets[p_key]\
                                     .last_support_price / 100.0
            term: Final[str] = "n" + str(p_key) + "(t)"
            ev_term: Final[str] = "v" + str(p_key)
            self.my_problog_prog += str(prob) + "::" + term + " :- " + ev_term + ".\n"
            self.my_problog_prog += ev_term + ".\n"

    def _add_term_and_query_to_problog_program(self,
                                               p_key: int,
                                               p_value: PositionNode
                                               ) -> None:
        term_base: Final[str] = "n" + str(p_key)
        pos_term: Final[str] = term_base + "(t)"
        con_ev_head_term: Final[str] = term_base + "_con_ev"
        if p_value.node_is_leaf_node:
            self._add_virtual_evidence_to_problog_program(p_key, p_value)
        else:
            prob: float = self.betting_exchange \
                                     .markets[p_key] \
                                     .last_support_price / 100.0 \
                          if self.betting_exchange.markets.has_key(p_key) \
                          else 0.5
            prior: str = term_base + "_pri"
            self.my_problog_prog += str(prob) + "::" + prior + ".\n"
            if p_value.arguments_pro_and_con_ids:
                con_disjuncts = str()
                for arg_id in p_value.arguments_pro_and_con_ids:
                    a_value: ArgumentNode = self.arg_node_index[arg_id]
                    if not a_value.supports_conclusion:
                        branch_index_term: str = term_base
                        for p in a_value.premises_ids:
                            branch_index_term += "_" + str(p)
                        con_evidence_term: str = branch_index_term + "_ev"
                        if con_disjuncts:
                            con_disjuncts += "; "
                        con_disjuncts += con_evidence_term
                if con_disjuncts:
                    self.my_problog_prog += con_ev_head_term + " :- " + con_disjuncts + ".\n"

                pro_disjuncts = str()
                for arg_id in p_value.arguments_pro_and_con_ids:
                    a_value: ArgumentNode = self.arg_node_index[arg_id]
                    if a_value.supports_conclusion:
                        branch_index_term: str = term_base
                        for p in a_value.premises_ids:
                            branch_index_term += "_" + str(p)
                        pro_evidence_term: str = branch_index_term + "_ev"
                        if pro_disjuncts:
                            pro_disjuncts += "; "
                        pro_disjuncts += pro_evidence_term + ", \\+" + prior
                if con_disjuncts:
                    self.my_problog_prog += pos_term + " :- \\+" + con_ev_head_term \
                                            + ", " + prior + ".\n"
                else:
                    self.my_problog_prog += pos_term + " :- " + prior + ".\n"
                if pro_disjuncts:
                    self.my_problog_prog += pos_term + " :- " + pro_disjuncts + ".\n"
        self.my_problog_prog += "query(" + pos_term + ").\n"

    def _build_problog_program(self) -> None:
        self.my_problog_prog = ""
        for a_key, a_value in self.arg_node_index.items():
            self._add_clause_to_problog_program(a_key, a_value)
        for p_key, p_value in self.pos_node_index.items():
            self._add_term_and_query_to_problog_program(p_key, p_value)

    def get_problog_program_string(self) -> str:
        return self.my_problog_prog

    def _problog_calculate(self) -> None:
        self._build_problog_program()
        if self.my_problog_prog:
            self.problog_model.set_problog_program(self.my_problog_prog)
            self.problog_model.calculate_marginals()

    def add_argument(self, argument: ArgumentNode) -> Optional[int]:
        """ Enter a new argument into the arg_node_index
            And return its id number
        """
        if self.next_arg_id <= \
           Limits.max_total_nodes_per_issue:
            arg_id = self.next_arg_id
            self.next_arg_id += 1
            self.arg_node_index[arg_id] = argument
            argument.arg_id = arg_id

            if argument.conclusion_id in self.pos_node_index:
                # update position node with back reference
                self.pos_node_index[argument.conclusion_id] \
                    .arguments_pro_and_con_ids.add(arg_id)
                # argument's conclusion is no longer a leaf node
                # if it was previously
                #if argument.supports_conclusion:
                self.pos_node_index[argument.conclusion_id].node_is_leaf_node = False

            # calculate probabilities for this argument's positions
            self._problog_calculate()
            #add new nodes and edges to graphviz graph
            self._add_argument_to_gv_graph(arg_id, argument)
            self._update_gv_graph_nodes()

            #add rules and disjunctions to problog model

            return arg_id
        else:
            return None

    def get_position_copy(self, pos_id: int) -> PositionNode:
        if pos_id in self.pos_node_index:
            position_copy = cast(PositionNode,
                                 copy.deepcopy(self.pos_node_index[pos_id]))
            return position_copy
        else:
            return PositionNode()

    def add_position(self,
                     position: PositionNode) -> Optional[int]:
        """ Enter a new position into the pos_node_index
            And return its id number.
            For the convenience of producing the drawn argument
            graph/diagram as a tree, the positions that are
            the same are duplicated in the graph.
            However, just one should be referred to in the
            BettingExchange and in the Problog model.
            So, for each position node, a list is kept of other
            position nodes that represent the same position.
            The one with the smallest pos_id will be used by
            the BettingExchange and the Problog model.
        """
        logger.debug("next_pos_id = " + str(self.next_pos_id))
        if self.next_pos_id <= \
                   Limits.max_total_nodes_per_issue:
            logger.debug("?next_pos_id <= " + str(Limits.max_total_nodes_per_issue))
#			pos_id = self.next_pos_id.get_and_set(
#										 self.next_pos_id.value + 1
#										 )
            pos_id = self.next_pos_id
            self.next_pos_id += 1
            logger.debug("next_pos_id = " + str(self.next_pos_id))
            logger.debug("pos_id = " + str(pos_id))
            self.pos_node_index[pos_id] = position
            position.pos_id = pos_id
            #maintain the other position nodes' lists of nodes
            #representing the same position
            for p in position.same_as:
                heapq.heappush(self.pos_node_index[p.pos_id].same_as,
                               pos_id)

            #next add node in graphviz model
            #  getting current price from betting market and
            #  marginal probability from cached problog model results
            self._add_position_to_gv_graph(pos_id, position)
            self._prepare_graph()
            #add probabilistic term to problog model

            return pos_id
        else:
            return None

    def hide_argument(self, index: int) -> None:
        #stub
        pass

    def _prepare_graph(self) -> None:
        self._v_gv_graph.layout(prog="dot")
        self._v_my_g_svg[self.write_buffer_index] = self._v_gv_graph.draw(None, "svg").decode("utf-8")
        self._v_my_g_svg[self.write_buffer_index] = re.sub(
            r'&#45;',
            r'-',
            self._v_my_g_svg[self.write_buffer_index])
        #Make SVG clickable. For now, using regular expression matching.
        # In the future, maybe use something less fragile.
        #old substitution, effective with shape=record but not effective with shape=Mrecord
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<polygon (.*)/>\n<text ', r'<g id="node\1<title>\2</title>\n<polygon \3/>\n<text style="cursor:pointer;" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        #last bet price and calculated probability
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text style="cursor:pointer;" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<text style="cursor:pointer;" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        #calculated probability field above an initial position
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<polygon (.*)/>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<polygon \5/>\n<text style="cursor:pointer;" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        #space around a position's text
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<text (.*)</text>\n<polygon ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<text \5</text>\n<polygon cursor="pointer" pointer-events="visible" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        #first four lines of a position's text
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<text (.*)</text>\n<polygon (.*)\>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<text \5</text>\n<polygon \6/>\n<text cursor="pointer" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<text (.*)</text>\n<polygon (.*)\>\n<text (.*)</text>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<text \5</text>\n<polygon \6/>\n<text \7</text>\n<text cursor="pointer" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<text (.*)</text>\n<polygon (.*)\>\n<text (.*)</text>\n<text (.*)</text>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<text \5</text>\n<polygon \6/>\n<text \7</text>\n<text \8</text>\n<text cursor="pointer" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<g id="node(.*)\n?<title>(.*)</title>\n<path (.*)/>\n<text (.*)</text>\n<text (.*)</text>\n<polygon (.*)\>\n<text (.*)</text>\n<text (.*)</text>\n<text (.*)</text>\n<text ', r'<g id="node\1<title>\2</title>\n<path \3/>\n<text \4</text>\n<text \5</text>\n<polygon \6/>\n<text \7</text>\n<text \8</text>\n<text \9</text>\n<text cursor="pointer" onclick="show_position_details(\2);" ', self._v_my_g_svg[self.write_buffer_index])

        #do this to prevent a participant injecting html or javascript into other participants' browsers
        self._v_my_g_svg[self.write_buffer_index] = re.sub(r'<text (.*)>(.*)</text>', r'<text \1><![CDATA[\2]]></text>', self._v_my_g_svg[self.write_buffer_index])
        swap_index: int = self.write_buffer_index
        self.write_buffer_index = self.read_buffer_index
        with self._v_my_wlock:
            self.read_buffer_index = swap_index


    def draw_graph(self) -> str:
        with self._v_my_rlock:
            ret = self._v_my_g_svg[self.read_buffer_index]
        return ret

class Issues(persistent.Persistent):
    """ Stores argument graphs for all issues.
    """
    def __init__(self) -> None:
        self.graphs = OOBTree()
        self.next_issue_id = int() #PicklableAtomicLong(0)

