I discuss two topics below, "Allsembly" as a trademark (together with the 2nd
additional term of the license) and wanting to add a static linking exception
as a third additional term.  Each has been given a separate heading.  Also
note that the software's license is LGPL verion 3 only (not "or later versions")
plus the additional terms.

# Trademark

Making "Allsembly" a trademark is not intended to prevent the use of the
name, even as a part of the names of other software products.  It is intended
to prevent its use in ways that cause confusion of those other pieces of 
software with this one.  If another piece of software actually implements
Allsembly, e.g., by fulfilling all of the spec. requirements (not published
yet), then I wouldn't mind it being called "Allsembly".  I would not want it
to be misrepresented as the one and only Allsembly, though, as long as this
project exists, and especially if that other is not Free and Open Source (FOSS)
software.  This might become important if the name "Allsembly" comes to have
some currency, such as being mentioned in articles or blog posts. 

Here are some examples to illustrate reasonable uses:

1) There are free software projects, _Keepass 2_, _KeepassX_, and _KeepassXC_.
They all do basically the same thing--password management--with some variation 
and they are all FOSS.  Keepass 2 uses _Mono_ to make it cross-platform.  
KeepassX uses the Keepass 2  database format, but runs natively under X Windows
for Unix-like OSes and doesn't rely on Mono.  KeepassXC moves KeepassX in new
directions since KeepassX development had slowed or its project maintainers 
wanted to be more conservative about feature additions.  This is all fine.
They could improve the situation by all having links to the other projects to
help the user choose the implementation that is best for them.

2) A couple of decades ago or so, Apple Computer licensed the name "Macintosh"
to Hewlett Packard (HP) so HP could manufacture a Mac branded computer.  I 
don't believe they ever did, but one could imaging that Apple would have 
conditioned it on HP meeting certain technical standards so that their brand
would not be tarnished by poor user experience on an HP engineered and
manufactured Mac.

The second addtional term of the software license is not intended to place
additional obligations on licensees of the software other than what trademark
law already requires.  It is just to clarify that the license doesn't extend
to trademarks.  (And it is the name of the software project, "Allsembly",
that I had particularly in mind.)
In the future, I hope to add a free trademark license to make that explicit.

It is not a pressing need, and it can wait until I am finished with
graduate studies and have a full-time job.  Then I expect I will hire legal
help to draft it.

# Static linking exception

I would like to add a linking exception allowing distribution of "Combined
Works" (see section 4 of the LGPL) without source code for the part that only
links with Allsembly code, without being "based on" it (which, in the sense
given by the LGPL means onlly calling its function or subclassing its classes).

I like the LGPL as a good weak copyleft license.  My goals in using it are
a little different from those of the Free Software Foundation (FSF).  I'm 
interested in a license that encourages widespread use, even commercial use
in proprietary software, which requiring that modifications be given back to
the community in source code form.  I also very much like the LGPLs provisions
about giving "prominent notice" so distributors of the sofware and its
derivatives may not represent a proprietary version as the only one but must
make users aware of a free alternative.

But the provision requiring that the combined version be able to be re-linked
with "the Library" (this project's functions and classes) and that its terms
allow reverse engineering might be an unnecessary deterrent to
use in proprietary products.  (I think users should be able to modify 
their software, but trying to ensure that through copyright is a lesser 
priority for me for this particular project.)

You might be thinking that it would be best for all implementations of 
Allsembly (as a community of public policy deliberators) to be open source
for transparency to its users--i.e., to enable maximum trust in the integrity
of the process.  That is true, but there are other uses of the software such
as for internal deliberations inside of companies and other organizations or
to get feedback from users about products or services.

If a company makes a proprietary product to sell to organizations for those
purposes, they might contribute back source code useful for the free software
project.  And it is also possible that it generates good publicity.  If they
make a proprietary competitor to the FOSS version(s), at least free version(s)
still exist.

Below is the draft language I am considering.  Although I am aware that legal
issues can be subtle and might require deep knowledge of relevant law, and I
am not a lawyer, I will probably add the additional term before consulting
a lawyer to avoid complications of having code in the project under two 
different licenses.  But I will wait a little while to get some feedback.
The addition can wait until there are pull requests from
other potential contributors.

> Linking Exception.  As an exception to Section 4 of the LGPL, the copyright holders of this software give you permission to convey a Combined Work under the terms of your choice [the first part of Section 4 without "that... do not restrict modification... and reverse engineering for debugging..."] provided you meet the requirements listed as (a) - (c) under Section 4 and that you convey the Minimum Corrresponding Source [as required by 4 (d)] but without the need to convey the Corresponding Application Code.  This exception does not invalidate any other reason why your software might be covered by the LGPL or the GPL; and it does not alter any license term of any work that is part of the Application combined with the Library even if one or more copyright holders of the Library are also incidentally copyright holders of those works.  You must still adhere to all of the license terms of any other works you link with the Library.

> It is the intention of the copyright holders that the exception given in Section 1 of the LGPL still apply if it otherwise would have applied by your meeting the terms of Section 4 without the above addtional exception.

> It is the intention of the copyright holders that they or their agents be permitted to disassemble or reverse engineer the Combined Work for the purpose of determining compliance with the license terms but that the terms under which you convey the Combined Work need not be compatible with disassembly or reverse engineering, as mentioned in Section 4 of the LGPL, for any other purpose.

Note:  I don't say anything about "static linking" because I don't intend to 
restrict the means of linking or combining.  They can cut and paste if they 
want. The LGPL is clear even in such a case that if their code does more with 
"the Library" than call its functions and subclass its classes, then such code
would be "based on" "the Library" rather than just based on "the Application" 
and need to be conveyed as "Minimum Corresponding Source" (i.e., what I've 
called, above, "contributing back").  The exception excludes LGPL Section 4(e)
(the requirement to provide installation information) because it might be interpretted to require that the user be able to modify the Combined Work (see, e.g.,
https://www.gnu.org/licenses/gpl-faq.html#RemoteAttestation).
