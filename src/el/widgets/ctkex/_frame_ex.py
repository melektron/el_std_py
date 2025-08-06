"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.08.25, 02:39
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Enhanced frame with improved automatic color detection with transparent parents.
"""


import math
import typing
from copy import copy

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config

from .._deps import *


class _CTkFramePassthroughArgs(typing.TypedDict, total=False):
    width: int
    height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]

    bg_color: Color
    fg_color: typing.Optional[Color]
    border_color: typing.Optional[Color]

    background_corner_colors: typing.Optional[tuple[Color]]
    overwrite_preferred_drawing_method: typing.Optional[str]

class CTkFrameExPassthroughArgs(_CTkFramePassthroughArgs, total=False):
    ...


class CTkFrameEx(ctk.CTkFrame):

    def __init__(self,
        master: tk.Misc,
        **kwargs: typing.Unpack[CTkFrameExPassthroughArgs]
    ):
        # we modify the mechanism to determine the fg_color by
        # always adding an fg_color attribute to the parent constructor
        if "fg_color" not in kwargs:
            if isinstance(master, ctk.CTkFrame):
                # here we use the _detect_color_of_master() method instead of just using `_fg_color`.
                # This accounts for transparency of the master(s).
                if self._detect_color_of_master(master) == ctk.ThemeManager.theme["CTkFrame"]["fg_color"]:
                    kwargs["fg_color"] = ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
                else:
                    kwargs["fg_color"] = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            else:
                kwargs["fg_color"] = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]

        super().__init__(master, **kwargs)
