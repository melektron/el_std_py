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