"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
27.07.25, 11:42
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import sys
import typing
from .._deps import *

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config

from ._button_ex import CTkButtonEx


class _CTkSwitchPassthroughArgs(typing.TypedDict, total=False):
    width: int
    height: int
    switch_width: int
    switch_height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]
    button_length: typing.Optional[int]

    bg_color: Color
    fg_color: typing.Optional[Color]
    border_color: Color
    progress_color: typing.Optional[Color]
    button_color: typing.Optional[Color]
    button_hover_color: typing.Optional[Color]
    text_color: typing.Optional[Color]
    text_color_disabled: typing.Optional[Color]

    text: str
    font: typing.Optional[FontArgType]
    textvariable: typing.Optional[tk.Variable]
    onvalue: typing.Union[int, str]
    offvalue: typing.Union[int, str]
    variable: typing.Optional[tk.Variable]
    hover: bool
    command: typing.Optional[typing.Callable[[], typing.Any]]
    state: StateType

class CTkSwitchExPassthroughArgs(_CTkSwitchPassthroughArgs, total=False):
    touchscreen_mode: MaybeObservable[bool]


class CTkSwitchEx(ctk.CTkSwitch):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        **kwargs: typing.Unpack[_CTkSwitchPassthroughArgs]
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
    def _on_enter(self, event=0):
        # in touchscreen mode simply ignore the entering
        if not self._touchscreen_mode:
            super()._on_enter(event)

    @typing.override
    def _on_leave(self, event=0):
        if not self._touchscreen_mode:
            super()._on_leave(event)
        else:
            # we still reset the color of the button in touchscreen mode
            # to avoid getting stuck in the hover color, unless we have just
            # clicked and an animation is running in which case we would disturb that
            self._canvas.itemconfig(
                "slider_parts",
                fill=self._apply_appearance_mode(self._button_color),
                outline=self._apply_appearance_mode(self._button_color),
            )

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
                    if sys.platform == "darwin":
                        cursor = "arrow"
                    elif sys.platform.startswith("win"):
                        cursor = "arrow"
                elif self._state == tk.NORMAL:
                    if sys.platform == "darwin":
                        cursor = "pointinghand"
                    elif sys.platform.startswith("win"):
                        cursor = "hand2"
            # update cursor if it differs from the previous one
            # to avoid unnecessary flickers
            if self._cursor_cache != cursor:
                self.configure(cursor=cursor)
                self._canvas.configure(cursor=cursor)
                if self._text_label is not None:
                    self._text_label.configure(cursor=cursor)
                self._cursor_cache = cursor

    @typing.override
    def configure(self, **kwargs: typing.Unpack[CTkSwitchExPassthroughArgs]):
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
        super().configure(**kwargs)

    @typing.override
    def cget(self, attribute_name: str) -> typing.Any:
        if attribute_name == "touchscreen_mode":
            return self._touchscreen_mode
        else:
            return super().cget(attribute_name)
