"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
16.10.24, 17:06
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Class do manage callbacks from classes in a more elegant way without
reinventing the wheel every time
"""

import inspect
from typing import Generic, Callable, ParamSpec
from weakref import WeakMethod, ref, ReferenceType


CallbackID = int
_id_counter = 0

P = ParamSpec("P")

class CallbackManager(Generic[P]):
    def __init__(self, weak_by_default: bool = True):
        self._weak_by_default = weak_by_default
        self._callbacks: dict[CallbackID, Callable[P, None] | ReferenceType[Callable[P, None]]] = {}
    
    def register(self, cb: Callable[P, None], weak: bool | None = None) -> CallbackID:
        """
        Registers a new callback to the callback manager. If 'weak' is set to 
        true, the callback will only be referenced weakly. If set to false, it will be 
        referenced strongly. If left to None, the default will be used according
        to the configuration of the CallbackManager instance.

        Returns: CallbackID used to identify and later remove the callback again.
        """
        if weak is None:
            weak = self._weak_by_default
        
        global _id_counter
        cb_id = _id_counter
        _id_counter += 1

        if not weak:
            self._callbacks[cb_id] = cb
        else:
            def finish(_) -> None:
                del self._callbacks[cb_id]

            if inspect.ismethod(cb):
                self._callbacks[cb_id] = WeakMethod(cb, finish)
            else:
                self._callbacks[cb_id] = ref(cb, finish)
        
        return _id_counter
    
    def remove(self, id: CallbackID) -> bool:
        """
        Removes a callback by it's id. Returns True if it was removed
        or False if there was no such callback registered.
        """
        if id in self._callbacks:
            del self._callbacks[id]
            return True
        else:
            return False
    
    def notify_all(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Calls all the registered callback functions. If lost weak references are found they
        are removed.
        """
        to_be_removed: list[CallbackID] = []
        for id, cb in self._callbacks.items():
            if isinstance(cb, ReferenceType):
                actual_cb = cb()
                if actual_cb is None:
                    to_be_removed.append(id)
                else:
                    actual_cb(*args, **kwargs)
            else:
                cb(*args, **kwargs)
        for id in to_be_removed:
            del self._callbacks[id]
    
    @property
    def callback_count(self) -> int:
        """ Number of currently registered callbacks """
        return len(self._callbacks)

    @property
    def has_callbacks(self) -> int:
        """ Whether there are any registered callbacks """
        return len(self._callbacks) > 0
