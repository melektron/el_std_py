"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
25.07.25, 09:35
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Tests for el.callback_manager.
"""

import pytest
import typing
import logging

from el.callback_manager import CallbackManager, RegistrationID
from el.lifetime import LifetimeManager


_log = logging.getLogger(__name__)


def test_cb_registration():
    last_cb_value1: int = 0
    def handler1(v: int):
        nonlocal last_cb_value1
        last_cb_value1 = v
    last_cb_value2: int = 0
    def handler2(v: int):
        nonlocal last_cb_value2
        last_cb_value2 = v
    
    mgr = CallbackManager[int]()
    
    mgr.notify_all(1)
    assert last_cb_value1 == 0, "not yet registered, shouldn't cause callback"
    assert last_cb_value2 == 0, "not yet registered, shouldn't cause callback"
    
    id1 = mgr.register(handler1)
    mgr.notify_all(2)
    assert last_cb_value1 == 2, "registered, should have updated"
    assert last_cb_value2 == 0, "not yet registered, shouldn't cause callback"

    id2 = mgr.register(handler2)
    mgr.notify_all(3)
    assert last_cb_value1 == 3, "registered, should have updated"
    assert last_cb_value2 == 3, "registered, should have updated"

    assert mgr.remove(1234567) == False, "invalid registration id should return false when trying to remove"

    assert mgr.remove(id1), "this registration should exist, should return true"
    mgr.notify_all(4)
    assert last_cb_value1 == 3, "unregistered, should no longer update"
    assert last_cb_value2 == 4, "still present, should have updated"

    assert mgr.remove(id2), "this registration should exist, should return true"
    mgr.notify_all(5)
    assert last_cb_value1 == 3, "unregistered, should no longer update"
    assert last_cb_value2 == 4, "unregistered, should no longer update"


def test_weak_function():
    """
    Tests that weak functions are automatically removed when
    they are deleted
    """
    last_cb_value: int = 0
    mgr = CallbackManager[int]()
    
    def create_registration():
        nonlocal last_cb_value
        def handler(v: int):
            nonlocal last_cb_value
            last_cb_value = v
        assert mgr.callback_count == 0, "no cb registered yet"
        mgr.register(handler) 
        assert mgr.callback_count == 1, "one cb should have been registered"
        assert last_cb_value == 0, "should not yet have been called"
        mgr.notify_all(1)
        assert last_cb_value == 1, "should have been called"
        # explicit deletion because GC can be inconsistent
        del handler
    
    create_registration()
    assert last_cb_value == 1, "variable should be nonlocal"
    assert mgr.callback_count == 0, "weak callback should have been removed"
    mgr.notify_all(2)
    assert last_cb_value == 1, "removed callback should not cause value change"


def test_weak_method():
    """
    Tests that weak methods and their object references are automatically 
    removed when they are deleted
    """
    last_cb_value: int = 0
    deleted: bool = False
    mgr = CallbackManager[int]()

    class Consumer:
        def __init__(self):
            mgr.register(self.handler)
        
        def handler(self, v: int):
            nonlocal last_cb_value
            last_cb_value = v
        
        def __del__(self):
            nonlocal deleted
            deleted = True
    
    def create_registration():
        assert mgr.callback_count == 0, "no cb should have been registered yet"
        consumer = Consumer()
        assert mgr.callback_count == 1, "one cb should have been registered"
        assert last_cb_value == 0, "should not yet have been called"
        mgr.notify_all(1)
        assert last_cb_value == 1, "should have been called"
        assert deleted == False, "should not have been deleted yet"
        # explicit deletion because GC can be inconsistent
        del consumer
    
    create_registration()
    assert deleted == True, "should not have been deleted now"
    assert last_cb_value == 1, "variable should be nonlocal"
    assert mgr.callback_count == 0, "weak callback should have been removed"
    mgr.notify_all(2)
    assert last_cb_value == 1, "removed callback should not cause value change"


def test_strong_function():
    """
    Tests that strong function references are kept alive
    """
    last_cb_value: int = 0
    mgr = CallbackManager[int](weak_by_default=False)
    
    def create_registration():
        nonlocal last_cb_value
        def handler(v: int):
            nonlocal last_cb_value
            last_cb_value = v
        assert mgr.callback_count == 0, "no cb registered yet"
        mgr.register(handler) 
        assert mgr.callback_count == 1, "one cb should have been registered"
        assert last_cb_value == 0, "should not yet have been called"
        mgr.notify_all(1)
        assert last_cb_value == 1, "should have been called"
        # explicit deletion because GC can be inconsistent
        del handler
    
    create_registration()
    assert last_cb_value == 1, "variable should be nonlocal"
    assert mgr.callback_count == 1, "strong callback should stay"
    mgr.notify_all(2)
    assert last_cb_value == 2, "strong callback should still work"


def test_strong_method():
    """
    Tests that strong methods and their object references are
    kept alive
    """
    last_cb_value: int = 0
    deleted: bool = False
    mgr = CallbackManager[int](weak_by_default=False)

    class Consumer:
        def __init__(self):
            mgr.register(self.handler)
        
        def handler(self, v: int):
            nonlocal last_cb_value
            last_cb_value = v
        
        def __del__(self):
            nonlocal deleted
            deleted = True
    
    def create_registration():
        assert mgr.callback_count == 0, "no cb should have been registered yet"
        consumer = Consumer()
        assert mgr.callback_count == 1, "one cb should have been registered"
        assert last_cb_value == 0, "should not yet have been called"
        mgr.notify_all(1)
        assert last_cb_value == 1, "should have been called"
        assert deleted == False, "should not have been deleted yet"
        # explicit deletion because GC can be inconsistent
        del consumer
    
    create_registration()
    assert deleted == False, "strong method object should still be kept alive"
    assert last_cb_value == 1, "variable should be nonlocal"
    assert mgr.callback_count == 1, "strong callback should stay"
    mgr.notify_all(2)
    assert last_cb_value == 2, "strong callback should still work"


def test_weak_override():

    """
    Tests that weak setting can be overridden on a per-call basis
    """
    last_cb_value: int = 0
    mgr = CallbackManager[int](weak_by_default=False)
    
    def create_registration():
        nonlocal last_cb_value
        def handler(v: int):
            nonlocal last_cb_value
            last_cb_value = v
        assert mgr.callback_count == 0, "no cb registered yet"
        mgr.register(handler, weak=True)
        assert mgr.callback_count == 1, "one cb should have been registered"
        assert last_cb_value == 0, "should not yet have been called"
        mgr.notify_all(1)
        assert last_cb_value == 1, "should have been called"
        # explicit deletion because GC can be inconsistent
        del handler
    
    create_registration()
    assert last_cb_value == 1, "variable should be nonlocal"
    assert mgr.callback_count == 0, "weak callback should have been removed"
    mgr.notify_all(2)
    assert last_cb_value == 1, "removed callback should not cause value change"


def test_lifetime():
    """
    Tests that a callback registration can be
    managed by a LifetimeManager
    """
    lifetime = LifetimeManager()

    last_cb_value1: int = 0
    def handler1(v: int):
        nonlocal last_cb_value1
        last_cb_value1 = v
    last_cb_value2: int = 0
    def handler2(v: int):
        nonlocal last_cb_value2
        last_cb_value2 = v
    
    mgr = CallbackManager[int]()
    
    with lifetime():
        id1 = mgr.register(handler1)
        id2 = mgr.register(handler2)
    
    mgr.notify_all(3)
    assert last_cb_value1 == 3, "registered, should have updated"
    assert last_cb_value2 == 3, "registered, should have updated"

    assert len(lifetime._managed_registrations) == 2, "two registrations should be managed"

    assert lifetime.end() == 2, "two registrations were alive and should have been removed"

    assert mgr.callback_count == 0, "should have been unregistered by lifetime ending"

    mgr.notify_all(5)
    assert last_cb_value1 == 3, "unregistered, should no longer update"
    assert last_cb_value2 == 3, "unregistered, should no longer update"


def test_lifetime_no_ref():
    """
    Tests that a LifetimeManager does not keep
    strong references to the CallbackManager
    """
    lifetime = LifetimeManager()
    last_cb_value: int = 0
    deleted: bool = False

    def sub_scope():
        mgr = CallbackManager[int](weak_by_default=True)

        class Consumer:
            def __init__(self):
                mgr.register(self.handler)
            
            def handler(self, v: int):
                nonlocal last_cb_value
                last_cb_value = v
            
            def __del__(self):
                nonlocal deleted
                deleted = True
        
        with lifetime():
            consumer = Consumer()
        mgr.notify_all(1)
        assert last_cb_value == 1, "should have been called"
        assert deleted == False, "should not have been deleted yet"
        # explicit deletion because GC can be inconsistent
        del mgr
    
    sub_scope()
    assert deleted == True, "strong instance should be deleted because CallbackManager should be deleted"
    assert lifetime.end() == 0, "CallbackManager should already be deleted, nothing should be unregistered"
