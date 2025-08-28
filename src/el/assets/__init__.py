"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
28.08.25, 14:04
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

UI Asset management for CTk.
"""

import os
from pathlib import Path

from ._manager import AssetManager

# asset manager for the el_std_py builtin assets
builtin = AssetManager(
    base_path=Path(os.path.dirname(os.path.abspath(__file__))) / "builtin"
)