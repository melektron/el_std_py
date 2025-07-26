"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
08.10.24, 09:17

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Utility classes and functions useful for developing 
CTk applications.
"""

from ._colors import (
    homogenize_color_types,
    apply_apm,
    apply_apm_observed,
    tk_to_rgb16,
    tk_to_rgb8,
    rgb_to_hex_str,
)
from ._dynamic_config import apply_to_config, apply_to_tk_var
from ._scaling import apply_widget_scaling, reverse_widget_scaling, apply_window_scaling, reverse_window_scaling
from .types import *