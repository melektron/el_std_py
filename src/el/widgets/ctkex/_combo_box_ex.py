"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
26.07.25, 18:52
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


class _CTkComboBoxPassthroughArgs(typing.TypedDict, total=False):
    width: int
    height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]

    bg_color: Color
    fg_color: typing.Optional[typing.Optional[Color]]
    border_color: typing.Optional[typing.Optional[Color]]
    button_color: typing.Optional[typing.Optional[Color]]
    button_hover_color: typing.Optional[typing.Optional[Color]]
    dropdown_fg_color: typing.Optional[typing.Optional[Color]]
    dropdown_hover_color: typing.Optional[typing.Optional[Color]]
    dropdown_text_color: typing.Optional[typing.Optional[Color]]
    text_color: typing.Optional[typing.Optional[Color]]
    text_color_disabled: typing.Optional[typing.Optional[Color]]

    font: typing.Optional[FontArgType]
    dropdown_font: typing.Optional[FontArgType]
    values: typing.Optional[list[str]]
    state: StateType
    hover: bool
    variable: typing.Optional[tk.Variable]
    command: typing.Optional[typing.Callable[[str], typing.Any]]
    justify: JustifyType

class CTkComboBoxExPassthroughArgs(_CTkComboBoxPassthroughArgs, total=False):
    touchscreen_mode: MaybeObservable[bool]


class CTkComboBoxEx(ctk.CTkComboBox):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        **kwargs: typing.Unpack[_CTkComboBoxPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )

        super().__init__(master, **kwargs)

        self._click_animation_running: bool = False
        
        # update cursor from ts mode right away
        self._update_cursor()

        # TODO: somehow patch DropdownMenu._configure_menu_for_platforms to prevent cursor
        # from being enabled in TS mode when scaling/appearance mode changes
        # Idea: override _set_appearance_mode and _set_scaling here and just call _update_cursor() every time

    @typing.override
    def _on_enter(self, event=0):
        # in touchscreen mode simply ignore the entering
        if not self._touchscreen_mode:
            super()._on_enter(event)
            # self._canvas.configure(cursor="hand2") # emulate windows behaviour for testing
        # update cursors which may have been changed by super()._on_enter()
        self._update_cursor(apply_defaults=False)   # only disable in TS mode, leave in normal mode

    @typing.override
    def _on_leave(self, event=0):
        if not self._touchscreen_mode:
            super()._on_leave(event)
            # self._canvas.configure(cursor="arrow") # emulate windows behaviour for testing
        elif not self._click_animation_running:
            # we still reset the color of the button in touchscreen mode
            # to avoid getting stuck in the hover color, unless we have just
            # clicked and an animation is running in which case we would disturb that
            self._canvas.itemconfig(
                "inner_parts_right",
                outline=self._apply_appearance_mode(self._button_color),
                fill=self._apply_appearance_mode(self._button_color),
            )
            self._canvas.itemconfig(
                "border_parts_right",
                outline=self._apply_appearance_mode(self._button_color),
                fill=self._apply_appearance_mode(self._button_color),
            )
        # update cursors which may have been changed by super()._on_leave()
        self._update_cursor(apply_defaults=False)   # only disable in TS mode, leave in normal mode

    @typing.override
    def _clicked(self, event=None):
        if self._touchscreen_mode:
            # in touchscreen mode we add a small click animation as it would
            # look unresponsive without the hover effect otherwise
            self._click_animation_running = True
            # set color of inner button parts to hover color
            self._canvas.itemconfig(
                "inner_parts_right",
                outline=self._apply_appearance_mode(self._button_hover_color),
                fill=self._apply_appearance_mode(self._button_hover_color),
            )
            self._canvas.itemconfig(
                "border_parts_right",
                outline=self._apply_appearance_mode(self._button_hover_color),
                fill=self._apply_appearance_mode(self._button_hover_color),
            )
            # end the animation in 100ms
            self.after(100, self._end_click_animation)

        super()._clicked(event)

    def _end_click_animation(self) -> None:
        self._click_animation_running = False
        # call leave callback which will reset the colors
        self._on_leave()

    def _update_cursor(self, apply_defaults: bool = True) -> None:
        """ Updates the cursor depending on touchscreen mode """
        if self._touchscreen_mode:
            # disable cursor in TS mode
            self.configure(cursor="none")
            self._canvas.configure(cursor="none")
            self._entry.configure(cursor="none")
            self._dropdown_menu.configure(cursor="none")
        elif apply_defaults:
            # set cursor to default when ts mode is disabled (may be overwritten later by other components)
            self.configure(cursor="")
            self._canvas.configure(cursor="")
            self._entry.configure(cursor="xterm")    # xterm is the tkinter entry default cursor
            self._dropdown_menu.configure(cursor="")

    @typing.override
    def configure(self, **kwargs: typing.Unpack[CTkComboBoxExPassthroughArgs]):
        """ 
        Change configuration options dynamically. When changing any
        MaybeObservable attributes with an Observable, the attribute
        will only be set once and not observed. This is intended for
        changing options without Observables.
        """
        if "touchscreen_mode" in kwargs:
            self._touchscreen_mode = maybe_obs_value(kwargs["touchscreen_mode"])
            kwargs.pop("touchscreen_mode")
            self._update_cursor()
        super().configure(**kwargs)

    @typing.override
    def cget(self, attribute_name: str) -> typing.Any:
        if attribute_name == "touchscreen_mode":
            return self._touchscreen_mode
        else:
            return super().cget(attribute_name)
