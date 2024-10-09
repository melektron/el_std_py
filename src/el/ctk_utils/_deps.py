"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
09.10.24, 15:36
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for datastore module
"""

from el.errors import SetupError

try:
    import customtkinter as ctk
    import tkinter as tk
except ImportError:
    raise SetupError("el.ctk_utils requires customtkinter. Please install it before using el.ctk_utils.")