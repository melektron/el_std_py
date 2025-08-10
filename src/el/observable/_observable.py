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

import abc
import typing 
import logging
from weakref import ref, ReferenceType
from dataclasses import dataclass

from el.lifetime import RegistrationID, AbstractRegistry


_log = logging.getLogger(__name__)

type ObserverFunction[T, R] = typing.Callable[[T], R]


class StatefulFilter[T, R](abc.ABC):
    @abc.abstractmethod
    def _connect(self, src: ReferenceType["Observable[T]"], dst: ReferenceType["Observable[R]"]) -> None:
        """
        Method that is called when a stateful filter instance
        is connected to an observable chain. The filter
        is given a weak reference to both the source observable 
        (the one whose change triggers a `__call__` on the filter)
        as well as the destination observable (the one that is
        assigned if `__call__` returns a value), so it can autonomously
        and asynchronously trigger value updates in the chain without
        requiring an update from the source observable. This is useful
        for time-based filters (delay, throttle, ...).

        The reference is weak to avoid potential reference circles between
        the source observable and the StatefulFilter instance.
        The source observable holds a strong reference to the StatefulFilter,
        but the same should not be true in the other direction.

        This is guaranteed to be called before the filter is
        ever invoked.
        """
        ...
    
    def _disconnect(self, src: ReferenceType["Observable[T]"], dst: ReferenceType["Observable[R]"]) -> None:
        """
        This method is called just before this observer is disconnected
        from the observer chain of `src` because an observation was terminated
        using a LifetimeManager. In most cases this method is not required,
        but it can be overridden to detect such an event and remove any internal 
        references or clean up resources if applicable. The source
        and destination observables are passed again which is useful for filters 
        that take in multiple sources to identify the source that will be disconnected.
        """
        ...

    @abc.abstractmethod
    def __call__(self, v: T) -> R:
        """
        the instance is called to notify it of a source update.
        v is the new source value. The function may return a value
        to trigger an update on the destination or return `...` (ellipsis)
        to inhibit the update and possibly trigger an update asynchronously 
        later using the objects passed via `_connect`.
        
        NOTE: To get proper type hinting, in observable chains when matching
        input and return type (T and R), they need to be a generic
        type argument of the __call__ method, not the class, so do the following
        in child classes to match input and return type:
        ```python
        @typing.override
        def __call__[CT](self, v: CT) -> CT: ...
        ```
        """
        ...


@dataclass
class _ObserverRecord[T]:
    """
    Internal representation of an observer
    """
    # intermediate receiver function wrapping the derived observable functionality
    function: ObserverFunction[T, None]
    # the resulting derived observable object
    derived: "Observable[T]"
    # set when the observer is a stateful filter so it can be deactivated
    stateful_filter: StatefulFilter | None = None


class Observable[T](AbstractRegistry):

    def __init__(self, initial_value: T = ..., *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value: T = initial_value
        self._observers: dict[RegistrationID, _ObserverRecord[T]] = {}
        self._next_observer_id: RegistrationID = 0

    def receive(self, v: T):
        """
        same as the value setter, just for internal use in chaining and for setting in lambdas 
        """
        self.value = v

    def _notify(self):
        """
        Notifies all observers of the current value
        """
        for observer in self._observers.values():
            observer.function(self._value)
    
    def force_notify(self):
        """
        Force fully cause a value update to be propagated
        to all observers without checking for value
        changes. This can be useful to send updates when externally
        mutating the value without the Observable's knowledge.
        """
        self._notify()
    
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
        internally stored but observers are not notified of it. This is mainly intended
        for filters and should in most cases not be used directly.
        """
        if v is ...:    #
            self._value = ...
        elif self._value != v:
            self._value = v
            self._notify()

    def observe[R](
        self, 
        observer: ObserverFunction[T, R],
        initial_update: bool = True
    ) -> "Observable[R]":
        """
        Adds a new observer function to the observable.
        This acts exactly the same as the ">>" operator and is intended
        for cases where the usage of such operators is not possible or
        would be confusing.

        If the observable already has a value, the observer is called immediately.

        This returns a new observer that observes the return value of observer function.
        This allows you to create derived observables with any conversion function
        between them or chain multiple conversions.

        When a function returns ... (Ellipsis), this is interpreted as "no value" and
        the derived observable is not updated. This can be used to create filter functions.

        Parameters
        ----------
        observer : ObserverFunction[T, R]
            observer function to be called on value change
        initial_update : bool, optional
            whether the observer should be called with an initial value immediately
            upon observation, by default True (which is the same behavior as the
            >> operator). If the source observable has no value, an initial update
            will never be emitted.
        
        Returns
        -------
        Observable[R]
            The derived observable.

        Raises
        ------
        TypeError
            Invalid observer function passed

        Example
        -------

        ```python
        number = Observable[int]()
        number.observe(lambda v: print(f"number = {v}"))
        number_times_two = number.observe(lambda v: v * 2 if v != 3 else ...)
        number_times_two.observe(lambda v: print(f"a) number * 2 = {v}"))
        # or all in one line
        number.observe(lambda v: v * 2).observe(lambda v: print(f"b) number * 2 = {v}"))
        
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
        
        # if the observer is a stateful filter, we must initialize it
        is_stateful_filter = False
        if isinstance(observer, StatefulFilter):
            is_stateful_filter = True
            observer._connect(ref(self), ref(derived_observable))
        
        # if we have a value and it isn't disabled, already update the observer
        # with an initial update
        if initial_update and self._value is not ...:
            observer_wrapper(self._value)
        
        # save the observer and notify Abstract Registry to allow lifetime usage
        self._observers[self._next_observer_id] = _ObserverRecord[T](
            function=observer_wrapper,
            derived=derived_observable,
            stateful_filter=observer if is_stateful_filter else None
        )
        self._ar_register(self._next_observer_id)
        self._next_observer_id += 1
         
        # return the derived observable for chaining
        return derived_observable

    def __rshift__[R](self, observer: ObserverFunction[T, R]) -> "Observable[R]":
        """
        Adds a new observer function to the observable like `.observe()` but
        with nicer syntax for chaining.

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
        return self.observe(observer)
    
    def __lshift__(self, observable: "Observable"):
        """
        Observes another observable object and therefore chains any value changes of that object.
        If other is the observable itself, a recursion error occurs
        """
        if not isinstance(observable, Observable):
            raise TypeError(f"Observable cannot be chained to object of type '{type(observable)}'. It should be an 'Observable'")
        if observable is self:
            raise RecursionError("Observable cannot observe itself")
        observable >> self.receive
    
    def link(self, other: "Observable[T]", initial_update: bool = True):
        """
        Establishes a bidirectional link between two
        observables (`other` and `self`).
        When either observable updates, the other does as well.
        When initially linking, `other` is updated
        with the value of `self`.

        Parameters
        ----------
        observable : Observable[T]
            observable to link with
        initial_update : bool 
            whether to initially update `other` with the value
            of `self`. By default True.
        """
        self.observe(other.receive, initial_update=initial_update)
        other.observe(self.receive, initial_update=False)

    @typing.override
    def _ar_unregister(self, id: RegistrationID):
        """
        Implement unregistering to allow for lifetime management.
        """
        if id in self._observers:
            observer = self._observers[id]
            if observer.stateful_filter is not None:
                observer.stateful_filter._disconnect(ref(self), ref(observer.derived))
            del self._observers[id]


type MaybeObservable[T] = Observable[T] | T

def maybe_observe[T](
    var: MaybeObservable[T],
    cb: ObserverFunction[T, typing.Any],
    initial_update: bool = True
) -> bool:
    """
    Allows "observing" a MaybeObservable. If `var` is not
    an observable, `cb` will be called once with the value
    of `var`, otherwise it will observe `var` and be called
    any time it's value changes.
    
    Parameters
    ----------
    observer : ObserverFunction[T, R]
        observer function to be called on value change
    initial_update : bool, optional
        whether the observer should be called with an initial value immediately
        upon observation, by default True. 
        If `var` is not an Observable and `initial_update` is set to False,
        `cb` will never be called.

    Returns
    -------
    bool
        True if `var` is an observable,
        False if `var` is not an observable
    """
    if isinstance(var, Observable):
        var.observe(cb, initial_update=initial_update)
        return True
    elif initial_update:
        cb(var)
    return False

def maybe_obs_value[T](var: MaybeObservable[T]) -> T:
    """
    Returns
    -------
    T
        Current value of the observable if it was one,
        or just the input value if not
    """
    if isinstance(var, Observable):
        return var.value
    else:
        return var

def maybe_get_obs[T](var: MaybeObservable[T]) -> Observable[T]:
    """
    Returns
    -------
    Observable[T]
        An observable corresponding to the maybe observable.
        If `var` is an observable it is returned, otherwise
        a new observable with initial value `var` is returned.
    """
    if isinstance(var, Observable):
        return var
    else:
        return Observable(var)

