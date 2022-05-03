Programmer's Guide
==================


Dependencies
------------

Apache2
    This is the web server.  Other web servers could be substituted.  I chose Apache because it is the premier free and open source web server.  We can have confidence in its security and robustness, as much as is possible for web server software.
    
Apache2 mod_wsgi
	For interacting with Django (using the Python WSGI standard directly instead of CGI)

django
    Web framework: provides user login and registration; generates the client-side HTML and javascript pages to serve in response to user actions.  (It also has its own basic webserver, which could be used to try out the Allsembly™ program without installing Apache.)

graphviz

graphviz-dev
    The Python library "PyGraphviz" relies on these.  Graphviz is used to draw the graphs.

Problog
    A probabilistic programming language.  This is used to compute the probabilities.

ZODB
   An object database.  This is used for persistence.  It stores all of the persistent objects.  The default backend is file storage, which is currently being used.  Other storage backends could be used in the future for better scalability, see :ref:`Design for scalability`.

PyGraphviz
    Easy to use Python bindings to the Graphviz library.

RPyC
    Python to Python RPC used to communicate between the Django services and the Allsembly™ server.  It could be useful later for implementing communication with a registration server.  (See :ref:`Design for confidentiality`.)

persistent
    This works with ZODB to automatically save and restore objects that subclass "Persistent".

transaction
    This provides a transaction manager that is used with ZODB.

atomic
    This provides an atomically updatable integer class.

readerwriterlock
    This provides thread synchronization using separate locks for readers and writers.  There can be multiple readers but only one writer.

python-daemon
    This provides an easy API for making a Python program run as a Unix daemon.

d3.js
    This is a graphics library for web clients.  I am currently only using it for pan and zoom of scalable vector graphics (SVG) that is the format of the argument graph.  It could be used to draw alternative layouts of the argument graph on the client-side if desired, especially when accompanied by *d3-graphviz*.

dialog-polyfill.js
    This provides the HTML DIALOG tag and its functionality for browsers that don't (fully) support it, yet.  The DIALOG tag is used for creating the modal dialogs.

jquery-3.6.0.js
    Used to simplify AJAX calls (asynchronous loading of web content using JavaScript).


Future possible dependencies
----------------------------

GPGME
    for encrypting the stream encryption keys with the public key(s) of the admins.  (The stream encryption key will also be encrypted with the user's hashed password.)  See more details about this in the section :ref:`Design for confidentiality`, below).

PyNaCl
    for stream encryption or salsa20 to encrypt a database field containing users' anonymized ids (see more details about this in the section :ref:`Design for confidentiality`, below).

Pyrsistent
    to avoid mistaken call by reference-like behaviors (and, therefore, subtle bugs).

returns
    to replace exceptions for error handling.


Files
-----

| requirements.txt
|     List of required dependencies and their version numbers
| 
| setup.cfg
|     Configuration options for mypy and configuration options for Pylint
| 
| allsembly/
|     All of the modules of the Python package
|
| django_app/
|     App for communicating with users to log them in and to generate
|     the html and JavaScript of the site.  It communicates with the
|     AllsemblyServer to provide the services.
|
| django_site/
|     Configuration information for the Django site, which uses the
|     Django app, the code for which is in the django_app directory.
| 
| docs/
| 
|     _build/
|         The Sphinx-generated HTML documentation, as a git submodule
| 
|     conf.py
|         The Sphinx configuration file.
| 
|     fdl-1.3.txt
|         The GNU Free Documentation License
| 
|     index.rst
|         The main file of the documentation
| 
|     make.bat
| 
|     Makefile
|         Files for building the documentation.  Sphinx is required. 
|     
| LICENSE.third-party/
|     Licenses for third-party software distributed with Allsembly™
| 
| misc/
|     Documents containing additional explanation about what Allsembly™ is about and the theory behind it--these files are not part of the documentation, and might be edited for publication elsewhere at some point.
| 
|     notes.md
|         This file contains an overview of the dialogue procedure and why it is expected to be effective, including notes about a few salient design issues.
| 
|     how_it_works.md
|         This file explains how human participants contribute to making the probabilistic estimates of the truth or correctness of conclusions possible, including a contrived example.
| 
|     prospectus.pdf
|         This file contains a scholarly presentation of the initial development of the theory and concepts that are behind this software prototype and includes some of the motivation as well.
|
| scripts/
| 
|     allsembly-server.py*
|         Use this script to start the Allsembly™ server.  Run it with the ``--help`` option to get usage information.  Also, see, the section :ref:`Installation and Testing` for some instructions.
|     allsembly.service
|         A systemd service script example.  Modify the line "ExecStart"; then use this file to make the allsembly-server.py persistent as a daemon (i.e., make it available on system startup).
|  
| test/
|     The tests.
| 
| web/
|     scripts/
|         The javascript libraries



Specification of requirements (draft)
-------------------------------------

More is to be added to this section later.

Make all of the argumentation and discussion publicly accessible.  This will
support a secondary function of having a kind of encyclopedia of arguments
pro and con issues for repeated reference.  Users should be able to obtain an 
independent URL to any part of an argument or discussion so as to refer to any specific aspect of that argument or discussion.  The data (only completely anonymous or anonymized data) should also be available in a format like Argument Interchange Format (XML-RDF) or CSV (comma-separated values), for computer assisted processing and exploration.  (Public accessibility is not currently implemented.)

Future requirement: provide for third-party clients; maintain a stable client interface.

Design overview
---------------
.. uml:: classes.uml

.. uml:: sequenceDiagram.uml


The client-side code is generated by the Django templates in django_app/templates according to the code in django_app/views.py.

It communicates with the Allsembly™ server using RPC (provided by the RPyC library).  The code on the Allsembly™ server side is in the rpyc_server.py module, especially the AllsemblyServices class.

The interaction proceeds as shown in Figure 2, above.  Currently, since there is no interaction between users--each user is in a kind of *sandbox* of its own--which graph to display is dependent on which user is logged it (i.e., the userid in the encrypted login cookie).

The UserServices object is used to provide each of the specific services that require login, and it is provided with a login username by the django_app, which must have logged in the user.  In most cases, the request is just added to a queue.  The AllsemblyServices RPyC server object is running its event loop in a separate thread from the server main loop.

The server main loop, allsembly.allsembly.AllsemblyServer.server_main_loop(), is started by the script, "scripts/allsembly-server.py", and it, in turn, starts the RPyC service in a separate thread.  In the main loop, each queue is checked and the requests there are processed.  Most of the processing involves calling functions in an ArgumentGraph object.  There is a separate ArgumentGraph object for each graph and it is stored in a mapping that is persisted in the database.  The ArgumentGraph object draws a new graph and calculates new probabilities with each client request that changes the graph.  Currently, after the client makes a request that changes the graph, it immediately after that requests a new drawn graph.  The intention is that in a future version, the client would be subscribed to a server sent events or websockets channel or be waiting on a long poll, to learn when a new graph is ready to be loaded.

Class detail
------------

For now this section just contains the docstrings from the modules.

**allsembly** module
^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.allsembly
   :members:

**rpyc_server** module
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.rpyc_server
   :members:

**demo** module
^^^^^^^^^^^^^^^
.. automodule:: allsembly.demo
   :members:

**user** module
^^^^^^^^^^^^^^^
.. automodule:: allsembly.user
   :members:

**argument_graph** module
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.argument_graph
   :members:

**prob_logic** module
^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.prob_logic
   :members:

**betting_exchange** module
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.betting_exchange
   :members:

**speech_act** module
^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.speech_act
   :members:



Future design
-------------


Design for confidentiality
^^^^^^^^^^^^^^^^^^^^^^^^^^

*This section and the next two sections, "Design for integrity" and "Design for scalability" describe features that are not expected to be added to the prototype.  They would be added later, in a stage of development beyond the prototype.  But they contain important ideas to keep in mind while developing the prototype.*

.. image:: images/anonymity_preserving_registration.*


The figure above shows a design with a separate server for login and a separate
server for registration, which could be hosted by different organizations.
The organization hosting the Registration server verifies the new user's
identity but never sees the user's userid or passwords; those are encrypted
on the client side using the public key of the organization hosting the
login server.

The basic idea is that records containing the userid and records containing
the personally identifying information (PII) are not connected by any
common fields, and cannot be connected without the private key of the ID
guardian.  (One can imagine the ID guardian as a law firm with it's private
key stored offline in a vault or something or escrow service that is somehow 
contractually bound not decrypt the userid field in a database record provided
to it from the registration database by the registering organization without, 
say, a court issued warrant.)

The idea does not necessarily require multiple organizations or servers and
separate DBMSes, though.  It can be accomplished in a single database managed
by one DBMS.  A record in the login table contains, e.g., userid and password.
A record in the registration database contains, e.g., real name, email address,
phone number, address, etc., and encrypted userid (that was encrypted by the
client's device before it reached the server and that can only be decrypted
using the private key held offline).

The flow is as follows:

   #. User connects to the registration server and provides personally identifying information that will be used to verify their identity and provides a desired userid that is encrypted with a public key of the login server (the Allsembly™ server).  The corresponding private key is stored unencrypted on the login server.  
   #. The registration server sends only the encrypted userid and password to the login server. 
   #. The login server informs the registration server whether the userid is unique.  If it is not, then the registration server informs the user to select a new userid.
   #. If the userid is unique, the login server stores the userid and password in its login database (table) with a flag indicating that it is not yet activated (because the user has not yet been verified).
   #. The registration server discards the encrypted password and further encrypts the already encrypted userid with the public key of the ID guardian.  It stores this encrypted userid with the PII in the registration database (table). (The encrypted userid should not be able to be compared with a the same userid encrypted with the same key at a different time.  Therefore, this saved userid might have been separatedly encrypted from the one sent to the login server, with a different random padding.)
   #. The next step is not fully worked out.  It involves passing a token that proves that the user has been verified.  It possibly involves cryptographic signatures and is done in such a way that neither the login server nor the registration server may use its counterpart to send arbitrary encrypted  messages to the user.  (Imagine that there is limited trust between them.)
   #. After the user has been verified, the user logs in to the login server.

Subsequently, the user uses the login server to change their password.  (Or the client might log in to both servers to change passwords, separately on both,
in such a way that it only requires one step for the user.)

If the user needs to change their PII, they log in to the registration 
server using their email adress.  (They could potentially use the same 
password hashed and salted differently.)

To enable recovery of a forgotten userid, userid could be stored by the registration server (or in the registration database) encrypted with the user's password.  The password is not stored bythe registration server, except possibly in hashed form, so the userid is encrypted using the password hashed with a different algorithm and/or parameters. In that case, the user logs into the registration server using email address and password; then, the registration server sends the encrypted userid to the user who decrypts it client-side.

There seems to be no way to recover a forgotten password without temporarily breaching anonymity for that user.  Although the user has both email address and userid, the user cannot authenticate with the login server using an email address without connecting the identities, so password reset via email would only get a user access to their profile on the registration server.

If the ID guardian is a separate person/organization from the organization
hosting the login server, then the representatives of both organizations
are needed to revoke anonymity.

NOTE: THIS IS NOT A PROOF.  THERE COULD BE IMPORTANT FLAWS IN THIS APPROACH.

However, I believe the approach has the following desirable properties:

   #. Attacker cannot learn identities of users by listening to traffic between client and server, without other information.
   #. Attacker cannot learn identities of users by obtaining either or both databases (tables).
   #. Attacker cannot learn the identities of existing users by controlling either or both servers.  (Such an attacker can only learn identities of new registrants andd users resetting their passwords.)


An additional issue for confidentiality is the connection of bets on
positions to userids.  To prevent a whole profile of a user's argumentative
commitments being built up by an attacker, ids used to match users with betting contracts can be anonymized.  The list of anonymized ids that correspond to a 
userid can be maintained as an encrypted field in the database table containing
user information.  The encryption key can be the user's password itself
hashed in a different way and with a different salt than the one stored
for login.  So, when a user logs in they send both hashes.  The server
decrypts the anonymized ids field and caches it for a while to provide
the services to the user.  It remains encrypted at-rest and anytime the
user logs out or the cache expires.

Design for integrity
^^^^^^^^^^^^^^^^^^^^

*This section describes features that are not expected to be added to the prototype.  They would be added later, in a stage of development beyond the prototype.  But it contains important ideas to keep in mind while developing the prototype.*

To provide accountability that the data stored on the server matches the
users' activities, the server should send cryptographically signed receipts
for bids, asks, and betting contract purchases and sales.

The client can store them in local memory and can also store pending
transactions to re-send in case it does not get a confirmation receipt.

Likewise, users should not be able to repudiate their orders or betting contracts.  So, those should be cryptographically signed by users as well.

Design for scalability
^^^^^^^^^^^^^^^^^^^^^^

*This section describes features that are not expected to be added to the prototype.  They would be added later, in a stage of development beyond the prototype.  But it contains important ideas to keep in mind while developing the prototype.*

The current design was not made for massive scalability.  This section is
just to add information about what can be done to scale the existing design
without extensive changes.

First of all different database backends can be dropped in as replacements.
The ZODB API supports ZEO, which is a multi-process available, networkable
DBMS.  It also supports a "Relstorage" backend, which allows for storage in
SQL databasaes such as MySQL, PostgreSQL, and commercial enterprise-scale
SQL DBMSes.  However, it still stores the objects pickled.
An alternative would be to use an SQL DBMS through an object-relational 
mapper (ORM) to possibly eek out some better concurrency.  It might not
be necessary to do that, though.

Python does not provide thread parallelism.  I assume that I will eventually
have to write custom code to replace Problog.  Other than that, I would
propose parallelising the Allsembly™ server using separate processes, with 
each process handling one or more complete issues (whole argument graphs).
The separate processes would have to coordinate with regard to users needing
to participate in issues--a user may participate on multiple issues overlapping
in time--being handled in another process or being handled in multiple 
processes.

Such changes, which are not too extensive with regard to modifications to
the existing design, might enable a lot of scalability and be sufficient for
the Allsembly™ project beyond the prototype.  Massive scalabily could be
part of a separate (we could hope funded) project if it, at some point,  
becomes a widely used piece of software.

Localization
^^^^^^^^^^^^
UPDATE: Part of this can be handled using Django.  More information
to be added.  I would still like to use XML in order to give clients
more control over the presentation, but XML containing the translated
strings can be generated by Django.  The default XSL can also be 
generated by Django, but in advance, rather than on-the-fly.

My current intention is to implement localization by putting the strings
in XML files and using XSLT transforms to select the appropriate
string and to combine it with any dynamic data.

The Accept-Language header or the user's language selection (stored
in a cookie or embodied in a special path, such as /en/file.xml)
can be used to select the appropriate string.

Directives in XML tags can encode the correct way to transform
dynamic data or other words in the text that are dependent on the dynamic
data.

For example, if the dynamic data is a number, another word might have
to be sometimes singular and sometimes plural:

"You have x token(s) remaining."

Sometimes there might be special words when the number is 2 or 3.

Sometimes words might need to be marked with affixes or suffixes to do
with grammatical role.

These things could be accomodated with regular expressions and XSLT
regular expression functions.  The same or similar methods can be
used to accommodate differences in date, time, and number formats
or separators between items in sequences.  Alternatively, some format
preferences could be handled using special code in the server.
For example, the server could be given the user's preference for
probabilities as decimal values or percentages and preference for
dot or comma separating the whole and fractional parts of a number,
etc., and the server would thenceforth produce probabilities that way,
or it could be handled with XSLT and (possibly complex) regular expressions 
or conditionals.

Benefits of this approach could be:

* XML and XSLT processing are built into web browsers.
* Javascript isn't required (but could be used).
* XML schemas could validate the documents using readily available tools
* XML is a commonly used standard.  The developer might already know it;
  otherwise, it may be useful to learn and reuseable knowledge.

Project development roadmap
---------------------------

Accessibility basics
^^^^^^^^^^^^^^^^^^^^
* Add text description to SVG diagram of the dialogue graph that describes the graph structure.
* Add keyboard controls for zooming and panning the SVG image. 
* Maintain the page layout reasonably when the page is scaled with ctrl-+/-.

Core features
^^^^^^^^^^^^^
* Enable a user to reuse existing positions to support or oppose other arguments.
* Enable a user to mark two or more positions as the same or as mutually exclusive (the "Relate" feature).
* Enable a user to add posts to a per-position informal discussion (the "Discuss" feature).
* Implement the betting markets, including the order book, the matchin algorithm, and the ledger of bids and betting contracts.
* Enable the (re-)selling of existing betting contracts.
* Implement detection of inconsistent bids and bets and prevent users from making such.
* Implement detection of inconsistencies in other commitments (as the result of reductio arguments and some "Relate" actions) and enable users to resolve inconsistencies by selling betting contracts.
* Enable topic proposal.
* Enable users to interact on the same dialogues (not only single user sanboxes and simulated multi-user activity).
* Add policy proposals as the initial position type and add a policy evaluation positon type and the other policy decision features.
* (For possible inclusion in the prototype:) Add encryption of anonymous IDs that connect a user to their bids and bets in the ledger.
* (For possible inclusion in the prototype:) Add asymmetric encryption of userids in a registration record to prevent its connection with user login records, as described under :ref:`Design for confidentiality`.  If this is added in the prototype, it will be an optional feature and only use a single public key, not two.

Demo features
^^^^^^^^^^^^^
* Enable deletion of positions.
* Add a guest login option.
* Allow a user to simulate multiple users by selecting the current user from a dropdown menu.

More to be added to this section, including categorizing items as short-, medium-, or long-term and possibly including beyond-the-prototype items, later.


Coding standards
----------------

NOTE: This project is uses typed Python.  The mypy settings are in the
file setup.cfg.  It uses all of the settings from ``mypy --strict``
(as of mypy version 0.812) except ``--disallow-subclassing-any``, which
is not used (especially) since some classes subclass "Persistent" in order
to take advantage of the ZODB database.

The modules may be type-checked using the following command from the
command line from within the main directory of the project:
``mypy allsembly/*.py``.  It should report no errors.

For more information about mypy or about optional type-checking in Python,
see http://mypy-lang.org.

Mypy may be installed with: ``python3.7 -m pip install mypy``.

Settings for Pylint (see https://pylint.org) are also in the setup.cfg file.
With Pylint installed, the modules may be linted by running Pylint from the 
command line as follows:
``pylint --rcfile=setup.cfg allsembly``.

The Pylint settings in setup.cfg correspond to:
``pylint --disable=all -enable F,E,W --disable=python3``.
This will report many warnings, mostly about unused variables and two
errors about imports.  The errors are false positives as far as I can
tell.  The module is successfully using the imported class (OOBTree).
I plan to attend to the warnings.
I also look at the output of the refactoring module even though it 
is disabled in setup.cfg, and I plan to implement some of its refactoring
recommendations.

Guidelines
^^^^^^^^^^
Python:  

* In the server modules, don't use exceptions and don't allow exceptions to escape your functions (it is okay in scripts).  Unhandled exceptions could be the source of unplanned server termination that could affect data integrity or worsen user experience even though the server can be restarted.  I will be reviewing the "returns" Python library to help with this in the future.
* Avoid the use of variables when possible and reasonable and annotate variables as "Final" whenever they do not need to be reused.  Reuse few variables.
* Avoid unnecessary references.  I am considering the "Pysistent" Python library to help with this in the future.
* Make use of the context manager ("with ...:" blocks) for resource managemant.
* Mark private data and functions with a leading underscore (Pylint will catch unintended uses).
* Use all caps for constants (Pylint will catch unintended uses).
* Use docstrings to document all modules, classes, and nontrivial functions.

JavaScript:  

* Use only as much JavaScript as necessary.
* Prefer declarative code to imperative whenever imperative code is not needed to provide a significant advantage.
* Use comments to document all files and nontrivial classes and functions.

Other languages:

Adopt similar guidelines.

Secure coding:  

See the "OWASP Secure Coding Practices Quick Reference Guide" at:  
https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/migrated_content

Choosing library dependencies:  

* Choose the most widely uses and respected libraries for encryption.
* For other purposes, choose more or less production ready libraries.


How it works
------------

For now, see `misc/how_it_works.md <https://github.com/waleedmebane/allsembly-prototype/blob/main/misc/how_it_works.md>`_ in the 
`source code repository <https://github.com/waleedmebane/allsembly-prototype>`_.

Other uses
----------

For example, the software could be adapted to provide a way for writers
to distribute bounties to people who help to improve their writing by
finding shortcomings in the reasoning.  Aside from adapting the code, if one 
wants to use it in such a way, one needs to be cognizant of any laws in one's
jusrisdiction restricting *contests*, including ones that contain an element
of chance.

Individuals or small groups could provide bounties for a recommended resolution
of some disagreement.

Private groups could use it without bounties to deliberate among themselves.
If any money is exchanged, for example, grafting a parimutuel betting scheme
onto the betting market aspect of the software, then one needs to be cognizant
of any laws in one's jusrisdiction restricting *gambling*, and possibly also
laws in the jurisdictions of each of the participants if those are different.

While Allsembly™ as a community is intended to be independent in the sense
of participants choosing their own issues to dialogue about, the software 
could also be adapted for public consultation in which issues and possibly 
some other parameters for the dialogue are decided by the organization seeking 
the policy recommendation to be generated through the dialogue.

It could be used for opinion research in conjunction with opinion polls, 
e.g., by comparing opinion before and after deliberation (as with Deliberative
Polling®) or by comparing the recommendation yielded by deliberation (if any)
with an opinion poll result.

It could be used for argumentation or AI research by mining (only completely anonymous) data, such as for training an artifical agent how to argue or deliberate
based on the activity of the human participants.
