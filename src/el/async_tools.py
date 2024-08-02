"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
12.07.24, 16:20
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Utilities for working with asyncio (I wish some of these were in stdlib)
"""

import asyncio
import functools
from typing import Callable, Any, Coroutine
from typing_extensions import ParamSpec


_running_bg_tasks = set()

P = ParamSpec('P')

# https://stackoverflow.com/a/71031698
# https://stackoverflow.com/a/71956673
def synchronize(coro: Callable[P, Coroutine[Any, Any, Any]]) -> Callable[P, None]:
    """
    Decorator that converts an async coroutine into a function that can be
    called synchronously ans will run in the background without needing
    to worry about task references.
    """
    @functools.wraps(coro)
    def inner(*args, **kwargs):
        task = asyncio.create_task(coro(*args, **kwargs))
        _running_bg_tasks.add(task) # keep reference as long as it runs
        task.add_done_callback(lambda t: _running_bg_tasks.remove(t))
    
    return inner

