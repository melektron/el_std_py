"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
16.11.24, 13:23
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Code analysis and timing utilities
"""

import time
import functools
import typing



def show_execution_time[T, **P](f: typing.Callable[P, T]) -> typing.Callable[P, T]:
    #@functools.wraps(f)
    def wrapper(*args, **kwargs):
        a = time.perf_counter()
        f(*args, **kwargs)
        rt = time.perf_counter() - a
        print(f"'{f.__name__}' executed in {rt} seconds.")
    return wrapper
    
        