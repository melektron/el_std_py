"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 12:09
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Common filter and transform functions for observables
"""

import typing
import time

from el.timers import WDTimer
from ._observable import Observable, ObserverFunction, StatefulFilter

def if_true[T](v: T) -> T:
    """
    Propagates only values that are equal to True
    when converted to boolean:
    ```python 
    bool(v) == True 
    ```
    Values that do not meet this requirement are filtered out.
    """
    if bool(v) == True:
        return v
    else:
        return ...
    
def call_if_true(
    t: typing.Callable, 
    f: typing.Callable | None = None
) -> ObserverFunction[typing.Any, None]:
    """
    Calls the provided function `t` when the observable changes it's
    value to equal true when converted to bool.
    ```python 
    bool(v) == True 
    ```
    If the optional `f` argument is provided, it is called when
    the value changes to equal false:
    ```python
    bool(v) == False
    ```
    If `f` is not provided, such value changes are ignored.
    """
    def obs(v: typing.Any) -> None:
        if bool(v) == True:
            t()
        else:
            if f is not None:
                f()
    return obs


def limits[T](
    min_value: T | None = None,
    max_value: T | None = None
) -> ObserverFunction[T, T]:
    """
    Clamps the range of a (typically numerical) value
    to between `min_value` and `max_value` (inclusive).
    If one of the limits is None, not limit is enforced
    on that end. 
    
    It is to note that this doesn't block 
    update propagation if the limit is breached, instead
    emitting the clamped value. Should the filter be called
    with an empty value (...), the event is not clamped but instead
    blocked.
    """
    def limiter(v: T) -> T:
        if v == ...:
            return v
        if min_value is not None and v < min_value:
            return min_value
        if max_value is not None and v > max_value:
            return max_value
        return v
    return limiter


def ignore_errors[I, O](
    handler: ObserverFunction[I, O],
) -> ObserverFunction[I, O]:
    """
    wraps the observer function `handler` within
    a try-except block. If an exception occurs,
    ellipsis is returned (i.e. update is absorbed)
    """
    def obs(v: I) -> O:
        try:
            return handler(v)
        except:
            return ...
    return obs


class throttle[T](StatefulFilter[T, T]):
    @typing.overload
    def __init__(self, *, hz: float, postpone_updates: bool = True):
        """
        Throttles the update rate to a maximum of `hz` Hz.
        
        Quick bursts of updates will not be propagated
        immediately, instead being postponed and propagated 
        as one cumulative update after the minimum interval according
        to the configured maximum frequency. This is to prevent permanent 
        steady-state error after a burst of quick updates. 
        This behavior requires an active asyncio event loop 
        to dispatch the postponed settled values. Set `postpone_updates` to 
        False to disable this behavior.
        """
    
    @typing.overload
    def __init__(self, *, interval: float, postpone_updates: bool = True):
        """
        Throttles the update rate to a minimum of `interval` seconds
        between updates.
        
        Quick bursts of updates will not be propagated
        immediately, instead being postponed and propagated 
        as one cumulative update after the minimum interval.
        This is to prevent permanent steady-state error 
        after a burst of quick updates. 
        This behavior requires an active asyncio event loop 
        to dispatch the postponed settled values. Set `postpone_updates` to 
        False to disable this behavior.
        """
    
    def __init__(
        self, *,
        hz: float | None = None, 
        interval: float | None = None,
        postpone_updates: bool = True,
    ):
        if hz is None and interval is not None:
            self._interval = interval
        elif interval is None and hz is not None:
            self._interval = 1 / hz
        else:
            raise ValueError("Either max. update rate (hz) or min. interval (interval) must be passed to throttle()")

        if postpone_updates:
            self._update_timer = WDTimer(self._interval)
            self._update_timer.on_timeout(self._on_timeout)
            self._last_update_time = None
        else:
            self._update_timer = None
            self._last_update_time = 0

    @typing.override
    def _connect(self, src, dst):
        self._src_obs = src
        self._dst_obs = dst

    @typing.override
    def __call__[CT](self, v: CT) -> CT:

        # non-postponing mode
        if self._last_update_time is not None:
            if time.time() > (self._last_update_time + self._interval):
                self._last_update_time = time.time()
                return v    # propagate update
            else:
                return ...  # inhibit update
        # non-postponing mode
        elif self._update_timer is not None:
            # if the timer is not active we propagate immediately,
            # otherwise we wait for timeout to propagate cumulative update
            if not self._update_timer.active:
                self._update_timer.refresh()
                return v    # propagate update
            else:
                return ...  # inhibit update

    async def _on_timeout(self) -> None:
        src_obs = self._src_obs()
        dst_obs = self._dst_obs()
        if src_obs is not None and dst_obs is not None:
            if src_obs.value != dst_obs.value:
                # propagate a postponed cumulative update
                # if the value has changed
                dst_obs.value = src_obs.value
                # and go into another throttle delay
                self._update_timer.refresh()