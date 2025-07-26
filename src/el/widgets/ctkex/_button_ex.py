"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
26.07.25, 13:36
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import sys
import typing
from .._deps import *

from el.observable import Observable
from el.widgets import CTkToolTip
from el.ctk_utils.types import *


class _CTkButtonPassthroughArgs(typing.TypedDict):
    width: int = 140,
    height: int = 28,
    corner_radius: typing.Optional[int] = None,
    border_width: typing.Optional[int] = None,
    border_spacing: int = 2,

    bg_color: Color = "transparent",
    fg_color: typing.Optional[Color] = None,
    hover_color: typing.Optional[Color] = None,
    border_color: typing.Optional[Color] = None,
    text_color: typing.Optional[Color] = None,
    text_color_disabled: typing.Optional[Color] = None,

    background_corner_colors: typing.Optional[tuple[Color]] = None,
    round_width_to_even_numbers: bool = True,
    round_height_to_even_numbers: bool = True,

    text: str = "CTkButton",
    font: typing.Optional[FontArgType] = None,
    textvariable: typing.Optional[tk.Variable] = None,
    image: ImageArgType = None,
    state: StateType = "normal",
    hover: bool = True,
    command: typing.Union[typing.Callable[[], typing.Any], None] = None,
    compound: CompoundType = "left",
    anchor: AnchorType = "center",

class CTkButtonExPassthroughArgs(_CTkButtonPassthroughArgs):
    touchscreen_mode: bool = False


class CTkButtonEx(ctk.CTkButton):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: bool = False,
        **kwargs: typing.Unpack[_CTkButtonPassthroughArgs]
    ):
        self._touchscreen_mode = touchscreen_mode
        super().__init__(master, **kwargs)


    @typing.override
    def _clicked(self, event=None):
        if self._state != tk.DISABLED:
            # click animation: change color with .on_leave() and back to normal after 100ms with click_animation()
            # edit in ctkex: If hovering is disabled or we are in touchscreen mode, we invert the animation 
            # so click is still visible (_click_animation is also modified)
            self._click_animation_running = True    # important: must be set before _on_enter so it renders
            if self._touchscreen_mode or not self._hover:
                self._on_enter()
            else:
                self._on_leave()
            self._click_animation_running = True    # important: must be after _on_leave as it resets this flag but we still need it for _click_animation
            self.after(100, self._click_animation)

            if self._command is not None:
                self._command()

    @typing.override
    def _on_enter(self, event=None):
        # when the animation is active we enable hover temporarily just enough to
        # execute the color change once to show the click animation, even when
        # in touchscreen mode or when hovering is normally disabled
        if self._click_animation_running and (self._touchscreen_mode or not self._hover):
            hover_before = self._hover
            self._hover = True
            super()._on_enter(event)
            # we reset to previous state as hover may have been enabled
            # and we were just in touchscreen mode, so we don't want to force it off
            self._hover = hover_before
        
        # if we are not in animation AND not in touchscreen mode we run the regular
        # _on_enter handler. That one will then check for whether hover is enabled or not.
        elif not self._touchscreen_mode:
            super()._on_enter(event)
        # if we are in touchscreen mode we don't do the animation

    @typing.override
    def _click_animation(self):
        if self._click_animation_running:
            # edit in ctkex: when in TS mode or hovering otherwise disabled,
            # we invert the animation
            if self._touchscreen_mode or not self._hover:
                self._on_leave()
            else:
                self._on_enter()
            # click animation finished

    @typing.override
    def configure(
        self,
        require_redraw=False,
        **kwargs: typing.Unpack[CTkButtonExPassthroughArgs],
    ):
        if "touchscreen_mode" in kwargs:
            self._touchscreen_mode = kwargs.pop("touchscreen_mode")
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
        """ Override this to allow for disable cursor in touchscreen mode """
        if self._cursor_manipulation_enabled:   # This seems to be hardcoded to true... what's the point?
            if self._touchscreen_mode:
                self.configure(cursor="none")
            else:
                # when disabling ts mode we first set a default cursor
                self.configure(cursor="")
                # then we override it some more based on OS (done by the standard impl)
                super()._set_cursor()