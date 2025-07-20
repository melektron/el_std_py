"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
20.07.25, 16:17
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for tkml module
"""

from el.errors import SetupError

try:
    #import customtkinter as ctk
    #from customtkinter.windows.widgets.scaling import CTkScalingBaseClass
    import tkinter as tk
    #import PIL as pil
except ImportError:
    raise SetupError("el.tkml requires tkinter. Please install it before using el.tkml.")
    #raise SetupError("el.widgets requires customtkinter and pillow (PIL). Please install them before using el.widgets.")