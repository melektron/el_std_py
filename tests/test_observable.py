"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 01:01
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

tests for el.datastore
"""


import pytest
import typing
import logging
import asyncio

from el.observable import Observable
from el.observable.filters import *

_log = logging.getLogger(__name__)


def test_observer_rshift():
    obs = Observable[int](0)
    observer_result = ...
    def observer(v: int):
        nonlocal observer_result
        observer_result = v
    obs >> observer
    
    assert obs.value == 0
    assert observer_result == 0, "must be changed by initial update"
    obs.value = 2
    assert obs.value == 2
    assert observer_result == 2
    
def test_observer_observe():
    obs = Observable[int](0)
    observer_result = ...
    def observer(v: int):
        nonlocal observer_result
        observer_result = v
    
    obs.observe(observer)
    
    assert obs.value == 0
    assert observer_result == 0, "must be changed by initial update"
    obs.value = 2
    assert obs.value == 2
    assert observer_result == 2

def test_no_initial_update_when_empty():
    obs = Observable[int]()
    observer_result = 5
    def observer(v: int):
        nonlocal observer_result
        observer_result = v
    obs >> observer
    
    assert obs.value == ...
    assert observer_result == 5, "must not be changed by initial update because observable was empty"
    obs.value = 2
    assert obs.value == 2
    assert observer_result == 2


def test_lshift_chaining():
    obs = Observable[int](0)
    chained_obs = Observable[int]()

    chained_observer_result = ...
    def chained_observer(v: int):
        nonlocal chained_observer_result
        chained_observer_result = v
    
    # add chained observer
    chained_obs >> chained_observer
    assert obs.value == 0
    assert chained_obs.value == ...
    assert chained_observer_result == ...,  "must not be changed by initial update"
    
    # chaining observables
    chained_obs << obs
    assert obs.value == 0
    assert chained_obs.value == 0
    assert chained_observer_result == 0,  "initial value must propagate all the way"
    
    # value propagation after chaining
    obs.value = 2
    assert obs.value == 2
    assert chained_obs.value == 2
    assert chained_observer_result == 2,  "update must propagate all the way"
    
    # chaining only works with observables
    with pytest.raises(TypeError):
        obs << chained_observer

def test_receive():
    """ receive chaining should behave the same as lshift chaining """

    obs = Observable[int](0)
    chained_obs = Observable[int]()

    chained_observer_result = ...
    def chained_observer(v: int):
        nonlocal chained_observer_result
        chained_observer_result = v
    
    # add chained observer
    chained_obs >> chained_observer
    assert obs.value == 0
    assert chained_obs.value == ...
    assert chained_observer_result == ...,  "must not be changed by initial update"
    
    # chaining observables
    obs >> chained_obs.receive
    assert obs.value == 0
    assert chained_obs.value == 0
    assert chained_observer_result == 0,  "initial value must propagate all the way"
    
    # value propagation after chaining
    obs.value = 2
    assert obs.value == 2
    assert chained_obs.value == 2
    assert chained_observer_result == 2,  "update must propagate all the way"


def test_derived_observable():
    obs = Observable[int](0)
    observer_result = ...
    def observer(v: int):
        nonlocal observer_result
        observer_result = v
    observer_result2 = ...
    def observer2(v: int):
        nonlocal observer_result2
        observer_result2 = v
    
    derived_obs = obs >> (lambda v: v * 2)
    assert isinstance(derived_obs, Observable)
    derived_obs >> observer

    # inline deriving syntax must also work
    obs >> (lambda v: v * 3) >> observer2
    
    assert obs.value == 0
    assert derived_obs.value == 0
    assert observer_result == 0
    assert observer_result2 == 0
    obs.value = 2
    assert obs.value == 2
    assert derived_obs.value == 4, "derived observable must have function applied"
    assert observer_result == 4
    assert observer_result2 == 6


def test_filter_if_true():
    obs = Observable[int]()
    observer_result = 5
    call_count = 0
    def observer(v: int):
        nonlocal observer_result, call_count
        observer_result = v
        call_count += 1
    
    obs >> if_true >> observer
    
    assert observer_result == 5, "must not yet be modified"
    assert call_count == 0
    obs.value = 2
    assert observer_result == 2, "truthy value must be propagated"
    assert call_count == 1
    obs.value = 0
    assert observer_result == 2, "falsy value must not be propagated"
    assert call_count == 1
    obs.value = 4
    assert observer_result == 4, "truthy value must be propagated"
    assert call_count == 2

def test_call_if_true():
    obs = Observable[int]()
    call_count = 0
    def cb():
        nonlocal call_count
        call_count += 1
    obs >> call_if_true(cb)
    
    obs.value = 2
    assert call_count == 1, "truthy value must cause cb"
    obs.value = 0
    assert call_count == 1, "falsy value must not cause cb"
    obs.value = 4
    assert call_count == 2, "truthy value must cause cb"


async def throttle_timing_check(tr: throttle):
    obs = Observable[int]()
    observer_result = ...
    call_count = 0
    def observer(v: int):
        nonlocal observer_result, call_count
        observer_result = v
        call_count += 1
    obs >> tr >> observer
    
    # burst of multiple calls should be postponed
    obs.value = 2
    assert observer_result == 2, "single update should happen immediately"
    assert call_count == 1
    await asyncio.sleep(0.01)
    obs.value = 3
    await asyncio.sleep(0.01)
    obs.value = 4
    await asyncio.sleep(0.07)
    assert observer_result == 2, "after 90ms the value should not yet have been updated"
    assert call_count == 1
    await asyncio.sleep(0.02)
    assert observer_result == 4, "after 110ms the value should have been updated to the cumulative result"
    assert call_count == 2, "postponed cumulative updates should cause exactly one update"
    
    # single update after delay should be one call again
    obs.value = 5
    await asyncio.sleep(0.3)    # wait a bunch so we have 0 wait time for the next update
    assert observer_result == 5
    assert call_count == 3

    # stress test of a bunch of immediate updates should result in two spaced-out updates
    for i in range(6, 20):
        obs.value = i
    # we immediately expect the first value
    assert observer_result == 6
    assert call_count == 4
    # should change after 100ms so after 90ms should not yet have changed
    await asyncio.sleep(0.09)
    assert observer_result == 6
    assert call_count == 4
    # and after a generous 150ms the cumulative update for the end result should definitely be through
    await asyncio.sleep(0.15)
    assert observer_result == 19
    assert call_count == 5

def throttle_timing_check_no_postpone(tr: throttle):
    obs = Observable[int]()
    observer_result = ...
    call_count = 0
    def observer(v: int):
        nonlocal observer_result, call_count
        observer_result = v
        call_count += 1
    obs >> tr >> observer
    
    # create a bunch of updates
    for i in range(1, 5):
        obs.value = i
        time.sleep(0.01)
    # we expect only the first update to pass
    assert observer_result == 1, "first update should pass"
    assert call_count == 1
    # even after some time
    time.sleep(0.2)
    assert observer_result == 1, "no further updates should pass"
    assert call_count == 1

    # and when doing again, the same thing should happen
    for i in range(6, 10):
        obs.value = i
        time.sleep(0.01)
    # we expect only the first update to pass
    assert observer_result == 6, "first update should pass"
    assert call_count == 2
    # even after some time
    time.sleep(0.2)
    assert observer_result == 6, "no further updates should pass"
    assert call_count == 2

async def test_throttle_hz():
    await throttle_timing_check(throttle(hz=10))
    throttle_timing_check_no_postpone(throttle(hz=10, postpone_updates=False))

async def test_throttle_interval():
    await throttle_timing_check(throttle(interval=0.1))
    throttle_timing_check_no_postpone(throttle(interval=0.1, postpone_updates=False))
