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

import typing
import logging

from el.ctk_utils.types import GridRowColConfigArgs
from ._deps import *
from ._context import _grid_next_column_ctx, _grid_next_row_ctx, _master_ctx

_log = logging.getLogger(__name__)

type ScreenUnits = str | float


def add_row[WT: tk.Widget](
    widget: WT,
    column_override: int | None = None,
    columnspan: int | None = None,
    rowspan: int | None = None,
    rowspan_increment: bool = True,
    row_increment: bool = True,
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
    column_override : int, optional
        Optional override of the column number. IF provided,
        the widget will be placed in this column instead of the contextually 
        determined one.
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
    row_increment : bool, optional
        If disabled, the row context will not be incremented at all. This is 
        useful (in combination with column_override) if you want to add a lot 
        of rows and sometimes add multiple things in the same row in different columns.
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
    kwargs["column"] = _grid_next_column_ctx.get() if column_override is None else column_override

    if row_increment:
        if rowspan is not None and rowspan > 1 and rowspan_increment:
            _grid_next_row_ctx.set(_grid_next_row_ctx.get() + rowspan)
        else:
            _grid_next_row_ctx.set(_grid_next_row_ctx.get() + 1)

    widget.grid(**kwargs)

    return widget


def add_column[WT: tk.Widget](
    widget: WT,
    columnspan: int | None = None,
    columnspan_increment: bool = True,
    column_increment: bool = True,
    row_override: int | None = None,
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
    column_increment : bool, optional
        If disabled, the column context will not be incremented at all. This is 
        useful (in combination with row_override) if you want to add a lot 
        of columns and sometimes add multiple things in the same column in different rows.
    row_override : int, optional
        Optional override of the row number. If provided,
        the widget will be placed in this row instead of the contextually 
        determined one.
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
    
    kwargs["row"] = _grid_next_row_ctx.get() if row_override is None else row_override
    kwargs["column"] = _grid_next_column_ctx.get()

    if column_increment:
        if columnspan is not None and columnspan > 1 and columnspan_increment:
            _grid_next_column_ctx.set(_grid_next_column_ctx.get() + rowspan)
        else:
            _grid_next_column_ctx.set(_grid_next_column_ctx.get() + 1)

    widget.grid(**kwargs)
    
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


def grid_layout(
    *rows: tuple[tk.Widget | None, ...]
) -> None:
    """
    Generates a grid layout for an entire container by calculating grid indices 
    of widgets from their locations in the provided arrays similar to CSS grid 
    template areas. 

    Example:
    ```python
    a = tkl(...)
    b = tkl(...)
    c = tkl(...)
    d = tkl(...)
    grid_layout(
        (a, a, b, c),
        (d, d, d, c)
    )
    ```

    Widgets can span multiple rows and/or columns which will result in their rowspan
    or columnspan being set. The span areas must be rectangular.

    If additional grid parameters need to be specified for specific widgets, they
    can be added using the `grid()` method directly (either before
    or after the `grid_layout()` call, doesn't matter) without passing row/column
    information to it. 
    
    This should not be mixed with calls to contextual TKML grid layout functions 
    such as `add_row()` etc. This layout method does not require any context and 
    could thus be used in a non-TKML environment as well.

    Parameters
    ----------
    *rows : tuple[tk.Widget | None, ...]
        Lists representing the rows of a grid.
        `None` represents an empty cell.

    Raises
    ------
    ValueError
        A widget are is not rectangular.
    """

    widget_positions: dict[tk.Widget, list[tuple[int, int]]] = {}
    # collect all the positions each widget was placed at
    for y, row in enumerate(rows):
        for x, widget in enumerate(row):
            if widget is None:  # skip empty cells
                continue
            if widget not in widget_positions:
                widget_positions[widget] = []
            widget_positions[widget].append((x, y))
    
    for widget, positions in widget_positions.items():
        # collect each column and row a widget appeared
        x_positions: set[int] = set()
        y_positions: set[int] = set()
        for position in positions:
            x_positions.add(position[0])
            y_positions.add(position[1])
        # widgets should always be grid positioned in a rectangular pattern,
        # thus the position should be representable by the x and y ranges
        x_range = range(min(x_positions), max(x_positions) + 1)
        y_range = range(min(y_positions), max(y_positions) + 1)
        # loop through all theoretical positions to ensure they actually
        # were present in the input set
        for x in x_range:
            for y in y_range:
                if (x, y) not in positions:
                    raise ValueError(f"Grid area occupied by widget {widget} is not rectangular: cell ({x}, {y}) is not assigned to this widget.")
        # if all areas are present, the placement is valid and to be executed
        widget.grid(
            column=min(x_positions),
            columnspan=(max(x_positions) - min(x_positions) + 1),
            row=min(y_positions),
            rowspan=(max(y_positions) - min(y_positions) + 1)
        )


def get_previous_column() -> int | None:
    """
    Returns
    -------
    The previous column that was added using add_column() or
    None if no column was added yet.
    """
    col = _grid_next_column_ctx.get()
    return col if col >= 0 else None


def get_previous_row() -> int | None:
    """
    Returns
    -------
    The previous row that was added using add_row() or
    None if no row was added yet.
    """
    
    row = _grid_next_row_ctx.get() - 1
    return row if row >= 0 else None


def configure_next_column(
    **kwargs: typing.Unpack[GridRowColConfigArgs]
) -> int | None:
    """
    Configures the next column of the contextual master that 
    would be placed using `add_column()`.
    See https://wiki.tcl-lang.org/page/grid+columnconfigure

    Parameters
    ----------
    minsize : int, optional
        The minimum size, in screen units, that will be permitted for this column.
    weight : int, optional
        The relative weight for apportioning any extra spaces among columns. 
        A weight of zero (0) indicates the column will not deviate from its 
        requested size. A column whose weight is two will grow at twice the 
        rate as a column of weight one when extra space is allocated to the layout.
        Keep in mind that equal weights does not mean the columns are the same width,
        just that they EXPAND in equal proportions. Use `uniform` to enforce width 
        proportions exactly.
    uniform : str, optional
        String identifying a uniform group the column is placed in. When a 
        value is supplied, places the column in a uniform group with other 
        columns that have the same value for `uniform`. The space for columns 
        belonging to a uniform group is allocated so that their sizes are 
        always in strict proportion to their `weight` values
    pad : int, optional
        The number of screen units that will be added to the largest window 
        contained completely in that column when the grid geometry manager 
        requests a size from the containing window.
    """
    local_master = _master_ctx.get()
    if local_master is None:
        raise ValueError("TKML configure_next_column is missing a contextual master. Only use this function in a container context that uses contextual grid.")
    local_master.grid_columnconfigure(_grid_next_column_ctx.get(), **kwargs)


def configure_next_row(
    **kwargs: typing.Unpack[GridRowColConfigArgs]
) -> int | None:
    """
    Configures the next row of the contextual master that 
    would be placed using `add_row()`.
    See https://wiki.tcl-lang.org/page/grid+rowconfigure

    Parameters
    ----------
    minsize : int, optional
        The minimum size, in screen units, that will be permitted for this row.
    weight : int, optional
        The relative weight for apportioning any extra spaces among rows. 
        A weight of zero (0) indicates the row will not deviate from its 
        requested size. A row whose weight is two will grow at twice the 
        rate as a row of weight one when extra space is allocated to the layout.
        Keep in mind that equal weights does not mean the rows are the same width,
        just that they EXPAND in equal proportions. Use `uniform` to enforce width 
        proportions exactly.
    uniform : str, optional
        String identifying a uniform group the row is placed in. When a 
        value is supplied, places the row in a uniform group with other 
        rows that have the same value for `uniform`. The space for rows 
        belonging to a uniform group is allocated so that their sizes are 
        always in strict proportion to their `weight` values
    pad : int, optional
        The number of screen units that will be added to the largest window 
        contained completely in that row when the grid geometry manager 
        requests a size from the containing window.
    """
    local_master = _master_ctx.get()
    if local_master is None:
        raise ValueError("TKML configure_next_row is missing a contextual master. Only use this function in a container context that uses contextual grid.")
    local_master.grid_rowconfigure(_grid_next_row_ctx.get(), **kwargs)

