"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
18.09.24, 18:04
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

CTkEntry that is well integrated with observables and has some convenience features
"""

from ._deps import *
from el.observable import Observable


class ValueBox(ctk.CTkEntry, Observable[str]):
    def __init__(
        self, 
        parent: ctk.CTkBaseClass,
        initial_value: str = "", 
        width: int = 150, 
        disabled_by_default: bool = True, 
        **kwargs
    ) -> None:
        
        self._entry_var = ctk.StringVar(parent)
        ctk.CTkEntry.__init__(
            self, 
            parent, 
            text_color=ctk.ThemeManager.theme["CTkEntry"]["text_color"], 
            width=width, 
            border_width=0, 
            state="disabled" if disabled_by_default else "normal",
            textvariable=self._entry_var,
            **kwargs
        )

        Observable.__init__(self, initial_value=initial_value)
        
        # bind the observable function to the entry's textvariable
        self >> self._entry_var.set
        self._entry_var.trace_add("write", lambda *_: self.receive(self._entry_var.get()))
        self.configure(textvariable=self._entry_var)

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