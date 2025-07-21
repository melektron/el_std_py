"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
21.07.25, 01:34
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

wrapper around the pack geometry manager to make it easier to use
in the context of tkml adapters
"""

import logging
from typing import Literal

from ._deps import *
from ._context import _grid_next_column_ctx, _grid_next_row_ctx

_log = logging.getLogger(__name__)

type ScreenUnits = str | float
type Anchor = Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"]  # from typeshed fallback


"""
    
Pack a widget in the parent widget. Use as options:
    after=widget - pack it after you have packed widget
    anchor=NSEW (or subset) - position widget according to
                                given direction
    before=widget - pack it before you will pack widget
    expand=bool - expand widget if parent size grows
    fill=NONE or X or Y or BOTH - fill widget if widget grows
    in=master - use master to contain this widget
    in_=master - see 'in' option description
    ipadx=amount - add internal padding in x direction
    ipady=amount - add internal padding in y direction
    padx=amount - add padding in x direction
    pady=amount - add padding in y direction
    side=TOP or BOTTOM or LEFT or RIGHT -  where to add this widget.
"""

def pack[WT: tk.Widget](
    widget: WT,
    after: tk.Misc | None = None,
    anchor: Anchor | None = None,
    before: tk.Misc | None = None,
    expand: bool | Literal[0, 1] | None = None,
    fill: Literal['none', 'x', 'y', 'both'] | None = None,
    side: Literal['left', 'right', 'top', 'bottom'] | None = None,
    ipadx: ScreenUnits | None = None,
    ipady: ScreenUnits | None = None,
    padx: ScreenUnits | tuple[ScreenUnits, ScreenUnits] | None = None,
    pady: ScreenUnits | tuple[ScreenUnits, ScreenUnits] | None = None
) -> WT:
    """
    Simple geometry manager to position the widget in a container.
    This wrapper does nothing other than calling .pack and then
    returning the widget.

    Parameters
    ----------
    widget : WT
        the widget to place
    after : tk.Misc | None, optional
        after what widget to place the widget
    anchor : Anchor | None, optional
        where the widget should be aligned to
    before : tk.Misc | None, optional
        before what widget to place the widget
    expand : bool | Literal[0, 1] | None, optional
        whether widget should expand when container expands
    fill : Literal[&#39;none&#39;, &#39;x&#39;, &#39;y&#39;, &#39;both&#39;] | None, optional
        fill widget if widget grows
    side : Literal[&#39;left&#39;, &#39;right&#39;, &#39;top&#39;, &#39;bottom&#39;] | None, optional
        what side of the container to add the widget to
    ipadx : ScreenUnits, optional
        internal padding in x direction
    ipady : ScreenUnits, optional
        internal padding in y direction
    padx : ScreenUnits | tuple[ScreenUnits, ScreenUnits], optional
        external padding in x direction
    pady : ScreenUnits | tuple[ScreenUnits, ScreenUnits], optional
        external padding in y direction

    Returns
    -------
    widget -> allows to use this function inline with widget creation
    """

    kwargs = {}
    if after is not None:
        kwargs["after"] = after
    if anchor is not None:
        kwargs["anchor"] = anchor
    if before is not None:
        kwargs["before"] = before
    if expand is not None:
        kwargs["expand"] = expand
    if fill is not None:
        kwargs["fill"] = fill
    if side is not None:
        kwargs["side"] = side
    if ipadx is not None:
        kwargs["ipadx"] = ipadx
    if ipady is not None:
        kwargs["ipady"] = ipady
    if padx is not None:
        kwargs["padx"] = padx
    if pady is not None:
        kwargs["pady"] = pady
    widget.pack(**kwargs)
    return widget
    