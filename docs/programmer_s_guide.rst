Programmer's Guide
==================


Dependencies
------------



Future possible dependencies
----------------------------


Files
-----

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

Design for confidentiality
^^^^^^^^^^^^^^^^^^^^^^^^^^

Design for integrity
^^^^^^^^^^^^^^^^^^^^

Design for scalability
^^^^^^^^^^^^^^^^^^^^^^

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

How it works
------------
