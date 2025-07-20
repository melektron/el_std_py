"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 01:01
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

tests for el.datastore
"""

import pytest
import typing
import logging
import tkinter as tk

from el.tkml.tk_element import tkc


_log = logging.getLogger(__name__)



def test_tkc_master_override():
    """
    Checks that the tke context manager works correctly
    """
    root = tk.Tk()
    root.configure(background="green")
    #root.pack_propagate(0)
    root.grid_columnconfigure(0, weight=1)
    with tkc(tk.Frame, root)(background="red") as e:
        e.grid(
            column=0, 
            row=0,
            padx=10,
            sticky="ew"
        )
        with tkc(tk.Button)(text="Hello, world!") as b:
            b.pack(
                padx=10,
                pady=10
            )
    
    root.mainloop()



