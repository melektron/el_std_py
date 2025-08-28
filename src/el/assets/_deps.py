"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
28.08.25, 14:06
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for assets module
"""

from el.errors import SetupError

try:
    import customtkinter as ctk
    import tkinter as tk
    from PIL import Image
    import numpy as np
except ImportError:
    raise SetupError("el.assets requires customtkinter, pillow (PIL) and numpy. Please install them before using el.assets or any el modules depending on it.")