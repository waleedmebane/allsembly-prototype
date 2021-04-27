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
""" Classes representing the betting exchanges.  Not fully implemented.
These are not used in the current version.
There will be one exchange per 'issue' containing one
 market per position.
An order book (see https://en.wikipedia.org/wiki/Order_book and
 https://www.5minutefinance.org/concepts/the-limit-order-book) is used
 to keep track of bids.  Since this is a betting market, both sides of
 a sale make bids, but one side bids to place a bet on success and
 the other side bids to place a bet on failure.  A betting contract
 can be made between bettors agreeing on price (i.e. price "p" for
 success and price "1-p" for failure).  Ordinarily, this means:
 if I am bidding on success, I will pay you "1" if there is failure
 and you will pay me "1" if there is success.
These markets are different.  There can be partial success and failure.
 The contracts mean the following.
 For success (i.e., the final estimation of the probability of truth of
 a position): I am bidding on success, which means a final estimate that
 is greater than or equal to my bid; I will pay you the amount of the
 shortfall.  You are bidding on failure, which means a final estimate
 that is less than or equal to your bid.  You will pay me the amount
 by which the final estimate exceeds your bid.
 For example, if I bet 70 "cents" to your 30 "cents", and the final
 estimate is 50 "cents", I pay you 20 "cents".  If the final estimate
 is 80 "cents", you pay me 10 "cents".  You stand to lose at most 30
 "cents", and I stand to lose at most 70 "cents", but if the market
 price was 70 "cents" that indicates a high probability of success;
 the odds are in my favor and my low risk is mitigated by a high price
 and your high risk is mitigated by a low price.
A "ledger" keeps track of the bets.
There will also be a secondary market, integrated with the primary market.
 Participants may change their minds.  In that case they would want to
 sell their contracts.  That market has both buyers and sellers, not only
 buyers, just like the securities exchange markets.  A seller will issue
 an "ask" and it can be matched with any bid.  In other words, as a buyer
 I might buy a new contract made with another buyer who is buying the
 opposite position from me (e.g., "failure" to my purchase of "success"),
 or I might buy out someone else's obligations in an existing contract
 (e.g. they'd bet "success" previously and now want to sell, and I can
 take over their bet of "success" at a new price, possibly lower than what
 they paid).  If the price has gone up, I might pay more than what they
 paid, but I only take on risk (the obligation to pay my counterpart in
 the contract) at the same level they did, so the contract is more
 valuable (e.g. if they purchased at 70 "cents" they could have lost only
 up to 70 "cents"; if they sell to me at 90 "cents", I can still only lose
 70 "cents"; they make 20 "cents", and I get a lower risk contract).
 This has to be taken into account in a future implementation.
"""

import persistent  #type: ignore[import]

from allsembly.speech_act import ProOrCon
from persistent.list import PersistentList #type: ignore[import]
from readerwriterlock import rwlock
#import heapq
from BTrees.OOBTree import OOBTree #type: ignore[import]


class OrderBook(persistent.Persistent):
    """ Order book matching algorithm matches highest bids on each side
        (support or oppose) for pareto optimal matching.
        See https://blogs.cornell.edu/info4220/2016/03/17/nyse-automated-matching-algorithm/
        For that purpose, each side's orders are stored in priority
        queues.
        Re-sale of old betting contracts is mixed in, but flagged so an
        appropriate value can be calculated for matching.
    """
    def __init__(self) -> None:
        self.support_bids_and_asks = PersistentList()
        self.oppose_bids_and_asks = PersistentList()

class BettingMarket(persistent.Persistent):
    def __init__(self) -> None:
        self.market_id = int()
        self.orders = OrderBook()
        self.support_ledger_ref = OOBTree()
        self.oppose_ledger_ref = OOBTree()
        self.last_support_price = float(50.0)

#    def add_orders(self, order_q: OrderQueue) -> None:
#        #stub
#        pass

    def fill_orders_by_matching(self) -> None:
        #stub
        pass

class BettingExchange(persistent.Persistent):
    """ A container for all of the markets.
        There is only one per issue.
    """
    _v_my_rwlock = rwlock.RWLockWrite()
    def __init__(self) -> None:
        self.markets = OOBTree()
        self.support_ledger = OOBTree() #bidding contracts by: support
                                   #bet user, oppose bet user, &
                                   #contract number
        self.oppose_ledger = OOBTree() #as above, but with oppose user
                                  #as first value in key
        self._v_my_wlock = BettingExchange._v_my_rwlock.gen_wlock()
        self._v_my_rlock = BettingExchange._v_my_rwlock.gen_rlock()
