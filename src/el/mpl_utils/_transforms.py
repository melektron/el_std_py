"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
18.01.25, 21:42
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Matplotlib transformations
"""

import typing
from ._deps import *


class FunctionTransform2D(mpl_trans.Transform):
    # https://matplotlib.org/stable/api/transformations.html#matplotlib.transforms.Transform
    input_dims = 2
    output_dims = 2
    # has_inverse is auto-populated

    def __init__(
        self, 
        forward: typing.Callable[[npt.ArrayLike], npt.ArrayLike],
        inverse: typing.Callable[[npt.ArrayLike], npt.ArrayLike] | None = None,
        *args, **kwargs
    ):
        """Transformation that applies arbitrary functions
        to transform a value dynamically. The main use-case is transformation
        according to dynamic captured variables using lambdas.

        Parameters
        ----------
        forward : typing.Callable[[npt.ArrayLike], npt.ArrayLike]
            forward transformation function taking array-like of length 2 and returning
            a new array-like of length 2 with the transformed value.
        inverse : typing.Callable[[npt.ArrayLike], npt.ArrayLike] | None, optional
            optional inverse transformation function. This is passed
            to a new FunctionTransform2D returned by .inverse(), by default None
        """
        super().__init__(*args, **kwargs)
        self._forward_fn = forward
        self._inverse_fn = inverse
        # override inverse flag on each instance (not sure if this does anything but the 
        # other option is to always have it as "true" so couldn't hurt)
        if inverse is not None:
            self.has_inverse = True
        else:
            self.has_inverse = False
            
    def transform(self, values: npt.ArrayLike) -> npt.ArrayLike:
        return self._forward_fn(values)

    def inverted(self):
        if self._inverse_fn is None:
            raise NotImplementedError("No inverse transformation function provided for el.mpl_utils.FunctionTransform2D")
        else:
            # return function transform with swapped functions
            return FunctionTransform2D(
                self._inverse_fn,
                self._forward_fn
            )