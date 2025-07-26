"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
26.07.25, 18:14
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import typing
from .._deps import *

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config

from ._button_ex import CTkButtonEx


class _CTkSegmentedButtonPassthroughArgs(typing.TypedDict):
    width: int = 140,
    height: int = 28,
    corner_radius: typing.Optional[int] = None,
    border_width: int = 3,

    bg_color: Color = "transparent",
    fg_color: typing.Optional[Color] = None,
    selected_color: typing.Optional[Color] = None,
    selected_hover_color: typing.Optional[Color] = None,
    unselected_color: typing.Optional[Color] = None,
    unselected_hover_color: typing.Optional[Color] = None,
    text_color: typing.Optional[Color] = None,
    text_color_disabled: typing.Optional[Color] = None,
    background_corner_colors: typing.Optional[tuple[Color]] = None,

    font: typing.Optional[FontArgType] = None,
    values: typing.Optional[list[str]] = None,
    variable: typing.Optional[tk.Variable] = None,
    dynamic_resizing: bool = True,
    command: typing.Optional[typing.Callable[[str], typing.Any]] = None,
    state: StateType = "normal"

class CTkSegmentedButtonExPassthroughArgs(_CTkSegmentedButtonPassthroughArgs):
    touchscreen_mode: MaybeObservable[bool] = False


class CTkSegmentedButtonEx(ctk.CTkSegmentedButton):

    # change type-hint of button dict
    _buttons_dict: dict[str, CTkButtonEx]

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        **kwargs: typing.Unpack[_CTkSegmentedButtonPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )
        super().__init__(master, **kwargs)

    @typing.override
    def _create_button(self, index: int, value: str) -> CTkButtonEx:
        """ 
        Replace the default buttons with CTkButtonEx which
        support touchscreen mode.
        """
        return CTkButtonEx(
            self,
            width=0,
            height=self._current_height,
            corner_radius=self._sb_corner_radius,
            border_width=self._sb_border_width,
            fg_color=self._sb_unselected_color,
            border_color=self._sb_fg_color,
            hover_color=self._sb_unselected_hover_color,
            text_color=self._sb_text_color,
            text_color_disabled=self._sb_text_color_disabled,
            text=value,
            font=self._font,
            state=self._state,
            command=lambda v=value: self.set(v, from_button_callback=True),
            background_corner_colors=None,
            round_width_to_even_numbers=False,
            round_height_to_even_numbers=False,
            touchscreen_mode=self._touchscreen_mode # pass touchscreen mode to the buttons
        )  # DrawEngine rendering option (so that theres no gap between buttons)

    @typing.override
    def configure(self, **kwargs: typing.Unpack[CTkSegmentedButtonExPassthroughArgs]):
        """ 
        Change configuration options dynamically. When changing any
        MaybeObservable attributes with an Observable, the attribute
        will only be set once and not observed. This is intended for
        changing options without Observables.
        """
        if "touchscreen_mode" in kwargs:
            self._touchscreen_mode = maybe_obs_value(kwargs["touchscreen_mode"])
            kwargs.pop("touchscreen_mode")
            # update all the buttons' touchscreen mode
            for btn in self._buttons_dict.values():
                btn.configure(touchscreen_mode=self._touchscreen_mode)
        super().configure(**kwargs)

    @typing.override
    def cget(self, attribute_name: str) -> typing.Any:
        if attribute_name == "touchscreen_mode":
            return self._touchscreen_mode
        else:
            return super().cget(attribute_name)
