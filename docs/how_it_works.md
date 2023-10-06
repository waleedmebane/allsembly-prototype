Copyright © 2021, 2023 Waleed H. Mebane
Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU Free Documentation License, Version 1.3;
with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

This is eventually meant to contain some more technical details,
but for now it contains a less technical overview.

The system does not do belief revision or conditionalization.  Instead,
it potentially creates a new model of the relationships between positions
with each new user contribution, and then calculates the marginal
probabilities from that new model.  In that way it incorporates the
total of available information.

It may be thought of as that the model is crowdsourced from the human
participants.  (The term "crowdsource" is sometimes considered to refer
to a method that is less inclusive than what is desired of this system,
so I will generally avoid it, but it is useful for conveying a vivid
impression of the mechanism in this case.)

For example:

Suppose that there are two arguments in favor of the same conclusion, as
represented below.

1) A decrease in revenue -> we ought to spend less
2) A lowering of taxes -> we ought to spend less

Initially, the system naively considers all positions to be independent.
Suppose they are accepted by a majority of the participants as indicated
by medium to high market price; then they will both independently
contribute to the probability of the conclusion, giving the conclusion
a calculated very high probability.  Human users are responsible for
noticing this state of affairs.  For example, a user might propose that
the two arguments are the same, in which case they have been double-
counted.  If it were agreed by the majority that they are the same,
the model is adjusted, and the new calculated probability for the 
conclusion would be the result of counting them together only once.

However, the two are not the same, but they are not independent either.
Taxes are not the only source of revenue.  We could say that a lowering
of taxes implies a decrease in revenue, all other things being equal.

So the dependence could be modeled by adding a new argument:

3) lowering of taxes AND no corresponding increase in other revenue -> a decrease in revenue

With this, there is a dependence relationship and the new probability
calculation will reflect that provided "lowering of taxes" in (2) is
recognized as the same as "lowering of taxes" in (3).  (Of course the
relationship depends on other factors as well, such as how much money
is being taxed in this period relative to the last, i.e., whether the
economy has grown.  And that could be a factor in whether someone
accepts the conclusion of (1) and (2) as well.  I do not assume that
they are true statements, only that they are statements that we could 
readily imagine being asserted and contested in public policy
dialogues.)

Suppose, instead, that the wording of (2) was 

2a) A lowering of levies -> we ought to spend less

A vote of a majority of users could establish that it means the same
thing as "lowering of taxes" since majority vote is authoritative on
matters of definition in this system.  Then, suppose that the original
writer maintains that what was meant my "levies" was something other
than monetary levies or taxes (but it is nevertheless related to the
conclusion, perhaps even through some complex chain of reasoning).  That 
author may simply write a new argument using clearer language.  Its
relationship to the conclusion might be in doubt (see the discussion of
"relevance" or "connectedness" in misc/notes.md in the repository).

Suppose that a majority is in bad faith when they vote on definitions,
such that they make words mean whatever they need to mean in order that
their preferred positions get a higher calculated probability than
alternatives.  That is mitigated by the fact that the majority must live
with those definitions as well, even if it affects the probabilities of
their prior and future conclusions, but opponents may always choose
different words.

So, the system does not do belief revision or conditionalization, AND
it is not an autonomous system either.  It is a system combining
human intelligence and machine intelligence (such as it is).  The 
machine intelligence is only in the probabilistic inference, i.e.,
the calculation of marginal probabilities.  The human users construct
the formal models over which inference is performed, and they do so
using a friendly user interface that hides the technical details. 

The human users also provide the prior probabilities, that is, their
judgments about whether each position will be supported by the
preponderance of evidence by the end of the exercise.  Those judgements
count as initial evidence.  And, in fact, the conclusions are ultimately
only based on such judgements.

To be sure, that means that a group that is not sensitive to evidence or
that always accepts conclusions arrived at in some other way in preference
to evidence-backed ones, will barely be helped, if at all, by this
system.  But such a group has a more serious problem.  If they are 
rational in the practical sense of choosing means necessary to achieve
their goals, then they are in for a rude awakening in the long run.
Given that evidence is a reliable indicator of what reality is like and
non-evidential beliefs match reality only more or less by chance, they
are likely to fail to achieve their goals in catastrophic ways in the
long run.  Therefore, I take it, that it is highly unliky that such a
group exists: groups that are less than perfectly sensitive to
evidence, yes, but not groups that are perfectly insensitive to 
evidence.  The skew toward beliefs not backed by evidence should be
expected to be small or medium and not large.

Suppose that a group is composed of members of three dispositions:
1) those who are perfectly insensitive to evidence;
2) those who are insensitive to evidence on some matters and sensitive
to evidence on others;
3) those who are perfectly sensitive to evidence.

The third group can still benefit from increased knowledge and the 
recognition of relationships between pieces of information provided by
a large group and the capacity to draw complex inferences supported by
a computational system.

The size of the first group should be expected to decrease over time as
they confront harsh realities at odds with their beliefs.

The second group can have their evidence-backed beliefs brought into
juxtaposition with their non-evidential beliefs if we suppose that their
judgements provided in the system are made according to their beliefs
(and the betting system provides an incentive from practical rationality
to do so).  When an evidence-backed belief they hold is inconsistent
with a non-evidential belief they hold, even through a chain of
inference, that fact will sometimes be exposed in the course of the
argumentation.  The system does not allow them to simultaneouly bet
on both positions.  Even if they do not change their beliefs, they must
choose on which of their beliefs to base their judgement (bet).  If most 
participants choose to base their judgements on the evidence, the system
rewards them for doing so as well.  (Only if most participants have the
same non-evidential epistemology would the system reward them for
adhering to it in their judgements.)

That wrapped up, consider the incentives participants have to notice
problems with the relationships between positions, as mentioned earlier, 
or with the prevailing judgements about positions (their market price).
No participant is assumed to be a partisan or advocate of a position
(although they may be).  A participant may change their mind about a
position at any time and they are expected to do so whenever the 
evidence so warrants.  However, at any given time, some participants 
should be expected to feel strongly about a position.  Suppose that
position is an underdog (i.e., the vast majority of people judge it
to be incorrect).  The believer is able to purchase bets in that
position at a discount and does so rationally because of their strong
belief.  However, it is only evidence that will sway the other participants
and make good the believer's investment.  Thus, the believer, to be
rational, must believe that the evidence will come out or that they will
provide it themselves and/or that the correct relationships between the
positions will be represented.  (Alternatively, they might believe they can
dupe the others into accepting the position for non-evidential reasons,
but the system is supposed to make that difficult.  Or they might believe
that the others will be sensitive to non-evidential considerations--that
case has been dealt with above.)  Keep in mind that beliefs do not 
directly influence the outcome (bets do), but correspondence between
beliefs and bets would be generally expected of practically
rational individuals in this system unless they can find a system-
subverting strategy for doing better.

Suppose, on the other hand, that a participant believes strongly in
a position that is strongly supported by the vast majority of other
participants.  They, too, are rational in betting on the position.  That
is because it is a "safe" position, even though its price is high (as
indicated by the very fact that its price is high).
