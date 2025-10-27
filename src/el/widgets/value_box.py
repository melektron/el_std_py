"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
18.09.24, 18:04
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

CTkEntryEx that is well integrated with observables and has some convenience features.
This is especially 
"""

import typing

from ._deps import *

from el.observable import Observable
from el.widgets.ctkex import CTkEntryEx, CTkEntryExPassthroughArgs
from el.tkml.adapters import stringvar_adapter


class ValueBox(CTkEntryEx, Observable[str]):
    def __init__(
        self, 
        master: tk.Misc,
        initial_value: str = "",
        display_only: bool = True,
        disabled_by_default: bool = True, 
        **kwargs: typing.Unpack[CTkEntryExPassthroughArgs],
    ) -> None:
        Observable.__init__(self, initial_value=initial_value)
        CTkEntryEx.__init__(
            self, 
            master,
            text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"], 
            border_width=0 if display_only else None,
            state="disabled" if disabled_by_default else "normal",
            textvariable=stringvar_adapter(self, master),
            **kwargs
        )

        self._disabled = disabled_by_default

    @property
    def disabled(self) -> bool:
        return self._disabled
    
    @disabled.setter
    def disabled(self, disabled: bool) -> None:
        self._disabled = disabled
        self.configure(state="disabled" if disabled else "normal")
    
    def set_disabled(self, disabled: bool) -> None:
        """ functional API for easy assignment from an observable """
        self.disabled = disabled