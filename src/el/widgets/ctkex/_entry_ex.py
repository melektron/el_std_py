"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
27.07.25, 22:09
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 
"""

import math
import typing
from .._deps import *

from el.observable import MaybeObservable, maybe_observe, maybe_obs_value
from el.callback_manager import CallbackManager
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config


class _CTkEntryPassthroughArgs(typing.TypedDict, total=False):
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
    font: typing.Optional[FontArgType]
    state: StateType

    justify: JustifyType

class CTkEntryExPassthroughArgs(_CTkEntryPassthroughArgs, total=False):
    touchscreen_mode: MaybeObservable[bool]
    background_corner_colors: tuple[Color]
    round_width_to_even_numbers: bool
    round_height_to_even_numbers: bool
    round_corner_exclude: tuple[bool, bool, bool, bool]


class CTkEntryEx(ctk.CTkEntry):

    def __init__(self,
        master: tk.Widget,
        touchscreen_mode: MaybeObservable[bool] = False,
        background_corner_colors: tuple[Color] | None = None,
        round_width_to_even_numbers: bool = True,
        round_height_to_even_numbers: bool = True,
        round_corner_exclude: tuple[bool, bool, bool, bool] = (False, False, False, False),
        **kwargs: typing.Unpack[_CTkEntryPassthroughArgs]
    ):
        self._touchscreen_mode = maybe_obs_value(touchscreen_mode)
        maybe_observe(
            touchscreen_mode, 
            apply_to_config(self, "touchscreen_mode"), 
            initial_update=False,
        )
        self._background_corner_colors = background_corner_colors
        # rendering options
        self._round_corner_exclude = round_corner_exclude
        self._round_width_to_even_numbers = round_width_to_even_numbers  # rendering options for DrawEngine
        self._round_height_to_even_numbers = round_height_to_even_numbers  # rendering options for DrawEngine
        #      ^ these are set on the drawing engine in _draw(), as we cannot otherwise hook that easily before drawing.

        # callback managers to provide other derived widgets the ability
        # to add persistent bindings for <FocusIn> or <FocusOut> that would
        # normally be removed when external bindings are removed
        self.persistent_on_focus_in = CallbackManager[tk.Event | None]()
        self.persistent_on_focus_out = CallbackManager[tk.Event | None]()

        super().__init__(master, **kwargs)

        self._set_cursor()

    @typing.override
    def _draw(self, no_color_updates: bool = False):
        """
        Override drawing method to implement round_corner_exclude and
        patch in background_corner_colors from CTkButton
        """
        # first we configure the drawing engine with the patched rounding options
        self._draw_engine.set_round_to_even_numbers(self._round_width_to_even_numbers, self._round_height_to_even_numbers)  # rendering options

        # then we patch in the bgcolor drawing from CTkButton
        if self._background_corner_colors is not None:
            self._draw_engine.draw_background_corners(self._apply_widget_scaling(self._current_width),
                                                      self._apply_widget_scaling(self._current_height))
            self._canvas.itemconfig("background_corner_top_left", fill=self._apply_appearance_mode(self._background_corner_colors[0]))
            self._canvas.itemconfig("background_corner_top_right", fill=self._apply_appearance_mode(self._background_corner_colors[1]))
            self._canvas.itemconfig("background_corner_bottom_right", fill=self._apply_appearance_mode(self._background_corner_colors[2]))
            self._canvas.itemconfig("background_corner_bottom_left", fill=self._apply_appearance_mode(self._background_corner_colors[3]))
        else:
            self._canvas.delete("background_parts")

        # then we draw the normal entry things
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
            if self._apply_appearance_mode(self._fg_color) == "transparent":
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
    def _entry_focus_in(self, event: tk.Event | None = None):
        super()._entry_focus_in(event)
        self.persistent_on_focus_in.notify_all(event)
    
    @typing.override
    def _entry_focus_out(self, event: tk.Event | None = None):
        super()._entry_focus_out(event)
        self.persistent_on_focus_out.notify_all(event)

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
            self.configure(cursor="")
            self._entry.configure(cursor="xterm")