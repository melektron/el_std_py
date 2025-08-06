"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
01.08.25, 16:30
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Configurable SpinBox implementations made from an entry, two buttons and a frame,
complete with observable support and touchscreen mode. 
"""

import typing
import pydantic

from el.observable import MaybeObservable, Observable, maybe_get_obs, maybe_obs_value
from el.observable.filters import ignore_errors
from el.lifetime import LifetimeManager
from el.ctk_utils.types import *
from el.ctk_utils import apply_to_config
from el.tkml.adapters import tku, tkl, stringvar_adapter
from el.tkml.grid import configure_next_column, add_column

from .ctkex import CTkEntryEx, CTkButtonEx
from ._deps import *



class SpinBox(ctk.CTkFrame, Observable[float]):
    def __init__(
        self,
        master: tk.Misc,
        width: int = 80,
        button_width: int = 30,
        height: int = 28,
        corner_radius: typing.Optional[int] = None,
        border_width: typing.Optional[int] = None,  # only for entry

        bg_color: Color = "transparent",
        fg_color_minus: typing.Optional[Color] = None,
        fg_color_plus: typing.Optional[Color] = None,
        fg_color_entry: typing.Optional[Color] = None,
        hover_color_minus: typing.Optional[Color] = None,
        hover_color_plus: typing.Optional[Color] = None,
        border_color: typing.Optional[Color] = None,    # only for entry
        text_color: typing.Optional[Color] = None,
        text_color_minus: typing.Optional[Color] = None,
        text_color_minus_disabled: typing.Optional[Color] = None,
        text_color_plus: typing.Optional[Color] = None,
        text_color_plus_disabled: typing.Optional[Color] = None,

        background_corner_colors: typing.Optional[tuple[Color]] = None,

        font: typing.Optional[FontArgType] = None,
        button_font: typing.Optional[FontArgType] = None,
        text_minus: str = "-",
        text_plus: str = "+",
        image_minus: ImageArgType = None,
        image_plus: ImageArgType = None,

        initial_value: float = 0.0,
        formatter: typing.Callable[[float], str] = lambda v: f"{v:.0f}",
        increments: float = 1.0,
        min_value: float = 0,
        max_value: float = float("inf"),

        state: StateType = "normal",
        hover: bool = True,
        command: typing.Union[typing.Callable[[float], typing.Any], None] = None,
        touchscreen_mode: MaybeObservable[bool] = False,
        round_corner_exclude: tuple[bool, bool, bool, bool] = (False, False, False, False),

        **kwargs,
    ):
        ctk.CTkFrame.__init__(
            self,
            master=master,
            bg_color=bg_color,
            fg_color="transparent",
            corner_radius=corner_radius,
            **kwargs
        )
        Observable.__init__(self, initial_value)

        self._border_width = ctk.ThemeManager.theme["CTkEntry"]["border_width"] if border_width is None else border_width
        self._border_color = ctk.ThemeManager.theme["CTkEntry"]["border_color"] if border_color is None else self._check_color_type(border_color)
        self._fg_color_minus = ctk.ThemeManager.theme["CTkButton"]["fg_color"] if fg_color_minus is None else self._check_color_type(fg_color_minus, transparency=True)
        self._fg_color_plus = ctk.ThemeManager.theme["CTkButton"]["fg_color"] if fg_color_plus is None else self._check_color_type(fg_color_plus, transparency=True)

        self._lifetime = LifetimeManager()
        self._entry_text = Observable[str]("")
        self._formatter = formatter
        self._increments = increments
        self._min_value = min_value
        self._max_value = max_value

        self._command = command

        with self._lifetime():
            self._entry_text << self.observe(ignore_errors(lambda v: self._formatter(v)))
            self << self._entry_text.observe(ignore_errors(float))
            self >> self._handle_change
        
        # build UI
        with self._lifetime():
            with tku(self):
                configure_next_column(uniform="buttons")
                self.button_minus = add_column(tkl(CTkButtonEx)(
                    height=height,
                    width=button_width,
                    corner_radius=corner_radius,
                    border_width=self._border_width,
                    bg_color=bg_color,
                    fg_color=fg_color_minus,
                    hover_color=hover_color_minus,
                    border_color=self._border_color,
                    text_color=text_color_minus,
                    text_color_disabled=text_color_minus_disabled,
                    background_corner_colors=(
                        background_corner_colors[0] if background_corner_colors is not None else self._bg_color,
                        self._border_color,
                        self._border_color,
                        background_corner_colors[3] if background_corner_colors is not None else self._bg_color,
                    ),
                    #background_corner_colors=(  # forward these if needed but split the corner colors up
                    #    background_corner_colors[0],
                    #    self._bg_color,
                    #    self._bg_color,
                    #    background_corner_colors[3],
                    #) if background_corner_colors is not None else None,
                    # DrawEngine rendering option (so that theres no gap between buttons, as is done in CTkSegmentedButton)
                    round_width_to_even_numbers=False,
                    font=button_font,
                    text=text_minus,
                    image=image_minus,
                    state=state,
                    hover=hover,
                    command=self._minus_command,
                    touchscreen_mode=touchscreen_mode,
                    round_corner_exclude=(
                        round_corner_exclude[0],
                        False, False,
                        round_corner_exclude[3],
                    )
                ))

                configure_next_column(weight=1)
                self.entry = add_column(tkl(CTkEntryEx)(
                    width=(width - 2*button_width),
                    height=height,
                    corner_radius=corner_radius,
                    border_width=border_width,
                    justify="center",

                    bg_color=bg_color,
                    fg_color=fg_color_entry,
                    border_color=border_color,
                    text_color=text_color,

                    textvariable=stringvar_adapter(self._entry_text),
                    font=font,
                    state=state,
                    touchscreen_mode=touchscreen_mode,
                    background_corner_colors=(
                        self._border_color,
                        self._border_color,
                        self._border_color,
                        self._border_color,
                    ),
                    round_width_to_even_numbers=False,
                    #round_corner_exclude=(True, False, False, False)
                ), sticky="ew")

                configure_next_column(uniform="buttons")
                self.button_plus = add_column(tkl(CTkButtonEx)(
                    height=height,
                    width=button_width,
                    corner_radius=corner_radius,
                    border_width=self._border_width,
                    bg_color=bg_color,
                    fg_color=fg_color_plus,
                    hover_color=hover_color_plus,
                    border_color=self._border_color,
                    text_color=text_color_plus,
                    text_color_disabled=text_color_plus_disabled,
                    background_corner_colors=(
                        self._border_color,
                        background_corner_colors[1] if background_corner_colors is not None else self._bg_color,
                        background_corner_colors[2] if background_corner_colors is not None else self._bg_color,
                        self._border_color,
                    ),
                    #background_corner_colors=(  # forward these if needed but split the corner colors up
                    #    self._bg_color,
                    #    background_corner_colors[1],
                    #    background_corner_colors[2],
                    #    self._bg_color,
                    #) if background_corner_colors is not None else None,
                    # DrawEngine rendering option (so that theres no gap between buttons, as is done in CTkSegmentedButton)
                    round_width_to_even_numbers=False,
                    font=button_font,
                    text=text_plus,
                    image=image_plus,
                    state=state,
                    hover=hover,
                    command=self._plus_command,
                    touchscreen_mode=touchscreen_mode,
                    round_corner_exclude=(
                        False,
                        round_corner_exclude[1],
                        round_corner_exclude[2],
                        False,
                    )
                ))

    def _minus_command(self) -> None:
        """ command handler for minus button """
        self.focus()
        if self.value <= self._min_value:
            return
        self.value -= self._increments

    def _plus_command(self) -> None:
        """ command handler for plus button """
        self.focus()
        if self.value >= self._max_value:
            return
        self.value += self._increments
    
    def _handle_change(self, v: float) -> None:
        if self._command is not None:
            self._command(v)
    
    @typing.override
    def destroy(self):
        self._lifetime.end()
        return super().destroy()
