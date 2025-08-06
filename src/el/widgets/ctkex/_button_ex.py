"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
26.07.25, 13:36
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


class _CTkButtonPassthroughArgs(typing.TypedDict, total=False):
    width: int
    height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]
    border_spacing: int

    bg_color: Color
    fg_color: typing.Optional[Color]
    hover_color: typing.Optional[Color]
    border_color: typing.Optional[Color]
    text_color: typing.Optional[Color]
    text_color_disabled: typing.Optional[Color]

    background_corner_colors: typing.Optional[tuple[Color]]
    round_width_to_even_numbers: bool
    round_height_to_even_numbers: bool

    text: str
    font: typing.Optional[FontArgType]
    textvariable: typing.Optional[tk.Variable]
    image: ImageArgType
    state: StateType
    hover: bool
    command: typing.Union[typing.Callable[[], typing.Any], None]
    compound: CompoundType
    anchor: AnchorType

class CTkButtonExPassthroughArgs(_CTkButtonPassthroughArgs, total=False):
    touchscreen_mode: MaybeObservable[bool]
    round_corner_exclude: tuple[bool, bool, bool, bool]


class CTkButtonEx(ctk.CTkButton):

    def __init__(self,
        master: tk.Misc,
        touchscreen_mode: MaybeObservable[bool] = False,
        round_corner_exclude: tuple[bool, bool, bool, bool] = (False, False, False, False),
        **kwargs: typing.Unpack[_CTkButtonPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )
        self._round_corner_exclude = round_corner_exclude
        super().__init__(master, **kwargs)

    @typing.override
    def _draw(self, no_color_updates: bool = False):
        """ Override drawing method to implement round_corner_exclude """
        # first we draw the normal parts
        super()._draw(no_color_updates)

        # then on top of that, we draw additional rectangles to cover up some
        # of the corners that we want to "exclude" from rounding.
        # First we calculate the width and height the same it is done in ctk_button.py and drawing_engine.py
        width = self._apply_widget_scaling(self._current_width)
        if self._round_width_to_even_numbers:
            width = math.floor(width / 2) * 2  # round (floor) _current_width and _current_height and restrict them to even values only
        height = self._apply_widget_scaling(self._current_height)
        if self._round_height_to_even_numbers:
            height = math.floor(height / 2) * 2
        border_width = round(self._apply_widget_scaling(self._border_width))

        requires_recoloring = False

        for i, exclude in enumerate(self._round_corner_exclude):
            # create border and inner rectangles to cover the selected corners
            if exclude:
                if not self._canvas.find_withtag(f"corner_cover_border_{i}"):
                    self._canvas.create_rectangle(
                        0, 0, 0, 0,
                        tags=(
                            f"corner_cover_border_{i}",
                            "corner_cover_border_parts",
                            "border_parts",
                        ),
                        width=0,
                    )
                    requires_recoloring = True
                if not self._canvas.find_withtag(f"corner_cover_inner_{i}"):
                    self._canvas.create_rectangle(
                        0, 0, 0, 0,
                        tags=(
                            f"corner_cover_inner_{i}",
                            "corner_cover_inner_parts",
                            "inner_parts",
                        ),
                        width=0,
                    )
                    requires_recoloring = True

                # position them properly
                self._canvas.coords(f"corner_cover_border_{i}", (
                    width if 1 <= i <= 2 else 0, 
                    height if i >= 2 else 0,
                    width / 2, height / 2
                ))
                self._canvas.coords(f"corner_cover_inner_{i}", (
                    (width - border_width) if 1 <= i <= 2 else border_width,
                    (height - border_width) if i >= 2 else border_width,
                    width / 2, height / 2
                ))

            # or if this corner is not needed (anymore), make sure it's parts are definitely deleted
            else:
                self._canvas.delete(f"corner_cover_border_{i}", f"corner_cover_inner_{i}")
        
        # raise the elements to ensure the cover parts are always on the top and
        # the inner parts are always above the border parts. Without this, visual
        # artifacts may occur after a redraw when the elements already exist.
        self._canvas.tag_raise("corner_cover_border_parts")
        self._canvas.tag_raise("corner_cover_inner_parts")

        # when parts are created, we also need to re-run the color setting procedure
        # done by super()._draw() to set the colors of the corner covers as well.
        # This has been copied from ctk_button.py.
        if no_color_updates is False or requires_recoloring:
            # set color for the button border parts (outline)
            self._canvas.itemconfig("border_parts",
                                    outline=self._apply_appearance_mode(self._border_color),
                                    fill=self._apply_appearance_mode(self._border_color))
            
            # set color for inner button parts
            if self._fg_color == "transparent":
                self._canvas.itemconfig("inner_parts",
                                        outline=self._apply_appearance_mode(self._bg_color),
                                        fill=self._apply_appearance_mode(self._bg_color))
            else:
                self._canvas.itemconfig("inner_parts",
                                        outline=self._apply_appearance_mode(self._fg_color),
                                        fill=self._apply_appearance_mode(self._fg_color))

            #self._canvas.itemconfig("corner_cover_border_parts",
            #                        fill="orange" if self._desired_width == self._current_width else "red")
            #self._canvas.itemconfig("corner_cover_inner_parts",
            #                        fill="lime" if self._desired_width == self._current_width else "green")

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
        """ Override this to allow for disable cursor in touchscreen mode """
        if self._cursor_manipulation_enabled:   # This seems to be hardcoded to true... what's the point?
            if self._touchscreen_mode:
                self.configure(cursor="none")
            else:
                # when disabling ts mode we first set a default cursor
                self.configure(cursor="")
                # then we override it some more based on OS (done by the standard impl)
                super()._set_cursor()
