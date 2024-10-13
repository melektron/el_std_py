"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
08.10.24, 09:17

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
from ._tooltip import add_tooltip
from ._dynamic_config import apply_to_config