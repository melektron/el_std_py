"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
09.10.24, 15:36
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for ctk_utils module
"""

from el.errors import SetupError

try:
    import customtkinter as ctk
    import tkinter as tk
    from PIL import ImageTk
except ImportError:
    raise SetupError("el.ctk_utils requires customtkinter and pillow (PIL). Please install them before using el.ctk_utils or any el modules depending on it.")