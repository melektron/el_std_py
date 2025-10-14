"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
11.09.25, 21:24
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import sys
import math
import typing
from copy import copy

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config

from .._deps import *


class _CTkCheckBoxPassthroughArgs(typing.TypedDict, total=False):
    width: int
    height: int
    checkbox_width: int
    checkbox_height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]

    bg_color: Color
    fg_color: typing.Optional[Color]
    hover_color: typing.Optional[Color]
    border_color: typing.Optional[Color]
    checkmark_color: typing.Optional[Color]
    text_color: typing.Optional[Color]
    text_color_disabled: typing.Optional[Color] = None,

    text: str
    font: typing.Optional[FontArgType]
    textvariable: typing.Optional[tk.Variable]
    state: StateType
    hover: bool
    command: typing.Optional[typing.Callable[[], typing.Any]]
    onvalue: typing.Union[int, str]
    offvalue: typing.Union[int, str]
    variable: typing.Optional[tk.Variable]

class CTkCheckBoxExPassthroughArgs(_CTkCheckBoxPassthroughArgs, total=False):
    touchscreen_mode: MaybeObservable[bool]


class CTkCheckBoxEx(ctk.CTkCheckBox):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        **kwargs: typing.Unpack[_CTkCheckBoxPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )

        # cache to deduplicate redundante cursor updates
        self._cursor_cache: str = "ThIsVaLuEnEvErHaPpEnS"

        super().__init__(master, **kwargs)

    @typing.override
    def _on_enter(self, event=None):
        # If touchscreen mode is enabled, we prohibit the _on_enter handler to
        # disable hovering behavior
        if self._touchscreen_mode:
            return
        
        super()._on_enter(event)

    @typing.override
    def configure(
        self,
        require_redraw=False,
        **kwargs: typing.Unpack[CTkCheckBoxExPassthroughArgs],
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

    @typing.override
    def _set_cursor(self):
        """ 
        Override this to allow for disable cursor in touchscreen mode,
        better Linux support and reduced flickering due to redundant 
        cursor updates.
        """
        if self._cursor_manipulation_enabled:   # This seems to be hardcoded to true... what's the point?
            cursor = "" # default for systems such as Linux
            if self._touchscreen_mode:
                cursor="none"
            else:
                if self._state == tk.DISABLED:
                    if sys.platform == "darwin" and self._command is not None:
                        cursor = "arrow"
                    elif sys.platform.startswith("win") and self._command is not None:
                        cursor = "arrow"
                elif self._state == tk.NORMAL:
                    if sys.platform == "darwin" and self._command is not None:
                        cursor = "pointinghand"
                    elif sys.platform.startswith("win") and self._command is not None:
                        cursor = "hand2"
            # update cursor if it differs from the previous one
            # to avoid unnecessary flickers
            if self._cursor_cache != cursor:
                self._canvas.configure(cursor=cursor)
                if self._text_label is not None:
                    self._text_label.configure(cursor=cursor)
                self._cursor_cache = cursor
