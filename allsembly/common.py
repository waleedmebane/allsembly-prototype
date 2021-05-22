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

from typing import TypeVar, Generic
from typing_extensions import Final

T = TypeVar('T')
class FinalVar(Generic[T]):
    """ *DEPRECATED: to be removed in a future version
    This was intended as a solution to Final not being
    able to be declared inside of loops.
    Create a new instance of this class
    inside of the loop.

    *Deprecated:
    The problem is actually that loops do not have a separate
    scope.  For example, in C++, I can write:
    for (i=0; i<10; ++i) {
        const int j = 1;
        ...
    }
    "j" is a new variable each time through the loop.

    This class, FinalVar, doesn't actually solve the problem.
    The FinalVar variable can still be re-bound, but the likely
    absence of a "get()" method on the new bound object would
    produce a runtime error and a static-checker error.

    Instead of using FinalVar, the problem could be solved with
    a function that contains the body of the loop.  For example:

    def _loop_body(...) -> ...:
        j: Final[int] = 1
        #do something and possible return some value

    for i in range(10):
        _loop_body(...)

    A similar limitation exists with try blocks.
    Since they don't create a scope, conveniently, I can define
    new variables there to use outside of their blocks (which I
    wouldn't be able to do with, e.g., C++), but
    I can't assign different values to them conditionally and
    also have them be Final.

    For example:

    try:
        my_int: Final[Optional[int]] = int('a')
    except ValueError:
        my_int: Final[Optional[int]] = None

    The code above produces a type-checker error because my_int is
    re-bound.  An alternative is:

    def optional_int(x: Any, base: int = 10) -> Optional[int]:
        try:
            return int(x, base)
        except ValueError:
            return None

    my_int: Final[Optional[int]] = optional_int('a')

    For the case of if statements, substitute if expressions or
    use the same method as with try blocks.
    """
    def __init__(self, in_val: T):
        self._value: Final[T] = in_val

    def get(self) -> T:
        return self._value

