"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
17.10.24, 13:37
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Class that manages object state changes
"""

import abc
from collections import deque
from typing import Generic, Callable, ParamSpec, override
from weakref import WeakMethod, ref, ReferenceType


_USE_PYDANTIC = False
try:
    import pydantic

    _USE_PYDANTIC = True
except ImportError:
    pass


class HistoryManager[T](abc.ABC):
    def __init__(self) -> None:
        # queues that snapshots are shifted between
        self._undo_items: deque[T] = deque()
        self._redo_items: deque[T] = deque()

    @abc.abstractmethod
    def take_snapshot(self) -> None:
        """Creates a snapshot of an object. This resets the redo queue."""

    @abc.abstractmethod
    def undo(self) -> T | None:
        """Pops one item from the undo queue. Returns None if none are available."""

    @abc.abstractmethod
    def redo(self) -> T | None:
        """Pops one item from the redo queue if possible. Returns None if none are available."""
    
    def clear(self) -> None:
        """Clears all history. This removes all undo and redo entries."""
        self._undo_items.clear()
        self._redo_items.clear()


if _USE_PYDANTIC:

    class ModelHistoryManager[MT: pydantic.BaseModel](HistoryManager[MT]):
        """
        History manager specialization for pydantic models using their native
        copy functionality
        """

        @override
        def take_snapshot(self, state: MT) -> None:
            new_snapshot = state.model_copy(deep=True)
            self._undo_items.append(new_snapshot)
            # when doing a new action, we move onto a new timeline
            # -> redo must be cleared
            self._redo_items.clear()

        @override
        def undo(self) -> MT | None:
            if len(self._undo_items) == 0:
                return None
            else:
                snapshot = self._undo_items.pop()
                self._redo_items.push(snapshot)
                return snapshot

        @override
        def redo(self) -> MT | None:
            if len(self._redo_items) == 0:
                return None
            else:
                snapshot = self._redo_items.pop()
                self._undo_items.push(snapshot)
                return snapshot
