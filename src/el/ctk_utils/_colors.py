"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
08.10.24, 09:19
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Utility functions to access various theme dependent colors and convert
them according to the active appearance mode
"""

from typing import Literal, Sequence
from ._deps import *

from el.observable import Observable, MaybeObservable
from .types import Color


def homogenize_color_types(
    color: str | tuple[str] | bytes | bytearray | Sequence[str],
) -> Color:
    """
    Ensures that a color value is either a tuple or a string, not any other iterable or
    string variant.
    """
    if isinstance(color, str):
        return color
    elif isinstance(color, (bytes, bytearray)):
        return color.decode()
    elif (
        isinstance(color, Sequence)
        and len(color) == 2
        and isinstance(color[0], str)
        and isinstance(color[1], str)
    ):
        return tuple(color)
    else:
        raise ValueError(
            f"Color {color} of type {type(color)} cannot be homogenized to 'str' or 'tuple[str, str]'"
        )

def apply_apm(color: Color, mode: Literal["Light", "Dark"] | None = None) -> str:
    """
    Takes in a CTk color (= single color string or a pair of color strings)
    and returns a single color string depending on the appearance mode. (one
    of the two if it is a pair)
    If no appearance mode is provided, the currently active mode will be used
    """
    match color:
        case str():
            return color
        case tuple():
            mode = mode or ctk.get_appearance_mode()
            return color[0] if mode == "Light" else color[1]
        case _:
            raise TypeError(f"argument 'color' must be a string or a tuple of two strings")

def apply_apm_observed(color: MaybeObservable[Color]) -> Observable[str]:
    """
    Observable factory that applies the current ctk appearance mode (light or dark)
    to the provided color value, to select the correct color to display. This is 
    useful to automatically distinguish and switch between a dark mode and a light
    mode color depending on the selected appearance mode.

    This factory always returns a single, observable tkinter color string that
    is dependant on the apm (=appearance mode) and will update automatically when 
    the apm changes, as long as the input color is a tuple of dark and light variants.

    Color can be provided in the following formats:
     - str: just a single, fixed color. It will be wrapped in an observable and
       returned immediately, as there is nothing to select depending on appearance mode.
     - tuple[str, str]: fixed light mode and fixed dark mode color. The returned observable 
       will always contain the correct color depending on appearance mode. This is the option
       commonly used when reading ctk theme colors.
     - Observable[str | tuple[str, str]]: When the input is another observable containing
       either a single color or a pair of colors, the output observable additionally changes when 
       the input observable changes. The input value can dynamically change between one color and 
       a color pair, where the correct value will be used according to apm if the input is a color pair.
    """
    # If there is just one color, we cannot track anything
    if isinstance(color, str):
        return Observable(color)
    
    obs = Observable("")

    match color:
        case tuple():
            def mode_changed(mode: str) -> None:
                obs.value = apply_apm(color, mode)
            ctk.AppearanceModeTracker.add(mode_changed)

        case Observable():
            current_color: Color = color.value
            current_mode: str = ctk.get_appearance_mode()

            def color_changed(new_color: Color) -> None:
                nonlocal current_color
                current_color = new_color
                obs.value = apply_apm(current_color, current_mode)
            color >> color_changed

            def mode_changed(mode: str) -> None:
                nonlocal current_mode
                current_mode = mode
                obs.value = apply_apm(current_color, current_mode)
            ctk.AppearanceModeTracker.add(mode_changed)
        
    return obs

def tk_to_rgb16(color_str: str, widget: tk.Tk | tk.Widget) -> tuple[int, int, int]:
    """
    Converts a tk color string to RGB using 'winfo rgb'. Therefore it 
    requires a tkinter widget to work. 
    """
    return widget.winfo_rgb(color_str)


def tk_to_rgb8(color_str: str, widget: tk.Tk | tk.Widget) -> tuple[int, int, int]:
    """
    Converts a tk color string to RGB using 'winfo rgb'. Therefore it 
    requires a tkinter widget to work. 
    """
    r, g, b = widget.winfo_rgb(color_str)
    return (r >> 8, g >> 8, b >> 8)


def rgb_to_hex_str(color_rgb: tuple[int, int, int]) -> str:
    """
    Creates a hex color string from RGB colors.
    """
    return f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"
