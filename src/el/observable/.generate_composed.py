"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
09.08.25, 16:07
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Helper script to generate the overloads for composed observables
"""


base_text = """
@typing.overload
def compose[{}]({}, all_required: bool = True) -> ComposedObservable[{}]:
    ...
"""

START_MARKER = "## == PROC GENERATED START == ##"
END_MARKER = "## == PROC GENERATED END == ##"

with open("_composed.py", "r") as f:
    content = f.read()
    try:
        content_pre, content = content.split(START_MARKER)
        _, content_post = content.split(END_MARKER)
    except ValueError:
        print("ERROR: No valid generation markers found in file")
        exit(1)

with open("_composed.py", "w") as f:
    f.write(content_pre)
    f.write(START_MARKER)

    for l in range(1, 65):
        t_args = [f"T{i}" for i in range(l)]
        args = [f"s{i}: Observable[T{i}]" for i in range(l)]
        f.write(base_text.format(", ".join(t_args), ", ".join(args), ", ".join(t_args)))

    f.write(END_MARKER)
    f.write(content_post)

print("SUCCESS: Generated overloads")