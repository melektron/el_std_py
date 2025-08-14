"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
10.10.24, 10:44
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Function to apply observable values to tk and ctk widget config options
"""

from typing import Literal, Callable
from ._deps import *


ConfigOptionName = Literal[
    # ctk.CTkButton(Ex)
    "corner_radius",
    "border_width",
    "border_spacing",
    "fg_color",
    "hover_color",
    "border_color",
    "text_color",
    "text_color_disabled",
    "background_corner_colors",
    "text",
    "font",
    "textvariable",
    "image",
    "state",
    "hover",
    "command",
    "compound",
    "anchor",
    "touchscreen_mode", # Ex
    # tk.Frame
    "background",
    "bd",
    "bg",
    "border",
    "borderwidth",
    "cursor",
    "height",
    "highlightbackground",
    "highlightcolor",
    "highlightthickness",
    "padx",
    "pady",
    "relief",
    "takefocus",
    "width",
    # ctk.CTkLabel
    "corner_radius",
    "fg_color",
    "text_color",
    "text_color_disabled",
    "text",
    "font",
    "image",
    "compound",
    "anchor",
    "wraplength",

    # widgets.SpinBox
    "min_value",
    "max_value",
]


def apply_to_config[
    PT
](widget: tk.Widget, config_name: ConfigOptionName) -> Callable[[PT], PT]:
    """
    Creates a function that applies observable values to a tk/ctk config option dynamically.
    """

    def set_opt(data: PT) -> PT:
        widget.configure(**{config_name: data})
        return data

    return set_opt


def apply_to_tk_var[PT](variable: tk.Variable) -> Callable[[PT], PT]:
    """
    Creates a function that applies observable values to tkinter variables dynamically.
    """

    def set_var(data: PT) -> PT:
        variable.set(data)
        return data

    return set_var
