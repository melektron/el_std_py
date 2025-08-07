"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 01:01
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

tests for el.tkml.

Be warned: some wild creatures are lurking in this file:
  Tests with GUI windows.
"""

import pytest
import typing
import logging
import tkinter as tk

from el.tkml._context import _master_ctx, _grid_next_column_ctx, _grid_next_row_ctx
from el.tkml.adapters import tkr, tkc, tkl, tku, stringvar_adapter, intvar_adapter, doublevar_adapter, boolvar_adapter
from el.tkml.grid import add_column, add_row, next_column, next_row, grid_layout
from el.observable import Observable

_log = logging.getLogger(__name__)


def test_tkr():
    with tkr(tk.Tk)(baseName="test") as m:
        assert _master_ctx.get() is m
        m.destroy()
    assert _master_ctx.get() is None

def test_tkc_master_override():
    """
    Checks that the tkc context manager works correctly
    (when overriding the master or not)
    """
    root = tk.Tk()
    #root.configure(background="green")
    #root.grid_columnconfigure(0, weight=1)
    assert _master_ctx.get() is None
    with tkc(tk.Frame, root)(background="red") as e:
        assert _master_ctx.get() is e
        e.grid(column=0, row=0, padx=10, sticky="ew")
        with tkc(tk.Button)(text="Hello, world!") as b:
            assert _master_ctx.get() is b
            b.pack(padx=10, pady=10)
        assert _master_ctx.get() is e
    assert _master_ctx.get() is None
    #root.mainloop()

def test_tkc_master_missing():
    """
    check for ValueError when TKML container is missing
    a contextual master.
    """
    with pytest.raises(ValueError) as exec_info:
        with tkc(tk.Frame)(background="red") as e:
            e.grid(column=0, row=0, padx=10, sticky="ew")

def test_tkl_master_missing():
    """
    check for ValueError when TKML leaf is missing
    a contextual master.
    """
    with pytest.raises(ValueError) as exec_info:
        assert _master_ctx.get() is None
        b = tkl(tk.Button)(text="test")
    assert _master_ctx.get() is None

def test_tku_new_grid():
    master = tk.Tk()
    column_token = _grid_next_column_ctx.set(1)
    row_token = _grid_next_row_ctx.set(1)
    with tku(master) as m:
        assert _grid_next_column_ctx.get() == 0
        assert _grid_next_row_ctx.get() == 0
        assert _master_ctx.get() is m
        assert _master_ctx.get() is master
        assert master is m
        m.destroy()
    assert _grid_next_column_ctx.get() == 1
    assert _grid_next_row_ctx.get() == 1
    assert _master_ctx.get() is None
    _grid_next_column_ctx.reset(column_token)
    _grid_next_row_ctx.reset(row_token)
    assert _grid_next_column_ctx.get() == 0
    assert _grid_next_row_ctx.get() == 0

def test_tku_no_new_grid():
    master = tk.Tk()
    column_token = _grid_next_column_ctx.set(1)
    row_token = _grid_next_row_ctx.set(1)
    with tku(master, new_grid=False) as m:
        assert _grid_next_column_ctx.get() == 1
        assert _grid_next_row_ctx.get() == 1
        assert _master_ctx.get() is m
        assert _master_ctx.get() is master
        assert master is m
        m.destroy()
    assert _grid_next_column_ctx.get() == 1
    assert _grid_next_row_ctx.get() == 1
    assert _master_ctx.get() is None
    _grid_next_column_ctx.reset(column_token)
    _grid_next_row_ctx.reset(row_token)
    assert _grid_next_column_ctx.get() == 0
    assert _grid_next_row_ctx.get() == 0


def test_grid_by_columns():
    """
    Tests the grid placement functions by
    placing in row directions.
    """
    assert _grid_next_column_ctx.get() == 0
    assert _grid_next_row_ctx.get() == 0
    with tkr(tk.Tk)() as w:
        assert _grid_next_column_ctx.get() == 0
        assert _grid_next_row_ctx.get() == 0
        b1 = add_row(tkl(tk.Button)(text="b1"), sticky="nsew")
        assert _grid_next_column_ctx.get() == 0
        assert _grid_next_row_ctx.get() == 1
        b2 = add_row(tkl(tk.Button)(text="b2"), sticky="nsew")
        assert _grid_next_column_ctx.get() == 0
        assert _grid_next_row_ctx.get() == 2
        b3 = add_row(tkl(tk.Button)(text="b3"), rowspan=2, sticky="nsew")
        assert _grid_next_column_ctx.get() == 0
        assert _grid_next_row_ctx.get() == 4

        next_column()
        assert _grid_next_column_ctx.get() == 1
        assert _grid_next_row_ctx.get() == 0
        b4 = add_row(tkl(tk.Button)(text="b4"), rowspan=2, sticky="nsew")
        assert _grid_next_column_ctx.get() == 1
        assert _grid_next_row_ctx.get() == 2
        b8 = add_row(tkl(tk.Button)(text="b8"), sticky="nsew")
        assert _grid_next_column_ctx.get() == 1
        assert _grid_next_row_ctx.get() == 3
        b5 = add_row(tkl(tk.Button)(text="b5"), sticky="nsew")
        assert _grid_next_column_ctx.get() == 1
        assert _grid_next_row_ctx.get() == 4

        next_column(reset_row=False)
        assert _grid_next_column_ctx.get() == 2
        assert _grid_next_row_ctx.get() == 4
        b6 = add_row(tkl(tk.Button)(text="b6"), sticky="nsew")
        assert _grid_next_column_ctx.get() == 2
        assert _grid_next_row_ctx.get() == 5
        b7 = add_row(tkl(tk.Button)(text="b7"), sticky="nsew")
        assert _grid_next_column_ctx.get() == 2
        assert _grid_next_row_ctx.get() == 6

        # also test grid-arranging containers
        # (these create sub grid-contexts but must place
        # themselves in the parent grid context requires passing a placement function)
        next_column()
        assert _grid_next_column_ctx.get() == 3
        assert _grid_next_row_ctx.get() == 0
        with tkc(tk.Frame, placement=(lambda e: add_row(e, sticky="nsew")))(
            background="green"
        ) as f:
            assert _grid_next_column_ctx.get() == 0
            assert _grid_next_row_ctx.get() == 0
            b9 = add_row(tkl(tk.Button)(text="b9"), sticky="nsew", padx=5, pady=5)
            assert _grid_next_column_ctx.get() == 0
            assert _grid_next_row_ctx.get() == 1
            b10 = add_row(tkl(tk.Button)(text="b10"), sticky="nsew", padx=5, pady=5)
            assert _grid_next_column_ctx.get() == 0
            assert _grid_next_row_ctx.get() == 2

        #w.mainloop()
    assert _grid_next_column_ctx.get() == 0
    assert _grid_next_row_ctx.get() == 0

# TODO: test for grid by row


def test_grid_layout():
    """
    Tests the grid_layout() placement function.
    """
    with tkr(tk.Tk)() as w:
        b1 = tkl(tk.Button)(text="b1")
        b1.grid(sticky="nsew")
        b2 = tkl(tk.Button)(text="b2")
        b2.grid(sticky="nsew")
        b3 = tkl(tk.Button)(text="b3")
        b3.grid(sticky="nsew")

        next_column()
        b4 = tkl(tk.Button)(text="b4")
        b4.grid(sticky="nsew")
        b8 = tkl(tk.Button)(text="b8")
        b8.grid(sticky="nsew")
        b5 = tkl(tk.Button)(text="b5")
        b5.grid(sticky="nsew")

        next_column(reset_row=False)
        b6 = tkl(tk.Button)(text="b6")
        b6.grid(sticky="nsew")
        b7 = tkl(tk.Button)(text="b7")
        b7.grid(sticky="nsew")

        # also test grid-arranging containers
        # (these create sub grid-contexts but must place
        # themselves in the parent grid context requires passing a placement function)
        next_column()
        with tkc(tk.Frame)( #placement=(lambda e: add_row(e, sticky="nsew"))
            background="green"
        ) as f:
            frame = f
            b9 = add_row(tkl(tk.Button)(text="b9"), sticky="nsew", padx=5, pady=5)
            b10 = add_row(tkl(tk.Button)(text="b10"), sticky="nsew", padx=5, pady=5)
        
        grid_layout(
            (b1,   b4,   None, frame),
            (b2,   b4,   None, ),
            (b3,   b8,   None, ),
            (b3,   b5,   None, ),
            (None, None, b6    ),
            (None, None, b7    ),
        )
        #w.mainloop()


def test_stringvar_adapter():
    with tku(tk.Tk()):
        obs = Observable[str]("")
        var = stringvar_adapter(obs)
        assert obs.value == ""
        assert var.get() == ""
        obs.value = "1"
        assert var.get() == "1"
        var.set("2")
        assert obs.value == "2"

def test_intvar_adapter():
    with tku(tk.Tk()):
        obs = Observable[int](0)
        var = intvar_adapter(obs)
        assert obs.value == 0
        assert var.get() == 0
        obs.value = 1
        assert var.get() == 1
        var.set(2)
        assert obs.value == 2

def test_doublevar_adapter():
    with tku(tk.Tk()):
        obs = Observable[float](0.1)
        var = doublevar_adapter(obs)
        assert obs.value == 0.1
        assert var.get() == 0.1
        obs.value = 1.1
        assert var.get() == 1.1
        var.set(2.1)
        assert obs.value == 2.1

def test_boolvar_adapter():
    with tku(tk.Tk()):
        obs = Observable[bool](False)
        var = boolvar_adapter(obs)
        assert obs.value == False
        assert var.get() == False
        obs.value = True
        assert var.get() == True
        var.set(False)
        assert obs.value == False

