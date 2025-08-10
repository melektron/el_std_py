"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
10.08.25, 13:19
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Functionality to compose a composed observable from multiple sources.
The composed observable updates whenever any of the sources do.
Due to limitations of pythons typing system, while it is possible
to define varadic type arguments (https://peps.python.org/pep-0646/), 
it is not possibly to transform them by adding or removing wrapper 
types on each argument. To work around this, a set of overloads for
a reasonable maximum amount of arguments (64) is procedurally generated 
between the marker comments below using the `.generate_composed.py`
helper script.
"""

import typing
from ._observable import Observable


type ComposedObserverFunction[*Ts, R] = typing.Callable[[*Ts], R]

class ComposedObservable[*Ts](Observable[tuple[*Ts]]):
    """ 
    Return type of `el.observable.compose()`. This is
    not to be constructed by a library user directly!
    """

    def receive(self, *vs: *Ts):
        """
        same as the value setter, just for internal use in chaining and for setting in lambdas 
        """
        self.value = vs

    def observe[R](
        self, 
        observer: ComposedObserverFunction[*Ts, R],
        initial_update: bool = True
    ) -> "Observable[R]":
        """
        Adds a new observer function to the composed observable returned from `compose()`.
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
        observer : ComposedObserverFunction[*Ts, R]
            observer function to be called on value change. This is 
            ComposedObserverFunction, meaning it will receive all arguments
            of the source observables unpacked.
        initial_update : bool, optional
            whether the observer should be called with an initial value immediately
            upon observation, by default True (which is the same behavior as the
            >> operator). If the source observable has no value, an initial update
            will never be emitted.
        
        Returns
        -------
        Observable[R]
            The derived observable. This is no longer a composed observable
            but instead just a regular one, as only one value can be returned.

        Raises
        ------
        TypeError
            Invalid observer function passed

        Example
        -------

        ```python
        number = Observable[int]()
        text = Observable[str]()
        composed = compose(number, text)
        composed.observe(lambda n, t: print(f"number = {n}, text = {t}"))

        # set the original observables
        number.value = 5
        text.value = "hi"
        ``` 

        Console output:

        ```
        number = 5, text = ...
        number = 5, text = "hi"
        ```
        """
        if not callable(observer):
            raise TypeError(f"Observer must be of callable type 'ComposedObserverFunction', not '{type(observer)}'")
        
        # create a wrapper that unpacks the tuple in the composed observable value
        def unpacker(v: tuple[*Ts]) -> R:
            return observer(*v)

        return super().observe(unpacker, initial_update)

    def __rshift__[R](self, observer: ComposedObserverFunction[*Ts, R]) -> "Observable[R]":
        """
        Adds a new observer function to the observable like `.observe()` but
        with nicer syntax for chaining. This is however not recommended
        for use on composed observables, as the observer may not be properly typed.
        """
        return self.observe(observer)



# DO NOT REMOVE THE FOLLOWING LINE
## == PROC GENERATED START == ##
@typing.overload
def compose[T0](s0: Observable[T0], all_required: bool = True) -> ComposedObservable[T0]:
    ...

@typing.overload
def compose[T0, T1](s0: Observable[T0], s1: Observable[T1], all_required: bool = True) -> ComposedObservable[T0, T1]:
    ...

@typing.overload
def compose[T0, T1, T2](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], all_required: bool = True) -> ComposedObservable[T0, T1, T2]:
    ...

@typing.overload
def compose[T0, T1, T2, T3](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], s58: Observable[T58], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], s58: Observable[T58], s59: Observable[T59], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], s58: Observable[T58], s59: Observable[T59], s60: Observable[T60], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60, T61](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], s58: Observable[T58], s59: Observable[T59], s60: Observable[T60], s61: Observable[T61], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60, T61]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60, T61, T62](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], s58: Observable[T58], s59: Observable[T59], s60: Observable[T60], s61: Observable[T61], s62: Observable[T62], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60, T61, T62]:
    ...

@typing.overload
def compose[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60, T61, T62, T63](s0: Observable[T0], s1: Observable[T1], s2: Observable[T2], s3: Observable[T3], s4: Observable[T4], s5: Observable[T5], s6: Observable[T6], s7: Observable[T7], s8: Observable[T8], s9: Observable[T9], s10: Observable[T10], s11: Observable[T11], s12: Observable[T12], s13: Observable[T13], s14: Observable[T14], s15: Observable[T15], s16: Observable[T16], s17: Observable[T17], s18: Observable[T18], s19: Observable[T19], s20: Observable[T20], s21: Observable[T21], s22: Observable[T22], s23: Observable[T23], s24: Observable[T24], s25: Observable[T25], s26: Observable[T26], s27: Observable[T27], s28: Observable[T28], s29: Observable[T29], s30: Observable[T30], s31: Observable[T31], s32: Observable[T32], s33: Observable[T33], s34: Observable[T34], s35: Observable[T35], s36: Observable[T36], s37: Observable[T37], s38: Observable[T38], s39: Observable[T39], s40: Observable[T40], s41: Observable[T41], s42: Observable[T42], s43: Observable[T43], s44: Observable[T44], s45: Observable[T45], s46: Observable[T46], s47: Observable[T47], s48: Observable[T48], s49: Observable[T49], s50: Observable[T50], s51: Observable[T51], s52: Observable[T52], s53: Observable[T53], s54: Observable[T54], s55: Observable[T55], s56: Observable[T56], s57: Observable[T57], s58: Observable[T58], s59: Observable[T59], s60: Observable[T60], s61: Observable[T61], s62: Observable[T62], s63: Observable[T63], all_required: bool = True) -> ComposedObservable[T0, T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T38, T39, T40, T41, T42, T43, T44, T45, T46, T47, T48, T49, T50, T51, T52, T53, T54, T55, T56, T57, T58, T59, T60, T61, T62, T63]:
    ...
## == PROC GENERATED END == ##
# DO NOT REMOVE THE PREVIOUS LINE


def compose(
    *args: Observable,
    all_required: bool = True
) -> ComposedObservable:
    """
    Composes multiple observables into one composed observable, 
    which updates whenever any of the source observables update.
    When the ComposedObservable is observed, the observer is called
    with the values of all provided source observables in order.

    Parameters
    ----------
    args : Observable
        any observables that should be used as source
    all_required : bool
        whether all source observables are required to have a value
        for the composed observable to be triggered. Setting this to true
        ensures that observers are never called with ellipsis values,
        but may cause updates of some observables to be missed while others
        are empty.
    
    Returns
    -------
    ComposedObservable
        Composed observable of the source types. This
        is typed using overloads.
    """
    composed_obs = ComposedObservable()
    def updater(_=None) -> None:
        values = tuple(obs.value for obs in args)
        if all_required and any(v == ... for v in values):
            composed_obs.value = ...
        else:
            composed_obs.value = values
    updater()   # set initial value
    # hook up all the sources by observing them
    for obs in args:
        obs.observe(updater, initial_update=False)   # init already done above
    
    return composed_obs

