.. Allsembly documentation master file, created by
   sphinx-quickstart on Tue May 11 10:37:15 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Allsembly™'s documentation!
======================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation_and_testing
   user_s_guide
   programmer_s_guide
   license


Introduction
============

This is software for creating an online community for anonymous proposal and collaborative evaluation of public policy options, with automated decision support.
It makes use of betting markets and Bayesian networks.

Only about half of the major features have been added, so far.

The way the finished software is supposed to work as an online community is
as follows, roughly.

Potential participants sign up to get accounts using their real identities, 
which are checked.  However, those identities are kept separated from their
userid that they use to login using cryptographic technology in such a way that
the userid and real identity cannot normally be reconnected.  For details, see :ref:`Design for confidentiality` 
in the Programmer's Guide.  Participants will not know each other's identities,
not even their userids.  All contributions will be anonymous to other users. 
The reasons for this are explained in the file `misc/prospectus.pdf <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/prospectus.pdf>`_ in the 
`source code repository <https://github.com/waleedmebane/allsembly-prototype>`_.  Anonymity means that
users will be free to speak their minds because they cannot be retaliated 
against, and it also means that markers of different status are obscured so that
status is less likely to become a reason to accept or reject the statements made
by any individual participant.  Contributions are written, which further helps
to obscure irrelevant personal features such as appearance, manner of speaking, 
dialect or accent, and speaking confidence.  Dialogues are asynchronous, like
email, rather than real time like chats because this process is concerned with
the best reasons and arguments of the group, rather than their off the cuff
thoughts.  It is not that there is no value in engaging with people early in the
process of the formation of their opinions, including with their first impressions. 
It's possible that could engender empathy or greater understanding under some
conditions or otherwise help people to reflect on their previously held views. 
However, that is not what the Allsembly™ community is designed for.  It is 
designed to determine which positions are best justified by evidence and what 
the justifications are.  The community's values understood after reflection 
on the needs of others in empathetic dialogue are important as a basis for such
justifications, but the best processes for producing such understandings may 
not be the best process for determining the best justified positions in an efficient way that allows for broad participation, which includes diverse 
participants.  Instead, there can be two (or more) processes which complement 
each other.  Also there can be different senses of justification: e.g., 
epistemic justification or procedural justification.  In some theories of 
deliberative democracy, a decision is justified when it was the product of
the right kind of process that gives all of the people an equal chance of 
having their points of view and concerns come to be embodied in the decision.
Even if it is otherwise a bad decision, their voices were heard and *fairly*
taken into account.  In another sense, that I'm calling *epistemic justification* a decision is justified by a standard of what is good that is separate from
the process itself.  It might be good, for example, when more people are better
off as a result.  The kind of justification of concern for the Allsembly™ 
community is epistemic justification, and the content of the good is left up
to the participants, but it should be what they can maintain with logical
consistency to be *the common good*.

Any member of the Allsembly™ community may, at any time, propose an issue to be 
addressed by the community.  When enough other members concur on its importance,
a panel is convened by (semi-)randomly selecting participants from among all of
the membership (members being those with accounts).  The membership, therefore,
forms a kind of selection pool, and a panel is similar to a jury, but it might
contain thousands of participants.  We should hope for the membership to be as
large and diverse as possible.  Ideally it would consist of the whole community,
such as the populace of a city or country.  That is for two reasons.  We want
the panel to have access to points of view representative of the community so
that their judgement is likely to correspond with that of the whole community 
on what are the norms and values of the community; and we want the panel to 
collectively have a large body of knowledge and expertise to draw upon (even 
though they are also able to investigate topics outside of their base of 
knowledge).

After a panel is convened, it proceeds in the way described in the file 
`misc/notes.md <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/notes.md>`_ in the source code repository and shown to some extent in the 
screen shots in the User's Guide.  Participants
present policy proposals as described in `misc/prospectus.pdf <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/prospectus.pdf>`_, and then they
present positions, statements about the evaluation of those proposals, and pro and
con evidence to support such statements.  The pro and con evidence statements
are themselves positions which may be supported or opposed with new pieces of, 
respectively, pro and con evidence.  Each contribution of new pro or con piece of
evidence is accompanied by a bet, expressing a level of confidence that by the
end, all of the weight of evidence in the chain of evidence will, on net, 
support that position (i.e., all of the opposing evidence eventually presented 
will not be enough to defeat it).  The software uses probability to estimate
the weight of the evidence as each new piece of evidence is added and as
participants adjust their expressed confidence in positions by making new bets.
A bet is supposed to represent the taking of a risk.  Thus a participant is
rational when their bet corresponds with what they actually believe.  And 
participants will be constrained to contribute only logically consistent 
positions.  See `misc/notes.md <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/notes.md>`_ for some further explanation.

In the end, proposals will have probability estimates associated with them.
Probability estimates might contain error.  So the result gives us a clear
policy recommendation only when its probability estimate is significantly
greater than its mutually exclusive rivals.  Otherwise, it enables us to see
which policy options are most well supported and, in many cases, it should 
reveal which fundamental disagreements on facts, values, or norms are 
responsible for the lack of decisive recommendation.

Remaining details have to to with the presentation of the proposals, evaluation
criteria, and pro and con positions (i.e., evidence).  Not all of that has been
definitively worked out.  What is needed is that each contribution be more or
less unique--in the ideal case, exactly unique.  A position should not prevail
because it is repeated more often than another, but, furthermore, we need the
size of the collection of contributions to be no larger than it needs to be so
that it is not too difficult for participants to read and evaluate them.  The
dialogue is represented by a (tree-like) graph.  Each branch of the graph contains a single
topic, which should aid in keeping contributions relevant.  But also a 
contribution that might appear irrelevant might just need to be contributed 
to a different part of the graph.  Having a graph makes both things possible.
Contributions are not prejudiced as irrelevant if one can find somewhere in the
graph to put them, even by adding a new initial position, but each branch is
kept on topic.  Some other details can be found in `misc/notes.md <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/notes.md>`_ and 
`misc/prospectus.pdf <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/prospectus.pdf>`_ and gleaned from the User's and Programmer's Guides.  In 
the future, I expect that summarization will have an important role to play as
well.  For example, the positions with the highest probability estimates or
highest last bet price might appear at a glance and others be visible after
clicking to expand a set.  'Bargain'-priced positions might still appear at a
glance in a separate market-watch style tab, maybe depending on user preference
settings.  Other summarization possibilities are to be investigated.

Note that the presentation of the graph is as a tree.  So, it could also have
been presented in the familiar style of threaded email or threaded forum posts,
and that can still be an alternative layout.  However, that layout takes a lot
of space vertically, whereas the standard tree view expands a similar amount in
both dimensions (depending, of course, on the contributions).  For now, the
standard tree style is used.

No account will be necessary to view contributions but only to make 
contributions.  However, access without an account is not implemented, yet. 
In the current implementation, users do not interact with each other, but
just have private 'sandboxes' in which they can try out the existing features.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Copyright © 2021 Waleed H. Mebane

Permission is granted to copy, distribute and/or modify this document
under the terms of the GNU Free Documentation License, Version 1.3;
with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
A copy of the license is included in the section entitled "GNU
Free Documentation License".

