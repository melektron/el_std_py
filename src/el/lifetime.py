"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
24.07.25, 17:08
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Contextual lifetime management for registerable objects
such as Observables and CallbackManagers
"""

import abc
import typing
from contextvars import ContextVar, Token
from contextlib import contextmanager
from weakref import ref, ReferenceType


# context var to track the current observer lifetime that observables should register
# new observations to
_lifetime_manager_ctx = ContextVar[typing.Union["LifetimeManager", None]]("_lifetime_manager_ctx", default=None)

# type to represent countable IDs given out by registries
# to identify their registrations (callbacks, observers, ...)
type RegistrationID = int


class AbstractRegistry(abc.ABC):
    """
    Base class of objects that allow registering
    some resource (callbacks, observers, ...).
    This provides a common interface for the 
    `LifetimeManager` to unregister those registrations.
    """

    def _ar_register(
        self, 
        id: RegistrationID, 
        manager: typing.Union["LifetimeManager", None] = None
    ) -> None:
        """
        This method should be called by subclasses
        when a new registration is made so that it can 
        later be cleaned up using `_ar_unregister()`.
        This causes the registration to be recorded by 
        the LifetimeManager if one is available in the context
        or was explicitly provided. If not `LifetimeManager` is 
        available, the registration is not recorded and will
        not be automatically managed.

        Parameters
        ----------
        id : RegistrationID
            Value to identify the registration. The creation
            and allocation of IDs is to be managed by the subclass,
            but should uniquely identify a registration pre instance.
        manager : LifetimeManager | None
            Optional parameter to explicitly specify the lifetime
            manager instance the registration should be managed by.
        """
        # determine what the master of this element should be
        # (either grab from context or use specified master)
        local_manager = manager if manager is not None else _lifetime_manager_ctx.get()
        
        if local_manager is not None:
            local_manager._register(self, id)
        

    @abc.abstractmethod
    def _ar_unregister(self, id: RegistrationID) -> None:
        """
        This method should be overridden by subclasses
        to allow the LifetimeManager to cleanup 
        a registration. After this call, the registration
        should be fully nullified, i.e. all references to objects
        (callback functions, ...) should be released

        Parameters
        ----------
        id : RegistrationID
            Registration ID to unregister
        """


class LifetimeManager:
    """
    Class to manage lifetime of registered resources (e.g. observers, callbacks, ...) and
    to automatically unregister them when the lifetime is deleted (or if the `end()` method
    is called)
    
    This lifetime object can be used as a context manager by calling it
    to automatically register all observation made under the context to this lifetime.
    This works with any objects that inherit form and implement `AbstractRegistry`,
    e.g. Observables:

    ```python
    lt = LifetimeManager()
    obs = Observable(...)
    with lt():
        obs >> self._on_change
    ```
    
    The call operator is necessary to allow managing the context on a per-call basis in
    case multiple calls happen concurrently in different threads or asyncio tasks.

    It is to be noted that the lifetime does not hold hard references to any registries
    it manages. It therefore doesn't prevent registries form disablign
    """

    def __init__(self):
        self._managed_registrations: list[tuple[ReferenceType[AbstractRegistry], RegistrationID]] = []
    
    @contextmanager
    def __call__(self):
        """
        call operator to enter lifetime context.
        Any observations created under this context
        will be registered to this observer lifetime object.
        This is a generator ctx manager to allow concurrent calls
        with different token states.
        """
        token = _lifetime_manager_ctx.set(self)
        try:
            yield
        finally:
            _lifetime_manager_ctx.reset(token)
    
    def _register(self, registry: AbstractRegistry, id: RegistrationID) -> None:
        """
        registers a registration on a specific registry to be managed by this lifetime manager.
        This keeps a weak reference to `registry`.
        """
        self._managed_registrations.append((
            ref(registry),
            id  # just an integer, no ref needed
        ))

    def end(self) -> int:
        """
        Ends the lifetime. This causes all managed 
        resources to be unregistered.

        Returns
        -------
        int
            the number of registrations that were unregistered
            (excluding any where the registry has already been deleted)
        """
        count = 0
        for registry_ref, id in self._managed_registrations:
            registry = registry_ref()
            if registry is not None:
                count += 1
                registry._ar_unregister(id)
        return count
            
    def __del__(self) -> None:
        """
        When the lifetime object is deleted, the lifetime ends.
        """
        self.end()