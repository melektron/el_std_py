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
import warnings

from el.timers import WDTimer
from ._observable import Observable, ObserverFunction, StatefulFilter
from el.numbers import clamp

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



class on_edge[T](StatefulFilter[T, T]):
    def __init__(
        self, *,
        rising: typing.Callable[[T], None] | None = None,
        falling: typing.Callable[[T], None] | None = None,
        criterion: typing.Callable[[T], bool] = bool
    ):
        """
        Detects edges in observable value changes.
        Calls the provided callback `rising` on the rising
        edge of observable values, and `falling` on the
        falling edge.
        For non-binary value types, a custom `criterion` can be
        defined to determine the binary state of the value.

        In an observer chain, this filter simply forwards it's
        value to the next observer without filtering or modification.

        Parameters
        ----------
        rising : typing.Callable[[T], None] | None, optional
            callback to invoke on rising, by default None
        falling : typing.Callable[[T], None] | None, optional
            callback to invoke on falling edte, by default None
        criterion : typing.Callable[[T], bool], optional
            criterion to determine the binary state of non binary values, by default bool()
        """

        self._rising = rising
        self._falling = falling
        self._criterion = criterion

        self._previous_state: bool = ...

    @typing.override
    def __call__[CT](self, v: CT) -> CT:
        state = self._criterion(v)

        if self._previous_state != state and self._previous_state is not ...:
            if state == True and self._rising is not None:
                self._rising(v)
            elif state == False and self._falling is not None:
                self._falling(v)
        
        self._previous_state = state
        return v


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
        return clamp(v, min_value, max_value)
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
        # postponing mode
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


class debounce[T](StatefulFilter[T, T]):
    def __init__(
        self,
        window: float,
        to_bool: typing.Callable[[T], bool] = bool,
        postpone_updates: bool = True,
    ):
        """
        Causes a value update to be propagated only after it has been
        in the same state as determined by `to_bool` for at least 
        `window` seconds.

        This is mostly used with boolean or binary data, but can be used
        with other values by providing a custom function `to_bool` to determine
        a binary state according to a custom criterion.
        
        Unlike the `throttle` filter, as long as the input value 
        changes with shorter than `window` intervals, no updates will be 
        propagated whatsoever. The value update will happen asynchronously
        after the value state has not changed within `window` seconds.
        This behavior requires an active asyncio event loop 
        to dispatch the postponed settled values. Set `postpone_updates` to 
        False to disable this behavior. In that case, updates will only be
        propagated synchronously with incoming updates, which, in case of boolean
        values, only occur when force-propagated. This mode is more useful for other
        data that changes more frequently in value but not in the determined
        debouncing state.
        """
        self._window = window
        self._to_bool = to_bool

        self._previous_state: bool = ...
        if postpone_updates:
            self._change_timer = WDTimer(self._window)
            self._change_timer.on_timeout(self._on_timeout)
            self._last_change_time = None
        else:
            self._change_timer = None
            self._last_change_time = 0
    
    @property
    def window(self) -> float:
        return self._window
    
    @window.setter
    def window(self, window: float) -> None:
        """Changes the debouncing window after the fact"""
        self._window = window
        if self._change_timer is not None:
            self._change_timer.timeout = window

    @typing.override
    def _connect(self, src, dst):
        self._src_obs = src
        self._dst_obs = dst

    @typing.override
    def __call__[CT](self, v: CT) -> CT:
        # determine binary state from value
        state = self._to_bool(v)
        
        # non-postponing mode
        if self._last_change_time is not None:
    
            # On initial update or if the value has changed, we just save that,
            # reset the timeout and don't propagate
            if self._previous_state != state:
                self._previous_state = state
                self._last_change_time = time.time()
                return ...
            
            else:
                # value has stayed the same, if it's been like this for long enough
                if time.time() > (self._last_change_time + self._window):
                    return v    # propagate update, this can happen multiple times now until the state changes
                else:
                    return ...  # inhibit update, need to wait a bit longer
        
        # postponing mode
        elif self._change_timer is not None:

            # On initial update or if the value has changed, we just save that,
            # refresh the timer and don't propagate
            if self._previous_state != state:
                self._previous_state = state
                self._change_timer.refresh()
                return ...
            
            else:
                # value has stayed the same, if it's been like this for long enough 
                # (aka. if timer is no longer active)
                if not self._change_timer.active:
                    return v    # propagate update, this can happen multiple times now until the state changes
                else:
                    return ...  # inhibit update, need to wait a bit longer
        
    async def _on_timeout(self) -> None:
        src_obs = self._src_obs()
        dst_obs = self._dst_obs()
        if src_obs is not None and dst_obs is not None:
            # propagate postponed update
            dst_obs.value = src_obs.value