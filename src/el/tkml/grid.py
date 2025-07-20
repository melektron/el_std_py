"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
20.07.25, 23:07
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

wrappers around the grid geometry manager to automatically count
rows/columns in context
"""


import logging
import functools
from typing import Callable, Concatenate, Generator, ContextManager
from contextlib import contextmanager, AbstractContextManager
from contextvars import ContextVar, Token

from ._deps import *
from ._context import _grid_next_column_ctx, _grid_next_row_ctx

_log = logging.getLogger(__name__)

type ScreenUnits = str | float


def add_row[WT: tk.Widget](
    widget: WT,
    columnspan: int | None = None,
    rowspan: int | None = None,
    rowspan_increment: bool = True,
    ipadx: ScreenUnits | None = None,
    ipady: ScreenUnits | None = None,
    padx: ScreenUnits | tuple[ScreenUnits, ScreenUnits] | None = None,
    pady: ScreenUnits | tuple[ScreenUnits, ScreenUnits] | None = None,
    sticky: str | None = None,
) -> WT:
    """
    Positions a widget in the parent widget in the next row
    of a grid container. The row and column are determined from TKML context.
    The next row is incremented after the widget is placed, while the column 
    stays the same.
    
    Parameters
    ----------
    widget : tk.Widget
        the widget to place
    columnspan : int, optional
        How many columns to the right the widget should span. 
        By default 1 (the current column).
    rowspan : int, optional
        How many rows down the widget should span. By default only 1.
    rowspan_increment : bool, optional
        If enabled (default), the next row is incremented by the number
        passed to `rowspan` (if applicable) so the next widget will be 
        placed the row AFTER all the ones spanned by this widget. Set this 
        to false to not account for rowspan.
    ipadx : ScreenUnits, optional
        internal padding in x direction
    ipady : ScreenUnits, optional
        internal padding in y direction
    padx : ScreenUnits | tuple[ScreenUnits, ScreenUnits], optional
        external padding in x direction
    pady : ScreenUnits | tuple[ScreenUnits, ScreenUnits], optional
        external padding in y direction
    sticky : str, optional
        in what directions the widget should expand to fill the cell size. 
        Can be any combination of `n`, `s`, `e`, `w`
    
    Returns
    -------
    widget -> allows to use this function inline with widget creation
    """
    
    kwargs = dict()
    if columnspan is not None:
        kwargs["columnspan"] = columnspan
    if rowspan is not None:
        kwargs["rowspan"] = rowspan
    if ipadx is not None:
        kwargs["ipadx"] = ipadx
    if ipady is not None:
        kwargs["ipady"] = ipady
    if padx is not None:
        kwargs["padx"] = padx
    if pady is not None:
        kwargs["pady"] = pady
    if sticky is not None:
        kwargs["sticky"] = sticky
    
    kwargs["row"] = _grid_next_row_ctx.get()
    kwargs["column"] = _grid_next_column_ctx.get()

    if rowspan is not None and rowspan > 1 and rowspan_increment:
        _grid_next_row_ctx.set(_grid_next_row_ctx.get() + rowspan)
    else:
        _grid_next_row_ctx.set(_grid_next_row_ctx.get() + 1)

    widget.grid_configure(kwargs)

    return widget


def add_column[WT: tk.Widget](
    widget: WT,
    columnspan: int | None = None,
    columnspan_increment: bool = True,
    rowspan: int | None = None,
    ipadx: ScreenUnits | None = None,
    ipady: ScreenUnits | None = None,
    padx: ScreenUnits | tuple[ScreenUnits, ScreenUnits] | None = None,
    pady: ScreenUnits | tuple[ScreenUnits, ScreenUnits] | None = None,
    sticky: str | None = None,
) -> WT:
    """
    Positions a widget in the parent widget in the next column
    of a grid container. The row and column are determined from TKML context.
    The next column is incremented after the widget is placed, while the row 
    stays the same.
    
    Parameters
    ----------
    widget : tk.Widget
        the widget to place
    columnspan : int, optional
        How many columns to the right the widget should span.
        By default 1 (the current column).
    columnspan_increment : bool, optional
        If enabled (default), the next column is incremented by the number
        passed to `columnspan` (if applicable) so the next widget will be 
        placed the in column AFTER all the ones spanned by this widget. Set this 
        to false to not account for columnspan.
    rowspan : int, optional
        How many rows down the widget should span. By default only 1.
    ipadx : ScreenUnits, optional
        internal padding in x direction
    ipady : ScreenUnits, optional
        internal padding in y direction
    padx : ScreenUnits | tuple[ScreenUnits, ScreenUnits], optional
        external padding in x direction
    pady : ScreenUnits | tuple[ScreenUnits, ScreenUnits], optional
        external padding in y direction
    sticky : str, optional
        in what directions the widget should expand to fill the cell size. 
        Can be any combination of `n`, `s`, `e`, `w`
    
    Returns
    -------
    widget -> allows to use this function inline with widget creation
    """
    
    kwargs = dict()
    if columnspan is not None:
        kwargs["columnspan"] = columnspan
    if rowspan is not None:
        kwargs["rowspan"] = rowspan
    if ipadx is not None:
        kwargs["ipadx"] = ipadx
    if ipady is not None:
        kwargs["ipady"] = ipady
    if padx is not None:
        kwargs["padx"] = padx
    if pady is not None:
        kwargs["pady"] = pady
    if sticky is not None:
        kwargs["sticky"] = sticky
    
    kwargs["row"] = _grid_next_row_ctx.get()
    kwargs["column"] = _grid_next_column_ctx.get()

    if columnspan is not None and columnspan > 1 and columnspan_increment:
        _grid_next_column_ctx.set(_grid_next_column_ctx.get() + rowspan)
    else:
        _grid_next_column_ctx.set(_grid_next_column_ctx.get() + 1)

    widget.grid_configure(kwargs)
    
    return widget


def next_row(
    reset_column: bool = True
):
    """
    Moves the context on to the next row so 
    the following widgets are placed on a new grid row.
    This is meant to be used when placing widgets with `add_column`.

    Parameters
    ----------
    reset_column : bool, optional
        Whether the next column should be reset to zero, by default enabled.
        Set to false to not reset the next column and keep placing in the
        next row but at the same column.
    """
    
    _grid_next_row_ctx.set(_grid_next_row_ctx.get() + 1)
    if reset_column:
        _grid_next_column_ctx.set(0)


def next_column(
    reset_row: bool = True
):
    """
    Moves the context on to the next column so 
    the following widgets are placed in a new grid column.
    This is meant to be used when placing widgets with `add_row`.

    Parameters
    ----------
    reset_row : bool, optional
        Whether the next row should be reset to zero, by default enabled.
        Set to false to not reset the next row and keep placing in the
        next column but at the same row.
    """
    
    _grid_next_column_ctx.set(_grid_next_column_ctx.get() + 1)
    if reset_row:
        _grid_next_row_ctx.set(0)

    