"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
18.01.25, 19:26
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for mpl_utils module
"""

from el.errors import SetupError

try:
    import matplotlib.artist as mpl_artist
    import matplotlib.backend_bases as mpl_bases
    import matplotlib.text as mpl_text

except ImportError:
    raise SetupError("el.mpl_utils requires matplotlib. Please install it before using el.mpl_utils.")