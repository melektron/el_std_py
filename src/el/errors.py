"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 11:40
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

More exception types that are either used by el or are 
generally useful
"""

class SetupError(Exception):
    pass

class IncompleteReadError(Exception):
    pass

class InvalidPathError(Exception):
    pass
