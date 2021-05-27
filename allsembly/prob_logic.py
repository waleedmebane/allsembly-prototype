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
""" Interface to the probabilistic logic code (currently using
the Problog python package).
"""

import logging
from logging import Logger

import persistent #type: ignore[import]
import problog #type: ignore[import]
from persistent.list import PersistentList #type: ignore[import]
from persistent.mapping import PersistentMapping #type: ignore[import]
from readerwriterlock import rwlock
import re

from typing import Any, Dict, cast
from typing_extensions import Final

logger: Logger = logging.getLogger(__name__)

class ProblogModel(persistent.Persistent):
    """Problog terms and rules that model the argument graph
       and allow Problog to create the Bayesian Network
       and do the inference.
       Uses "virtual evidence": uncertain evidence is modelled with
       a probabilistic rule, where the probability is the certainty
       of the evidence; the antecedent is virtual evidence, with
       probability 1, and the consequent is the real evidence.

       Note that the current Problog models (constructed in ArgumentGraph 
       methods, _add_clause_to_problog_program(), 
       _add_virtual_evidence_to_problog_program(), and
       _add_term_and_query_to_problog_program())
       are not necessarily the best for all 
       kinds of arguments.  The For example, the inference in causal arguments 
       might only go in one direction.  Dealing most appropriately with 
       all major types is a longer-term goal.
    """
       # In future it will be possible to update the model by reusing 
       # the same program with different
       # weights if no new arguments have been added--method taken from:
       # https://dtai.cs.kuleuven.be/problog/tutorial/01-compile-once.html
    pl_model: Any
    _v_my_rwlock = rwlock.RWLockWrite()

    def set_problog_program(self, problog_program_string: str) -> None:
        #parse the Problog string
        logger.debug(problog_program_string)
        self.pl_model: Any = problog.program.PrologString(problog_program_string)

    def get_problog_query_results(self) -> Dict[int, float]:
        with self._v_my_rlock:
            ret = cast(Dict[int, float],
                self._problog_query_results[self.read_buffer_index]
                       )
        return ret

    def __init__(self) -> None:
        self._problog_query_results: Any = PersistentList([PersistentMapping(), PersistentMapping()])
        self.read_buffer_index = 0
        self.write_buffer_index = 1
        self._v_my_wlock = ProblogModel._v_my_rwlock.gen_wlock()
        self._v_my_rlock = ProblogModel._v_my_rwlock.gen_rlock()

    def __setstate__(self, state: Dict[Any, Any]) -> None:
        self.__dict__ = state
        self._v_my_wlock = ProblogModel._v_my_rwlock.gen_wlock()
        self._v_my_rlock = ProblogModel._v_my_rwlock.gen_rlock()

    def calculate_marginals(self) -> None:
        """calculates the posterior probabilities"""
        # compile the model
        query_results: Final[Dict[str, float]] = problog.get_evaluatable()\
                                                 .create_from(self.pl_model)\
                                                 .evaluate()
        #logger.debug(query_results)
        self._problog_query_results[self.write_buffer_index].update(
            #making a dict with node number as key and posterior probability as value
            #by removing the leading character from the node name to get the node number
#           {int(str(x)[1:]): y for x, y in query_results.items()}
           {int(re.sub(r'\(t\)', r'', str(x)[1:])): y for x, y in query_results.items()}
        )
        swap_index: int = self.write_buffer_index
        self.write_buffer_index = self.read_buffer_index
        with self._v_my_wlock:
            self.read_buffer_index = swap_index

    def add_terms(self, new_terms: str) -> None:
        """updates the model from string"""
        #stub

    def update_term_weights(self, updated_weights: Dict[str, float]) -> None:
        """updates model weights from dict"""
        #stub

