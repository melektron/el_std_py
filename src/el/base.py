"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
11.09.25, 01:07
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

el-std-py base features that cannot be assigned any other category.
"""


def filter_kwargs(**kwargs):
    """Filters kwargs for non-None values.

    This is meant to be used in conjunction with kwargs expansion:
    ```python
    button.configure(**filter_kwargs(
        icon=self._icon,
        text=updated_text,
        fg_color=color_override
    ))
    ```
    This only passes those argument on to the configure() call that are
    not none.

    Returns
    -------
    dict[str, Any]
        dictionary containing all kwargs that are not None.
    """
    return {
        key: value
        for key, value in kwargs.items()
        if value is not None
    }


def filter_string(text: str, chars_to_remove: str) -> str:
    """Returns text without characters in `chars_to_remove`.

    Parameters
    ----------
    text : str
        text to filter
    chars_to_remove : str
        characters to remove. This is not treated as string but instead
        as a list of individual characters (like with `.strip()`)

    Returns
    -------
    str
        filtered string\acrshort{}
    """
    return text.translate(str.maketrans('', '', chars_to_remove))