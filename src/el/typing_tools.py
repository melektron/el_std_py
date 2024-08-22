"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
12.08.24, 16:22
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

utility functions for typing
"""

import typing


def get_origin_always(tp) -> type:
    """
    Always returns the type origin, removes subscripts if there
    are any or returns the same type otherwise.
    """
    if (o := typing.get_origin(tp)) is not None:
        return o
    return tp


class ReassignGuard[T]:
    def __set_name__(self, owner, name: str) -> None:
        self._public_name = name
        self._private_name = "rg_" + name   # add some characters in front of _ so private attributes don't accidentally end up starting with two underscores
    
    def __get__(self, obj, objtype=None) -> T:
        return getattr(obj, self._private_name)
    
    def __set__(self, obj, value: T) -> None:
        if hasattr(obj, self._private_name):    # assign only the first time
            raise AttributeError(f"Re-assignment of {obj.__class__.__name__}.{self._public_name} is prohibited")
        setattr(obj, self._private_name, value)
