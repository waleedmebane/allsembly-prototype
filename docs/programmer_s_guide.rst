Programmer's Guide
==================


Dependencies
------------

Reason for each dependency to be documented.

Apache2

openssl

libapache2-mod-fcgid

graphviz

graphviz-dev

Problog

ZODB

PyGraphviz

json-rpc

Werkzeug

flup

RPyC

persistent

transaction

atomic

readerwriterlock

argon2-cffi

cryptography

python-daemon

d3.js

dialog-polyfill.js

simple-jsonrpc-js.js


Future possible dependencies
----------------------------

Reason for considering each possible future dependency to be documented.

Pydantic

Pyrsistent

returns


Files
-----

Purpose of each file not commonly included in a package to be documented.

COPYING

COPYING.LESSER

LICENSE.txt

requirements.txt

setup.cfg

allsembly/

    allsembly.py

    argument_graph.py

    betting_exchange.py

    common.py

    config.py

    CONSTANTS.py

    demo_default_settings.py

    demo.py

    prob_logic.py

    py.typed

    rpyc_server.py

    speech_act.py

    user.py

docs/

    _build/

    classes.uml

    conf.py

    fdl-1.3.txt

    index.rst

    installation_and_testing.md

    license.rst

    make.bat

    Makefile

    programmer_s_guide.rst

    sequenceDiagram.uml

    user_s_guide.rst

LICENSE.third-party/

misc/

    notes.md

scripts/

    allsembly_add_user.py*

    allsembly_demo.py*

    allsembly_dev_demo.py*

    allsembly-server.py*

    server_config.py

test/


web/

    allsembly_demo_login.xsl

    allsembly_demo.xsl

    scripts/



Specification of requirements (draft)
-------------------------------------

Design overview
---------------
.. uml:: classes.uml

.. uml:: sequenceDiagram.uml

Text to explain the above figures: to be added.

Class detail
------------

For now this section just contains the docstrings from the modules.

**allsembly** module
^^^^^^^^^^^^^^^^
.. automodule:: allsembly.allsembly
   :members:

**rpyc_server** module
^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.rpyc_server
   :members:

**demo** module
^^^^^^^^^^^^^
.. automodule:: allsembly.demo
   :members:

**user** module
^^^^^^^^^^^^^
.. automodule:: allsembly.user
   :members:

**argument_graph** module
^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.argument_graph
   :members:

**prob_logic** module
^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.prob_logic
   :members:

**betting_exchange** module
^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.betting_exchange
   :members:

**speech_act** module
^^^^^^^^^^^^^^^^^^^
.. automodule:: allsembly.speech_act
   :members:



Future design
-------------

User data validation and type safety
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate Typescript function signatures for JSON-RPC and generate HTML5 forms
with "type" fields using a combination of Python and XSLT.
Use Pydantic for basic validation from type hints.

Design for confidentiality
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. image:: images/anonymity_preserving_registration.*


The figure above shows a design with a separate server for login and a separate
server for registration, which could be hosted by different organizations.
The organization hosting the Registration server verifies the new user's
identity but never sees the user's userid or passwors; those are encrypted
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

   #. User connects to the registration server and provides personally identifying information that will be used to verify their identity and provides and a desired userid that is encrypted with a public key of the login server (the Allsembly™ server).  The corresponding private key is stored unencrypted on the login server.  
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

A password may be reset by logging in to the registration server and again 
sending an encrypted userid which is passed on to the login server.  But to
avoid a user being able to reset other users' passwords something special
needs to be done.

There is no way to recover a forgotten userid without revoking anonymity.

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

To provide accountability that the data stored on the server matches the
users' activities, the server should send cryptographically signed receipts
for bids, asks, and betting contract purchases and sales.

The client can store them in local memory and can also store pending
transactions to re-send in case it does not get a confirmation receipt.

Design for scalability
^^^^^^^^^^^^^^^^^^^^^^

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

Coding standards
----------------

NOTE: This project is uses typed Python.  The mypy settings are in the
file setup.cfg.  It uses all of the settings from mypy --strict
(as of mypy version 0.812) except --disallow-subclassing-any, which
is not used (especially) since some classes subclass "Persistent" in order
to take advantage of the ZODB database.

The modules may be type-checked using the following command from the
command line from within the main directory of the project:
`mypy allsembly/*.py`.  It should report no errors.

For more information about mypy or about optional type-checking in Python,
see http://mypy-lang.org.

Mypy may be installed with: `python3.7 -m pip install mypy`.

Settings for Pylint (see https://pylint.org) are also in the setup.cfg file.
With Pylint installed, the modules may be linted by running Pylint from the 
command line as follows:
`pylint --rcfile=setup.cfg allsembly`.

The Pylint settings in setup.cfg correspond to:
`pylint --disable=all -enable F,E,W --disable=python3`.
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



How it works
------------
