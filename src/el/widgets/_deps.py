"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
01.11.24, 17:05
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for widget module
"""

from el.errors import SetupError

try:
    import customtkinter as ctk
    from customtkinter.windows.widgets.scaling import CTkScalingBaseClass
    from customtkinter.windows.widgets.appearance_mode import CTkAppearanceModeBaseClass
    import tkinter as tk
    #import PIL as pil
except ImportError:
    raise SetupError("el.widgets requires customtkinter. Please install it before using el.widgets.")
    #raise SetupError("el.widgets requires customtkinter and pillow (PIL). Please install them before using el.widgets.")