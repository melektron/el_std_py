"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
20.07.25, 23:02
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

context variables used by tkml nodes
"""

from contextvars import ContextVar

from ._deps import *


# context var to track the current master widget for all subsequent calls
_master_ctx = ContextVar[tk.Widget | None]("_master_ctx", default=None)

# context var to track the next grid column and row
_grid_next_column_ctx = ContextVar[int]("_grid_next_column_ctx", default=0)
_grid_next_row_ctx = ContextVar[int]("_grid_next_row_ctx", default=0)
