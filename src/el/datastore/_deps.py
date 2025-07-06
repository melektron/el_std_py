"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 10:24
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Dependency management for datastore module
"""

from el.errors import SetupError

try:
    import pydantic
    import pydantic.main
    import pydantic_core
except ImportError:
    raise SetupError("el.datastore requires pydantic. Please install it before using el.datastore.")

# datastore path type
type DSPath = list[str]