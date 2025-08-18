"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
18.08.25, 17:06
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

TEsts for the keyboard widget
"""

import pytest
import tkinter as tk
import customtkinter as ctk

import el.widgets.ctkex as ex
from el.lifetime import LifetimeManager
from el.widgets.keyboard import Keyboard


def test_keyboard_registration_manual():
    """
    Tests whether callback listeners are properly added to
    and removed from entry widgets registered with the keyboard.
    """
    root = ctk.CTk()
    keyboard = Keyboard(
        master=root
    )
    entry = ex.CTkEntryEx(master=root)
    reg_id = keyboard.register_target(entry)
    assert entry.persistent_on_focus_in.callback_count == 1
    assert entry.persistent_on_focus_out.callback_count == 1
    assert len(keyboard._targets) == 1

    keyboard.unregister_target(reg_id)
    assert entry.persistent_on_focus_in.callback_count == 0
    assert entry.persistent_on_focus_out.callback_count == 0
    assert len(keyboard._targets) == 0


def test_keyboard_registration_automatic():
    """
    Tests whether callback listeners are properly added to
    and removed from entry widgets registered with the keyboard.
    """
    root = ctk.CTk()
    keyboard = Keyboard(
        master=root
    )
    entry = ex.CTkEntryEx(master=root)
    reg_id = keyboard.register_target(entry)
    assert entry.persistent_on_focus_in.callback_count == 1
    assert entry.persistent_on_focus_out.callback_count == 1
    assert len(keyboard._targets) == 1

    keyboard.destroy()
    assert entry.persistent_on_focus_in.callback_count == 0
    assert entry.persistent_on_focus_out.callback_count == 0
    assert len(keyboard._targets) == 0


def test_keyboard_registration_external():
    """
    Tests whether callback listeners are properly added to
    and removed from entry widgets registered with the keyboard.
    """
    lifetime = LifetimeManager()
    root = ctk.CTk()
    keyboard = Keyboard(
        master=root
    )
    entry1 = ex.CTkEntryEx(master=root)
    keyboard.register_target(entry1)
    entry2 = ex.CTkEntryEx(master=root)
    with lifetime():
        keyboard.register_target(entry2)
    assert entry1.persistent_on_focus_in.callback_count == 1
    assert entry1.persistent_on_focus_out.callback_count == 1
    assert entry2.persistent_on_focus_in.callback_count == 1
    assert entry2.persistent_on_focus_out.callback_count == 1
    assert len(keyboard._targets) == 2

    lifetime.end()
    # only the entry registered within the lifetime should be removed
    assert entry1.persistent_on_focus_in.callback_count == 1
    assert entry1.persistent_on_focus_out.callback_count == 1
    assert entry2.persistent_on_focus_in.callback_count == 0
    assert entry2.persistent_on_focus_out.callback_count == 0
    assert len(keyboard._targets) == 1



# idk how to test keyboard focus handling and key events
