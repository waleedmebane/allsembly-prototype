Copyright © 2021, 2023 Waleed H. Mebane
Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU Free Documentation License, Version 1.3;
with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

Allsembly™ Prototype

This is software for collaborative creation of justification arguments.
User participants should be able to express their level of confidence in 
positions (statements) that they and other participants assert.
They do this by placing bets on the chance of the accumulated evidence
supporting the position (and, implicityly, by how much) by the end of the exercise.
As with prediction markets, the price of a bet is set between 0 and 1, e.g.,
dollar.  The current price of a bet (the price of the last bet) is 
taken to be a probability.  It is the aggregated judgement of the 
participants about the position or aggregated level of confidence in the
position.

A Bayesian network is implicitly set up representing the relationships
between the positions.  This is accomplished by expressing the arguments
in a logical form, as Problog programs.  Problog is a probabilistic logic
programming language, an extension of Prolog.  This program currently
depends on Problog for its probability calculations.  Positions 
are given initial probabilities based on the prices of bets on those
positions, and their relationships (of, e.g., independence or dependence)
are modeled according to their logical relationships.
Then all of the positions have their marginal probabilities calculated.


The result is an estimate of the confidence one ought to have in each
position (if one is Bayesian), given the weight of evidence pro and con, 
that has been given so far.
There is evidence that human reasoning is Bayesian (although boundedly so).
See Charter and Oaksford 2007, _Bayesian Rationality_.  If that is the case, 
the more evidence is presented, and people change their bets in light of the
evidence, the more the bet price and the calculated estimate of the weight
of the evidence should align.
Reasons for their non-alignment could be:
1) There is evidence that some participants are basing their judgements on
(perhaps unknowingly) that has not been articulated, yet.
2) Relationships between evidence and conclusions are not properly
specified.  The probability calculations could be an over or under count
because dependencies between the evidence statements are not taken into 
account.  When those dependencies are identified by the participants, by
marking statements as mutually exclusive or as equivalent and adding
more arguments creating additiona links between them, the probabilities
should start to look more reasonable.
3) Participants are making their bets for reasons other than their judgement
of the weight of the evidence, e.g., cognitive bias or self-interest bias or
in-group/out-group bias or emotional resonance.
4) Participant rationality is bounded and they haven't considered the
evidential relationships broadly enough or there are inconsistencies in
the beliefs they hold, which they have not noticed yet or which they are
unwilling to regard as inconsistent for some psychological reason.

The betting is supposed to give an incentive for participants to give their
true assessments of what the rational confidence in a position ought to be.
They are not asked what they believe, but rather how confident they are that
the position will be supported by the evidence by the end of the exercise.

The betting is also supposed to give an incentive to contribute evidence
since evidence is needed to change other participants' judgements about
the question, whether the position will be supported by the end, or their
levels of confidence in those judgements.  It may also be an incentive to
seek out evidence, so as to take advantage of potentially currently
undervalued positions.

Bets work in the following way:
If I bet 70 cents against your 30, I am expressing my confidence that the final valuation will be greater than or equal to 70 cents, and I promise to pay you the difference if the final valuation is lower.
E.g., if the final valuation is 50 cents, I pay you 20 cents; if the final valuation is 80 cents, you pay me 10 cents.

This is in contrast with prediction markets in which the payout for a winning
bet is a full 'dollar'.  This is for two reasons:  1) the status of the 
statement remains uncertain at the end; 2) participants should not be
incentivized to, en masse, try to switch their positions (sell their betting
contracts and buy new ones) to the most popular position when the exercise
gets close to its end, if their only reason for doing so would be its
popularity and not their assessment of the evidence.  A participant may
gain ('profit') merely by converting some other participants to their view, 
even if their view isn't the prevailing one by the end.

The betting is intended to be done with play money and with a betting limit.
Each market (each of which is for a separate position) will have a
separate allocation of amounts of play money to each participant.
The amounts may not be shared between markets.  This is so that the
betting limit remains effective at preventing market manipulations.
Participants will not be able to accumulate profits from many markets 
and pool them to manipulate some other market (e.g., to put all their
profits into shoring up some highly preferred position).  The total
of each participant's 'profit' from all markets may still be used to rank
participants in terms of their relative performance.

The probability estimate is supposed to show how belief in evidence ought to
propagate according to the model of rationality given by the axioms of 
probability.

In particular, beliefs must be consistent.  A .9 probability of the truth
of a statement is incompatible with a .9 probability of the truth of
a mutually exclusive state of affairs or normative claim.  The probability
calculus will cause participant bets and the calculated estimate to
diverge when participants hold inconsistent views.

Furthermore, participants will be prevented from making inconsistent bets,
such as bets both supporting and opposing the same position, unless the
prices are compatible (i.e. 70% confidence is compatible with 30% doubt),
and they are set by the participant to sell automatically if they come 
into conflict.

If other participants make reductio ad contradictione arguments using
positions all of which one supports, one will be obliged to modify one's
bets so that they become consistent or produce an acceptable rebuttal.
(How to produce an acceptable rebuttal has not been worked out, yet.
I believe the only rebuttal could be that the argument was not
"connected" as defined below.)

One issue that needs futher consideration is the relevance of
presented evidence to alleged conclusions.  It is a semantic issue and
cannot be determined automatically for natural language arguments.
It will have to be determined by a vote, but that gives majority
(as opposed to logical relationships) great power over the outcome.
To mitigate this, participants can reassert their arguments in a different
logical form if they are rejected by a majority as lacking relevance.

Henceforth I will use the term "connectedness" instead of relevance to
highlight the fact that it is a binary consideration.  Either it is
connected (e.g., in a graph of the relationships between arguments) or
it is not.  It is connected when the evidence has the right sort of 
semantic relationship to its alleged conclusion.  When it is connected
it can still be a bad argument because the inference rule that allegedly
connects it with the conclusion could be false.  That is, evidence
connects with inference rules, and inference rules connect with
conclusions.  A deductive inference rule in the form: if a and b
and ... z and not exception_a and not exception_b and ... not
exception_z, then conclusion, fully specifies what evidence is required
to make its conclusion true.  Its conclusion need not be a statement
of the form: p is _certain_.  It can be of the form: p is _expected_ or
_probable_.  The qualifications a-z and exceptions a-z also narrow the
_scope_ of applicability of the rule.  And one each of the qualifications
and exceptions could be an unknown, catching all that we haven't named, yet.
Therefore it is possible for a probabilistic argument to use
deductive inference.

An inference rule of this sort can be a _scheme_ for generating arguments.
If I assert the rule and that the rule implies the conclusion, I may
be taken to also be asserting all of the conjuncts a-z are true and
none of exceptions a-z are true.  All of a-z and exceptions a-z are
guaranteed to be connected to the inference rule, and the question will
only be whether the inference rule is true, that is, whether it expresses
the proper proportions of influence of the qualifying factors and
exclusions that in fact lead to the conclusion.  It can be criticized
like a normal position.  It can be bet on and new arguments pro and con
can be asserted about it.

In that way, the participant may escape having their argument
summarily dismissed on account of lack of connectedness.  It is only
necessary that the group accept some generic argument schemes as 
expressing semantic relations that connect their antecedents and 
consequents.  Then they can be used by all participants for arguments
on every side of any issue.

A second way for a participant to get around a majority vote against
semantic connectedness of their argument could be to use a controlled
natural language, such as Attempto, together with a machine readable
dictionary, such as Wordnet, to establish the semantic connectedness.

Neither the method of argument schemes or the method of controlled 
natural language are implemented at this time.

A third way, simpler than the previous two, is to make an additional 
argument that goes in between the argument that needs to be connected
and its alleged conclusion. The new argument has as one of its premises
an intermediate conclusion to which the old argument is connected,
and has as its conclusion the conclusion of the old argument.  In
other words, it might just be a matter of breaking the inference
down into smaller steps until the connectedness of the whole chain
of arguments becomes evident.

It is hoped that participation in a computer-supported collaborative
argument creation (reasoning) exercise, such as intended to be provided
by the software would help many of the participants to align their judgements
with the available evidence, both by having more evidence come out--
contributed by all of the participants--and by getting a clear indication
of how their judgements compare to the aggregated judgements and to the
probability estimates.

Copyright © 2021 Waleed H. Mebane
