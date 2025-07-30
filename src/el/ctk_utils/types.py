"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
26.07.25, 13:27
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Type definitions for various "magic values" and long types frequently
used in ctk widget parameters
"""

import typing
from ._deps import *

type Color = str | tuple[str, str]
type FontArgType = typing.Union[tuple, ctk.CTkFont]
type ImageArgType = typing.Union[ctk.CTkImage, "ImageTk.PhotoImage", None]

type AnchorType = typing.Literal["center", "n", "s", "e", "w"]
type JustifyType = typing.Literal["left", "center", "right"]
type CompoundType = typing.Literal["right", "left", "top", "bottom"]
type StateType = typing.Literal["normal", "disabled", "active"]

class GridRowColConfigArgs(typing.TypedDict, total=False):
    minsize: int
    weight: int
    uniform: str
    pad: int