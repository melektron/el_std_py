"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
27.07.25, 22:09
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import typing
from .._deps import *

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config


class _CTkEntryPassthroughArgs(typing.TypedDict):
    width: int
    height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]

    bg_color: Color
    fg_color: typing.Optional[Color]
    border_color: typing.Optional[Color]
    text_color: typing.Optional[Color]
    placeholder_text_color: typing.Optional[Color]

    textvariable: typing.Optional[tk.Variable]
    placeholder_text: typing.Optional[str]
    font: typing.Optional[FontArgType] = None,
    state: StateType = tk.NORMAL,

class CTkEntryExPassthroughArgs(_CTkEntryPassthroughArgs):
    touchscreen_mode: MaybeObservable[bool]


class CTkEntryEx(ctk.CTkEntry):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        **kwargs: typing.Unpack[_CTkEntryPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )
        super().__init__(master, **kwargs)
        self._set_cursor()

    @typing.override
    def configure(
        self,
        require_redraw=False,
        **kwargs: typing.Unpack[CTkEntryExPassthroughArgs],
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
        if self._touchscreen_mode:
            self.configure(cursor="none")
            self._entry.configure(cursor="none")
        else:
            self.configure(cursor="xterm")
            self._entry.configure(cursor="xterm")