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
""" Classes representing the betting exchanges.  Not fully implemented.
These are not used in the current version.
There will be one exchange per 'issue' containing one
 market per position.
An order book (see https://en.wikipedia.org/wiki/Order_book and
 https://www.5minutefinance.org/concepts/the-limit-order-book) is used
 to keep track of bids.  It works like an 'auction market' (see
 https://www.investopedia.com/terms/a/auctionmarket.asp). Since this
 is a betting market, both sides of a sale make bids, but one side bids
 to place a bet on success and the other side bids to place a bet on
 failure.  A betting contract can be made between bettors agreeing on
 price (i.e. price "p" for success and price "1-p" for failure).
 Ordinarily, this means:
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
There are special conditions needed for price to correspond
 with probability of success.
 Participants cannot be withholding information that, if known, would
 swing the estimate.  That is, if I know a decisive reason why a position
 that currently has a high price is actually false, no one else knows it,
 and I wait until the near the end of the exercise to share it, then
 all along, the price was very wrong as an indicator of the probability
 of success.  However, the market is supposed to give participants an
 incentive to share their best evidence early.  They cannot know that
 no one else knows it, and they know that others have an incentive to
 investigate and find it out, in any case.  So, their best chance of
 getting the benefit (in the form of 'profit') from their knowledge is
 to share it early.  If that happens, then the price might swing a lot
 early in the trading, but later stabilize.  This does not mean that the
 position is probably true or that no decisive reason that it is false
 exists.  But it is probably true to the best of the knowledge of the
 group and of their ability to learn relevant pro and con evidence in the
 time allotted.
 The "Efficient Market Hypothesis" and related empirical results seeming
 to confirm it says some of what I wrote above in a different way.
 I also think I see a reasonable analogy with the way that scientists get
 credit for their work by publishing it.  They have an incentive to
 publish before others working on similar projects (or so I understand);
 they cannot change the estimate, accepted within the community, of the
 probability of the truth of theories in any other way than by offering
 evidence (in an ideal characterization); and that evidence is presented
 publicly and peer reviewed.
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
 they paid).  In that case, it is useful to look at it as though they
 have 'ante'd up' their betting contract price.  If they paid 70 cents,
 and I buy their contract for 60 cents, their 10 cents remains with
 the contract.  The contract will still pay up to 70 cents to the other
 bettor on the contract, but 10 cents comes from the previous contract
 owner before any money is taken from me.  So I break even at 60 cents
 which is the same as if I'd purchased a new contract for 60 cents.
 Suppose, again, that the original bettor paid 70 cents, but this time
 I buy their contract for 80 cents.  I still only have an obligation
 to pay the other bettor on the contract up to 70 cents, and I stand
 to win up to 30 cents, but I have already paid 10 cents to the
 original bettor (and they received 'back', in essence, their ante'd
 sum of 70 cents, which I replaced). So I only break even at 80 cents.
 And I stand to gain only up to 20 cents on net, which is the same
 as if I'd purchased a new contract for 80 cents.
 In terms of accounting, though, I don't think I would want to
 modify the ids of the parties on the 'contract' written in the
 ledger.  Instead I think there should be a line indicating that
 it was sold and to whom and for how much.  To find out the current
 owner, we would work our way forward through the chain of sales,
 or to start from a current owner and find out which contract
 they are obligated under: first find the sale item with the presumed
 current owner's id; check that there is no later sale, then find
 the mentioned contract id number.
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
        queues.  (Lists will be made into priority queues using the
        algorithm from the heapq module of the Python standard library.)
        Re-sale of old betting contracts is accommodated by having
         separate seller queues (self.support_asks and self.oppose_asks).
        Since sellers cannot sell to other sellers, the order book needs
         to keep track of sellers separately from buyers.  There will be
         four queues: bids for support contracts, bids for oppose contracts,
         offers for support contracts, offers for oppose contracts.  Bids for
         support contracts can be matched with bids for oppose contracts to
         enter the parties into a new contract or with support offers to transfer
         an old contract, and correspondingly with bids for oppose contracts
         and their counterparts.
        A user also may not buy from or sell to self.
    """
    def __init__(self) -> None:
        self.support_bids = PersistentList()
        self.oppose_bids = PersistentList()
        self.support_asks = PersistentList()
        self.oppose_asks = PersistentList()

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
