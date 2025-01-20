"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
19.01.25, 19:40
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Some of this code is inspired by StackOverflow
"""

import typing
from itertools import groupby


# https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-equal
def all_equal(iterable: typing.Iterable) -> bool:
    g = groupby(iterable)
    return next(g, True) and not next(g, False) # check for exactly one result