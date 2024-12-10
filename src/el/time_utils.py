"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
06.12.24, 15:26
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Utilities for working with the time module
"""

import math
import datetime

def floor_to_ms(t: datetime.datetime) -> datetime.datetime:
    return t.replace(microsecond=min(((t.microsecond // 1000) * 1000), 999999))

def ceil_to_ms(t: datetime.datetime) -> datetime.datetime:
    return t.replace(microsecond=min((math.ceil(t.microsecond / 1000) * 1000), 999999))