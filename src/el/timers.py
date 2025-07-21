"""
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
25.07.23, 21:30
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Various asynchronous timers:
 - resettable watchdog/countdown timer
 - interval timer

For these timers to work, an asyncio loop must be running
"""

import typing
import asyncio
import functools

type TimerCallback = typing.Callable[[], typing.Coroutine]

class _BaseTimer:
    def _run_callback(self, cb: TimerCallback | None):
        if cb is not None:
            asyncio.create_task(cb())


class WDTimer(_BaseTimer):
    def __init__(self, timeout: float) -> None:
        """
        Watchdog timer that continuously down from the time
        specified in timeout and but can be reset to the start at any time
        using the refresh() method.
        If the timer reaches zero (timeout) it fires a callback.
        When the timer is restarted the first time after reaching zero using refresh()
        (or the first time it this method is called) a restart callback fires.

        timeout: time to count down for in seconds
        """
        self._timeout: float = timeout
        self._timer_task: asyncio.Task = None
        self._on_timeout_cb: TimerCallback = None
        self._on_restart_cb: TimerCallback = None

    def on_timeout(self, cb: TimerCallback):
        """
        Registers a callback handler (must be async) for the timeout event
        (aka. when the timer isn't refreshed before the timeout time.)

        Note: There can only be one callback, registering a second one
        overwrites the first one.
        """
        self._on_timeout_cb = cb

        return self

    def on_restart(self, cb: TimerCallback):
        """
        Registers a callback handler (must be async) for the restart event
        (aka. when the timer restarts counting after a timeout or
        on initial start)

        Note: There can only be one callback, registering a second one
        overwrites the first one.
        """
        self._on_restart_cb = cb

        return self

    def refresh(self):
        """
        Resets the timer so it starts counting all over again if it is already
        counting and starts it if it has finished counting down or is started
        the first time.
        This causes restart callback to run if the timer isn't running
        at the time of calling.
        """

        # first start
        if self._timer_task is None:
            self._run_callback(self._on_restart_cb)
            self._timer_task = asyncio.create_task(self._timer_fn())

        # after timeout
        elif self._timer_task.done():
            self._run_callback(self._on_restart_cb)
            self._timer_task = asyncio.create_task(self._timer_fn())

        # while it is still running
        else:
            self._timer_task.cancel()
            self._timer_task = asyncio.create_task(self._timer_fn())
        
        return self

    @property
    def active(self) -> bool:
        """
        whether the timer is currently actively counting
        or not (because it has timed out or hasn't been started)
        """
        return self._timer_task is not None and not self._timer_task.done()

    async def _timer_fn(self):
        await asyncio.sleep(self._timeout)
        self._run_callback(self._on_timeout_cb)
    
    def __del__(self):
        if self._timer_task is None:
            return self
        self._timer_task.cancel()
        self._timer_task = None



class IntervalTimer(_BaseTimer):
    def __init__(self, period: float) -> None:
        """
        Timer that calls a coroutine continuously with a set period

        period: interval period in seconds
        """
        self._period: float = period
        self._timer_task: asyncio.Task = None
        self._on_interval_cb: TimerCallback = None

    def on_interval(self, cb: TimerCallback, *args, **kwargs):
        """
        Registers a callback handler (must be async) for the timer interval event.

        Note: There can only be one callback, registering a second one
        overwrites the first one.

        returns self
        """
        self._on_interval_cb = functools.partial(cb, *args, **kwargs)

        return self

    def start(self):
        """
        Starts the timer. The fist callback will happen after the set period.
        If the timer is already running, it will be stopped and restarted.

        returns self
        """

        # first start
        if self._timer_task is None:
            self._timer_task = asyncio.create_task(self._timer_fn())

        # while it is still running
        else:
            self._timer_task.cancel()
            self._timer_task = asyncio.create_task(self._timer_fn())
        
        return self

    def stop(self):
        """
        returns self
        """
        if self._timer_task is None:
            return self
        self._timer_task.cancel()
        self._timer_task = None

        return self

    async def _timer_fn(self):
        await asyncio.sleep(self._period)
        self._run_callback(self._on_interval_cb)
        self._timer_task = asyncio.create_task(self._timer_fn())

    def __del__(self):
        self.stop()
