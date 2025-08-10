"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
10.08.25, 13:19
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Functionality to compose a composed observable from multiple sources.
The composed observable updates whenever any of the sources do.
`_composed_base.py` is only the base implementation. 
Due to limitations of pythons typing system, while it is possible
to define varadic type arguments (https://peps.python.org/pep-0646/), 
it is not possibly to transform them by adding or removing wrapper 
types on each argument. 
This is combined 
with procedurally generated overloads into `_composed_generated.py` using the `.generate_composed.py`
helper script
As a workaround, `_composed_base.py` is enhanced overloads for up to 64 arguments
have been generated using the helper script `.generate_composed.py`
"""

# DO NOT REMOVE THE FOLLOWING LINE
## == PROC GENERATED START == ##
## == PROC GENERATED END == ##
# DO NOT REMOVE THE PREVIOUS LINE