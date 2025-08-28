"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
28.08.25, 15:52
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Tests for el.assets
"""

import os
import logging
from pathlib import Path

import customtkinter as ctk
import tkinter as tk

import el.nixos_ctk_font_fix
import el.assets
from el.assets import AssetManager, builtin


_log = logging.getLogger(__name__)


def test_builtin_loading():
    """
    Checks that all builtin asset files can be loaded
    using the asset manager
    """
    root = ctk.CTk()

    directory = Path(os.path.dirname(os.path.abspath(el.assets.__file__))) / "builtin"
    for file in directory.iterdir():
        if not file.is_file():
            continue    # only inspect files
        # try to load asset
        try:
            img = builtin.load_button_icon(root, file.name)
        except Exception as e:
            raise RuntimeError(f"Builtin asset `{file.name}` failed to load: {e}")


def test_default_size():
    """
    Checks that the default size is correctly applied
    """
    root = ctk.CTk()

    img = builtin.load_button_icon(root, "cancel.png")
    assert img._size == builtin.default_btn_icon_size


def test_size_override():
    """
    Checks that the size can be overridden
    """
    root = ctk.CTk()

    img = builtin.load_button_icon(root, "cancel.png", size=(32, 32))
    assert img._size != builtin.default_btn_icon_size, "should differ from default"
    assert img._size == (32, 32), "should be the specified size (scaling not yet applied)"


def test_colored_icon():
    """
    Checks that icon can be correctly colored with one color
    """
    root = ctk.CTk()

    img = builtin.load_colored_button_icon(root, "cancel.png", "red")
    assert img._light_image.resize((32, 32)).getpixel((15, 15)) == (255, 0, 0, 255), "center pixel should be red with full opacity"
    assert img._light_image.resize((32, 32)).getpixel((0, 15)) == (0, 0, 0, 0), "side pixel should be completely transparent"
    assert img._dark_image.resize((32, 32)).getpixel((15, 15)) == (255, 0, 0, 255), "center pixel should be red with full opacity"
    assert img._dark_image.resize((32, 32)).getpixel((0, 15)) == (0, 0, 0, 0), "side pixel should be completely transparent"
    

def test_colored_icon_aware():
    """
    Checks that icon can be correctly colored with two different colors
    for light and dark mode
    """
    root = ctk.CTk()

    img = builtin.load_colored_button_icon(root, "cancel.png", ("red", "#00ff00"))
    assert img._light_image.resize((32, 32)).getpixel((15, 15)) == (255, 0, 0, 255), "center pixel should be red with full opacity"
    assert img._light_image.resize((32, 32)).getpixel((0, 15)) == (0, 0, 0, 0), "side pixel should be completely transparent"
    assert img._dark_image.resize((32, 32)).getpixel((15, 15)) == (0, 255, 0, 255), "center pixel should be green with full opacity"
    assert img._dark_image.resize((32, 32)).getpixel((0, 15)) == (0, 0, 0, 0), "side pixel should be completely transparent"
