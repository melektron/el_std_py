"""
ELEKTRON © 2023
Written by melektron
www.elektron.work
21.05.23, 14:41
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Observable class whose changes can be tracked
"""

import typing 
import logging


_log = logging.getLogger(__name__)

T = typing.TypeVar("T")
R = typing.TypeVar("R")
ObserverFunction = typing.Callable[[T], R]


class Observable(typing.Generic[T]):
    _value: T
    _observers: list[ObserverFunction[T, typing.Any]]

    def __init__(self, initial_value: T = ...):
        self._value = initial_value
        self._observers = []

    def _receive(self, v):
        """
        same as the value setter, just for internal use in chaining
        """
        self.value = v

    def _notify(self):
        """
        Notifies all observers of the current value
        """
        for observer in self._observers:
            observer(self._value)
    
    @property
    def value(self) -> T:
        """
        Returns the current value or ... if no value is set yet
        """
        return self._value

    @value.setter
    def value(self, v: T):
        """
        Updates the value with a new value and notifies all observers
        if the value is not equal to the previous value.

        If the observable is set to ... (Ellipsis), that means "no value". This will be 
        internally stored but observers are not notified of it. 
        """
        if v is ...:    #
            self._value = ...
        elif self._value != v:
            self._value = v
            self._notify()

    def __rshift__(self, observer: ObserverFunction[T, R]) -> "Observable[R]":
        """
        Adds a new observer function to the observable.

        If the observable already has a value, the observer is called immediately.

        This returns a new observer that observes the return value of observer function.
        This allows you to create derived observables with any conversion function
        between them or chain multiple conversions.

        When a function returns ... (Ellipsis), this is interpreted as "no value" and
        the derived observable is not updated. This can be used to create filter functions.

        Example usage:

        ```python
        number = Observable[int]()
        number >> (lambda v: print(f"number = {v}"))
        number_times_two = number >> (lambda v: v * 2 if v != 3 else ...)
        number_times_two >> (lambda v: print(f"a) number * 2 = {v}"))
        # or all in one line
        number >> (lambda v: v * 2) >> (lambda v: print(f"b) number * 2 = {v}"))
        
        # set the original observable
        number.value = 5
        number.value = 3
        ``` 

        Console output:

        ```
        number = 5
        a) number * 2 = 10
        b) number * 2 = 10
        number = 3
        b) number * 2 = 10
        ```

        """
        if not callable(observer):
            raise TypeError(f"Observer must be of callable type 'ObserverFunction', not '{type(observer)}'")
        # create a derived observable
        derived_observable = Observable[R]()
        # create a function to pass the return value of of the observer to the new observable
        def observer_wrapper(new_value: T) -> None:
            result = observer(new_value)
            if result is not ...:   # allow for filter functions to ignore values
                derived_observable.value = result
        # if we have a value, already update the observer
        if self._value is not ...:
            observer_wrapper(self._value)
        # save the observer
        self._observers.append(observer_wrapper)
        # return the derived observable for chaining
        return derived_observable
    
    def __lshift__(self, observable: "Observable"):
        """
        Observes another observable object and therefore chains any value changes of that object.
        If other is the observable itself, a recursion error occurs
        """
        if not isinstance(observable, Observable):
            raise TypeError(f"Observable cannot be chained to object of type '{type(observable)}'. It should be an 'Observable'")
        if observable is self:
            raise RecursionError("Observable cannot observe itself")
        observable >> self._receive


ComposedObserverFunction = typing.Callable[[tuple[any]], None]

class ComposedObservable:
    """
    NOTE: this is currently not working
    """
    
    _sources: tuple[Observable]
    _observers: list[ComposedObserverFunction]
    _init_complete = False

    def __init__(self, *sources: Observable):
        # observe all the sources
        self._sources = sources
        for source in sources:
            if not isinstance(source, Observable):
                raise TypeError(f"Observable cannot be composed from non-Observable source '{type(source)}'")
            source >> self._receive
        self._observers = []
        self._init_complete = True

    def _receive(self, v):
        """
        Internal callback that is observing all sources.
        This is therefore called when any of the sources change value.
        """
        # ignore all the callbacks during init when all the sources observers are registered
        if not self._init_complete: return
        self._notify()

    def _notify(self):
        """
        Notifies all observers of the current value.
        """
        for observer in self._observers:
            observer(self.value)
    
    @property
    def value(self) -> tuple[any]:
        """
        Returns the tuple of sources values
        """
        return (source.value for source in self._sources)

    def __rshift__(self, observer: ComposedObserverFunction):
        """
        Adds a new observer function to the composed observable.
        The Observer will be called every time any of the sources'
        value changes
        """
        if not callable(observer):
            raise TypeError(f"Observer must be of callable type 'ComposedObserverFunction', not '{type(observer)}'")
        observer(self.value)
        self._observers.append(observer)
