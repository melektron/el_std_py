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

import sys
import asyncio
import functools
from typing import Callable, Any, Coroutine
from typing_extensions import ParamSpec
import multiprocessing.connection as mpc


_running_bg_tasks = set()

P = ParamSpec('P')

# https://stackoverflow.com/a/71031698
# https://stackoverflow.com/a/71956673
def synchronize(coro_fn: Callable[P, Coroutine[Any, Any, Any]]) -> Callable[P, None]:
    """
    Decorator that converts an async coroutine into a function that can be
    called synchronously ans will run in the background without needing
    to worry about task references.
    """
    @functools.wraps(coro_fn)
    def inner(*args, **kwargs):
        task = asyncio.create_task(coro_fn(*args, **kwargs))
        _running_bg_tasks.add(task) # keep reference as long as it runs
        task.add_done_callback(lambda t: _running_bg_tasks.remove(t))
    
    return inner


def create_bg_task[T_R](coro: Coroutine[Any, Any, T_R]) -> asyncio.Task[T_R]:
    """
    Creates an asyncio task that is kept alive by a reference
    in an internal set, even if the returned task object
    is not stored anywhere else. This is usefull if you just want
    to start some process without wanting to keep track of it.
    """
    task = asyncio.create_task(coro)
    _running_bg_tasks.add(task)
    task.add_done_callback(lambda t: _running_bg_tasks.remove(t))
    return task


async def async_mpc_pipe_recv[RT](reader: "mpc.Connection[Any, RT]", timeout: float | None = None) -> RT:
    """async with asyncio.timeout(timeout):
        await asyncio.sleep(10)
        return """
    """
    Asynchronously ready from a multiprocessing.Pipe Connection object,
    asynchronously pausing the task until data is available to read.

    Inspiration: https://stackoverflow.com/a/62098165
    
    :returns: The received data

    Parameters
    ----------
    reader : multiprocessing.connection.Connection
        readable connection object to attempt to read data from
    timeout : float | None, optional
        Timeout when waiting for data, by default None. None means no timeout.

    Returns
    -------
    Any
        Received data

    Raises
    -------
    TimeoutError
        Timeout waiting for received data
    """    
    if sys.platform == 'win32':
        async with asyncio.timeout(timeout):
            while not reader.poll():
                await  asyncio.sleep(0.01)

        return reader.recv()

    else:
        data_available = asyncio.Event()
        asyncio.get_event_loop().add_reader(reader.fileno(), data_available.set)

        async with asyncio.timeout(timeout):
            while not reader.poll():
                await data_available.wait()
                data_available.clear()

        return reader.recv()
    

class ResetSemaphore(asyncio.Semaphore):
    """A Semaphore implementation that can be reset.

    A semaphore manages an internal counter which is decremented by each
    acquire() call and incremented by each release() call. The counter
    can never go below zero; when acquire() finds that it is zero, it blocks,
    waiting until some other thread calls release().
    By using the reset() method, the counter can immediately be reset to zero
    or another specified value.

    Semaphores also support the context management protocol.

    The optional init argument gives the initial value for the internal
    counter; it defaults to 1. If the value given is less than 0,
    ValueError is raised.
    """
    def __init__(self, value=1):
        super().__init__(value)
    
    def reset(self, value: int = 0) -> None:
        """ Resets the internal counter to the provided value """
        self._value = value