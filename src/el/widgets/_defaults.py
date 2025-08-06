"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
05.08.25, 14:29
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

A system to configure global default values for certain ctk features
that should really be globally configurable, but are only configurable
via constructor arguments.
These settings apply to all el-std widgets, including ctkex widgets.

"""

import typing

from ._deps import *


class DefaultSettings(typing.TypedDict, total=False):
    round_width_to_even_numbers: bool
    round_height_to_even_numbers: bool


class DefaultsManager:
    global_defaults: DefaultSettings = DefaultSettings()
    specific_defaults: dict[type, DefaultSettings] = {}

    @classmethod
    def apply_to_passthrough[T: dict](cls, w_type: type[tk.Misc], kwargs: T) -> T:
        """ 
        takes the Widget Type plus a set of CTk passthrough kwargs 
        and automatically sets any keys that are not already in the kwargs
        but are overridden in the global defaults or the widget-type specific
        defaults to the value specified in the most specific defaults set.
        
        The priority of attribute values is therefore the following:
         1. A value that is manually specified in the constructor if present, otherwise
         2. A widget-specific default if present, otherwise
         3. A global default if present, otherwise
         4. No override, the default value hardcoded in customtkinter
        """
    
    @classmethod
    def apply[T](
        cls, 
        w_type: type[tk.Misc], 
        default: T | None = None
        # ...
    ) -> None:
        ...
    
    
    @classmethod
    def configure(
        cls, 
        types: typing.Iterable[type[tk.Misc]] | None,
        **kwargs: typing.Unpack[DefaultSettings]
    ) -> None:
        """Sets a specific default configuration globally or for specific widgets.

        Parameters
        ----------
        types : typing.Iterable[type[tk.Misc]] | None
            Optional set of widget types for which the defaults should be applied.
            If nothing is provided, the default is applied globally.
        **kwargs : DefaultSettings 
            Any possible default setting value
        """

        if types is None:
            cls.global_defaults.update(**kwargs)
        else:
            for widget_type in types:
                if widget_type not in cls.specific_defaults:
                    cls.specific_defaults[widget_type] = kwargs
                else:
                    cls.specific_defaults[widget_type].update(**kwargs)
