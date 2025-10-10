"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
10.10.25, 13:15
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import math
import typing
from copy import copy

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config

from .._deps import *


class _CTkScrollbarPassthroughArgs(typing.TypedDict, total=False):
    width: typing.Optional[int]
    height: typing.Optional[int]
    corner_radius: typing.Optional[int]
    border_spacing: typing.Optional[int]
    minimum_pixel_length: int

    bg_color: Color
    fg_color: typing.Optional[Color]
    button_color: typing.Optional[Color]
    button_hover_color: typing.Optional[Color]

    hover: bool
    command: typing.Optional[typing.Callable[[], typing.Any]]
    orientation: OrientationType

class CTkScrollbarExPassthroughArgs(_CTkScrollbarPassthroughArgs, total=False):
    touchscreen_mode: MaybeObservable[bool]


class CTkScrollbarEx(ctk.CTkScrollbar):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        **kwargs: typing.Unpack[_CTkScrollbarPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )
        super().__init__(master, **kwargs)

    @typing.override
    def _on_enter(self, event=None):
        if not self._touchscreen_mode:
            super()._on_enter(event)
        # if we are in touchscreen mode we don't do the animation

    @typing.override
    def configure(
        self,
        require_redraw=False,
        **kwargs: typing.Unpack[CTkScrollbarExPassthroughArgs],
    ):
        """ 
        Change configuration options dynamically. When changing any
        MaybeObservable attributes with an Observable, the attribute
        will only be set once and not observed. This is intended for
        changing options without Observables.
        """
        if "touchscreen_mode" in kwargs:
            self._touchscreen_mode = maybe_obs_value(kwargs["touchscreen_mode"])
            kwargs.pop("touchscreen_mode")
            self._set_cursor()

        super().configure(require_redraw, **kwargs)

    @typing.override
    def cget(self, attribute_name: str) -> typing.Any:
        if attribute_name == "touchscreen_mode":
            return self._touchscreen_mode
        else:
            return super().cget(attribute_name)

    def _set_cursor(self):
        """ Override this to allow for disable cursor in touchscreen mode """
        if self._touchscreen_mode:
            self.configure(cursor="none")
        else:
            self.configure(cursor="")
