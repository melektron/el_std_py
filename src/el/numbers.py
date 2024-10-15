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

Number = int | float

def linear_map(in_min: Number, in_max: Number, out_min: Number, out_max: Number, in_value: Number) -> Number:
    """
    Maps the number 'in_value' from range 'in_min'...'in_max' to range 'out_min'...'out_max'.
    """
    return ((in_value - in_min) * (out_max - out_min)) / (in_max - in_min) + out_min