"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
19.10.24, 22:11
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

scaling calculation utilities
"""

from ._deps import *


def apply_widget_scaling(widget: tk.Tk | tk.Widget | tk.Toplevel, value: int | float) -> float:
    """
    Applies the widget scaling to value. The scaling factor is dependent on the DPI
    scaling of the window, which is determined by passing a widget of the target window
    or the window itself to this function. This is implemented by ctk.ScalingTracker, for
    which this is just a wrapper.
    """
    return value * ctk.ScalingTracker.get_widget_scaling(widget)


def reverse_widget_scaling(widget: tk.Tk | tk.Widget | tk.Toplevel, value: int | float) -> float:
    """
    Reverses the widget scaling to value (to go back from scaled coordinates to real pixel 
    coords). The scaling factor is dependent on the DPI
    scaling of the window, which is determined by passing a widget of the target window
    or the window itself to this function. This is implemented by ctk.ScalingTracker, for
    which this is just a wrapper.
    """
    return value / ctk.ScalingTracker.get_widget_scaling(widget)


def apply_window_scaling(widget: tk.Tk | tk.Widget | tk.Toplevel, value: int | float) -> float:
    """
    Applies the window scaling to value. The scaling factor is dependent on the DPI
    scaling of the window, which is determined by passing a widget of the target window
    or the window itself to this function. This is implemented by ctk.ScalingTracker, for
    which this is just a wrapper.
    """
    return value * ctk.ScalingTracker.get_window_scaling(widget)


def reverse_window_scaling(widget: tk.Tk | tk.Widget | tk.Toplevel, value: int | float) -> float:
    """
    Reverses the widget scaling to value (to go back from scaled coordinates to real pixel 
    coords). The scaling factor is dependent on the DPI
    scaling of the window, which is determined by passing a widget of the target window
    or the window itself to this function. This is implemented by ctk.ScalingTracker, for
    which this is just a wrapper.
    """
    return value / ctk.ScalingTracker.get_window_scaling(widget)