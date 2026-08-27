Allsembly™ Prototype
====================

This software will be for creating an online community for anonymous proposal and collaborative evaluation of public policy options, with automated decision support.

[![Ceasefire Now](https://badge.techforpalestine.org/ceasefire-now)](https://techforpalestine.org/learn-more)

It will make use of betting markets and probabilistic inference.
Some additional explanation may be found in the _Introduction_ section of the 
documentation, in docs/notes.md, and in misc/prospectus.pdf.

Only about half of the major features have been added, so far.

The documentation is currently hosted at https://waleedmebane.github.io/allsembly-docs/ .
You may also generate the documentation from the files in the docs
subdirectory using the documentation creation tool, Sphinx
(https://www.sphinx-doc.org/).

I do not expect to develop the prototype further until Summer or later.

I intend to make future updates on Codeberg instead of Github in order to avoid the use of Microsoft products due to ethical concerns highlighted in a [June 2025 UN special rapporteur report](https://afsc.org/newsroom/unprecedented-investor-action-demands-microsoft-answer-reported-involvement-gaza-genocide) and concerns [highlighted by some Microsoft employees](https://noazureforapartheid.com/). I will add a link here to the new repository after it is created.

## License

Please find the license terms in the file: LICENSE.txt.
The license is LGPLv3-only with three additional terms: 1) disallowing using the
authors' names and likenesses; 2) declining to grant license to use trademarks; 
and 3) providing additional permission for static linking.

The Javascript libraries "d3", "dialog-polyfill", and "jquery"
are included with this software in the sub-directory:
web/scripts

Their license terms and copyright notices are in files in the sub-directory:
LICENSE.third-party.  The respective license terms file has its
suffix named after the name of the library.  They are under permissive,
BSD and MIT, license terms.

Installation
------------

Installation directions are in the file:
docs/installation_and_testing.md

Code of conduct for contributors
--------------------------------

This project currently has only one contributor; therefore, I have not yet adopted a code of conduct. If enough people express interest in contributing, I expect to adopt a code of conduct based on the [Contributor Covenant 3.0 Code of Conduct](https://www.contributor-covenant.org/version/3/0/code_of_conduct/), with appropriate interpretation and enforcement guidelines that are manageable for a small group.

## Contributing

I haven't written a guide to contributing, yet. A good way to understand the code could be to read the "Programmer's Guide" section of the documentation. Besides the open issues, there is a preliminary development roadmap there. Formal specification of part of the system is available in my recently published dissertation. I plan to add it to the repository when I move it to Codeberg. The dissertation contains an important erratum that I will also document at that time (in a nutshell, in Definition 12, on page 155 and elsewhere where it is quoted, the sentence defining "undefeated arguments" should removed and "undefeated" replaced with "justified" in the following sentence so that the recursion always teminates).
I've been slow at moving the repository to Codeberg, which is where I intend to house further development; however, if you have an idea, feel free to open an issue or pull request. For now, please do not use LLMs to write your issues or pull requests (text or code). For now, please do not submit the code to be analyzed by LLM-based systems. Please try to follow the spirit of the Contributor Covenant Code of Conduct to the best of your understanding. Please use a separate issue or pull request for each concern, and keep them tightly scoped. Thank you for your interest in the project!
