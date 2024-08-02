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
from ._observable import Observable, ObserverFunction

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
    
def call_if_true(c: typing.Callable) -> ObserverFunction[typing.Any, None]:
    """
    Calls the provided function when the observable changes it's
    value to equal true when converted to bool.
    ```python 
    bool(v) == True 
    ```
    Value changes that do not meet this requirement are ignored
    """
    def obs(v: typing.Any) -> None:
        if bool(v) == True:
            c()
    return obs