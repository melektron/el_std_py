"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.10.25, 10:52
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Utilities for working with pathlib.Path
"""

import os
import pathlib


def abspath(input: pathlib.Path) -> pathlib.Path:
    """Shortcut for using os.path.abspath with pathlib.Path.

    Parameters
    ----------
    input : pathlib.Path
        some (possibly relative path)

    Returns
    -------
    pathlib.Path
        equivalent absolute path
    """
    return pathlib.Path(os.path.abspath(str(input)))