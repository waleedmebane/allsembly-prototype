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
"""Classes for representing the kinds of actions that a participant
can take in a dialogue.  These are used in user requests to the
Allsembly server.  They will correspond to the formal dialogue
specification, which is not yet included with the source package.
The formal specification currently exists only as an early draft.
"""
from enum import Enum, auto
from typing import Optional, Tuple, List
from typing_extensions import Final

from allsembly.config import Limits


class ProOrCon(Enum):
    PRO: Final[int] = auto()
    CON: Final[int] = auto()


class Bid:
    """ Represents an offer to buy a bidding contract.
        Bid prices should be between 0 and 1 in certain
        increments (e.g., .001).
        Which position it is for and whether it is
        pro or con the position is determined by
        context.
        If it is a bid on the conclusion of an argument,
        it will have the same pro/con value as the
        argument.
        If it is a bid on a premise, it will be a
        pro bid.
    """
    def __init__(self,
                 max_price: float,
                 min_price: float,
                 amount: int) -> None:
        self.max_price = max_price
        self.min_price = min_price
        self.amount = amount #maximum number of betting contracts
                             #to purchase


class MarketLocator:
    """Issue id and position id, needed
       to locate a market within the betting exchange
    """
    def __init__(self, issue_id: int, position_id: int):
        self.issue_id = issue_id
        self.position_id = position_id


class IndependentBid:
    """ Represents an offer to buy a bidding contract
        specifically pro or con a specific position.
        Bid prices should be between 0 and 1 in certain
        increments (e.g., .001).
    """
    def __init__(self, max_price: float, min_price: float,
                 market_locator: MarketLocator,
                 pro_or_con: ProOrCon) -> None:
        self.max_price = max_price
        self.min_price = min_price
        self.market_locator = market_locator
        self.pro_or_con = pro_or_con


class ExistingPosition:
    """ A position already entered into the graph.
    """
    def __init__(self, position_id: int):
        self.position_id: int = position_id

    def get_id(self) -> int:
        return self.position_id


class PremiseBase:
    pass

class Premise(PremiseBase):
    """ An ordinary premise.
        A commitment in the form of a bid is required to assert
        an ordinary premises.  That expresses that the user
        has confidence in the premise.
    """
    def __init__(self, statement: str, bid_on_statement: Bid) -> None:
        #TODO: sanitize input strings
        self.statement = statement[:Limits.max_text_input_string_chars]
        self.bid = bid_on_statement


class UnconcededPosition(PremiseBase, ExistingPosition):
    """ A position that is already in the graph.
        When it is used as a premise, no bid is required.
        Participants may use other participants'
        premises in their arguments even when they do
        not believe them to be true.
        This is necessary for participants to make reductio
        style arguments and draw out contradictions in others'
        positions.
    """
    def __init__(self, position_id: int):
        self.pos_id: int = position_id

class HypotheticalPremise(PremiseBase):
    """ Not implemented yet.
        A normal bid of support has to be greater than 50 'cents'
        of a 'dollar', indicating support and not indifference
        (i.e., > 50% confidence).
        Confidence in a HypotheticalPremise has to be greater
        than that in any of its mutually exclusive alternatives,
        expressing a belief that it is the best candidate for
        truth, so far, among the alternatives.
        Therefore, asserting a HypotheticalPremise entails
        stating what the mutually exclusive alternatives are
        and disclosing one's level of confidence for all
        but one of them.  It must be consistent with all of them
        possibly summing to one (when each has a value between
        zero and one), and the asserted premise must have
        the largest confidence value among the alternatives.
    """
    pass


class ChainArgument:
    """ An chain of arguments to be paired with a position.
        Since it doesn't give its target.  The target can
        be implicit: whatever it is paired with.
        So the chain of arguments can be constructed
        recursively.
        A user might want to support their asserts with
        complex chains of arguments.  That way they can
        ensure that the value of their assertions from the start
        reflects the chain of support that they know about.
    """
    #chaining might not be important since it can be done
    #with multiple, separate ArgueSpeechActs as well.
    #so chaining will not be fully implemented in the first version
    def __init__(self, pro_or_con: ProOrCon, first_premise: Premise,
                 argument_about_first_premise: Optional['ChainArgument'],
                 remaining_premises:
                     List[Tuple[Premise, Optional['ChainArgument']]]
                 ) -> None:
        self.pro_or_con = pro_or_con
        self.first_premise = first_premise
        self.argument_about_first_premise = argument_about_first_premise
        self.remaining_premises = remaining_premises

class Argument:
    """ Required elements of an argument for an
        ArgueSpeechAct
    """
    def __init__(self, pro_or_con: ProOrCon, first_premise: Premise,
                 target_position: UnconcededPosition,
                 bid_on_target: Optional[Bid],
                 argument_about_first_premise: Optional[ChainArgument],
                 remaining_premises:
                     List[Tuple[Premise, Optional[ChainArgument]]]
                ):
        argument_about_first_premise #not used; ignoring chained arguments
        self.pro_or_con = pro_or_con
        self.premises = [first_premise]
        self.target_position = target_position
        self.bid_on_target = bid_on_target
        for rp in remaining_premises: #ignoring chained arguments
            self.premises.append(rp[0])

class InitialPosition:
    """ In an inquiry dialogue, these will be the same as arguments,
        but they will have an explicit conclusion
        rather than a target, and premises are optional.
        In a deliberation, these will be either action proposals
        or evaluation criteria.
        For now, no bid is required on an initial position.
        If it is in an inquiry dialogue, there will probably be only
        one initial position.
    """
    def __init__(self, conclusion: str,
                 #first_premise: Premise,
                 #argument_about_first_premise: Optional[ChainArgument],
                 #remaining_
                 premises:
                     List[Tuple[Premise, Optional[ChainArgument]]] = []
                ):
        #self.premises = [first_premise]
        #TODO: sanitize input strings
        self.conclusion = conclusion[:Limits.max_text_input_string_chars]
        self.premises: List[Premise] = []
#		for rp in remaining_premises: #ignoring chained arguments
        for rp in premises: #ignoring chained arguments
            self.premises.append(rp[0])


class ArgueSpeechAct:
    """ Request for adding an argument into the
        argument graph.
    """
    #TODO: I think I should change this from a class to a type alias
    def __init__(self, argument: Argument):
        self.argument = argument

class ProposeSpeechAct:
    """ Request for adding an InitialPosition to the
        argument graph
    """
    #TODO: I think I should change this from a class to a type alias
    def __init__(self, initial_position: InitialPosition):
        self.position = initial_position

class Ask:
    """ Represents an offer to sell an existing bidding
        contract held by the user-owner.
        Not implemented yet.
    """
    pass

class ArgumentScheme:
    # might not be a separate category from Argument
    # this would be a rule from which all premises of
    # an argument could be derived given some parameter-arguments.
    # The relevance of the derived argument would not
    # be in doubt.
    # For some general information about Argument Schemes
    # see https://en.wikipedia.org/wiki/Argumentation_scheme .
    pass
