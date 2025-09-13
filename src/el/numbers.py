"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
15.10.24, 16:23
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Mathematical utilities, things that interact with numbers
"""

import typing

type Number = int | float

def linear_map(in_min: Number, in_max: Number, out_min: Number, out_max: Number, in_value: Number) -> Number:
    """
    Maps the number 'in_value' from range 'in_min'...'in_max' to range 'out_min'...'out_max'.
    """
    return ((in_value - in_min) * (out_max - out_min)) / (in_max - in_min) + out_min

def clamp[T](
    v: T,
    min_value: T | None = None,
    max_value: T | None = None,
) -> T:
    """
    Clamps the range of a (typically numerical) value
    to between `min_value` and `max_value` (inclusive).
    If one of the limits is None, not limit is enforced
    on that end. 

    Parameters
    ----------
    v : T
        Value to clamp. This can be any value
        that supports the > and < operators.
    min_value : T | None, optional
        Optional minimum value , by default None
    max_value : T | None, optional
        Optional maximum value, by default None

    Returns
    -------
    T
        The clamped value
    """
    if min_value is not None and v < min_value:
        return min_value
    if max_value is not None and v > max_value:
        return max_value
    return v