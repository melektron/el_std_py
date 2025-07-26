"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
09.10.24, 17:58

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Modified CTkButton for tool actions in a toolbar. This button has loosened
border restrictions, allowing for button icons to be more tightly spaced in
square button. It additionally has a builtin tooltip support.
"""

import typing

from ._deps import *
try:
    from PIL import ImageTk
except ImportError:
    raise SetupError("el.widgets.toolbar_button requires pillow (PIL). Please install it before using el.widgets.toolbar_button.")
    #raise SetupError("el.widgets requires customtkinter and pillow (PIL). Please install them before using el.widgets.")
    
from el.observable import Observable, MaybeObservable
from el.widgets import CTkToolTip, ctkex


class ToolbarButton(ctkex.CTkButtonEx):

    def __init__(
        self,
        master: tk.Misc,
        width: int = 32,            # changed default to 32
        height: int = 32,           # changed default to 32
        border_spacing: int = 3,    # changed default to 3
        text: str = "",             # changed default to empty
        tooltip: MaybeObservable[str] | None = None,
        **kwargs: typing.Unpack[ctkex.CTkButtonExPassthroughArgs]
    ):
        """
        Modified CTkButtonEx for tool actions in a toolbar. This button has loosened
        border restrictions, allowing for button icons to be more tightly spaced in
        square button. It additionally has a builtin tooltip support and some
        modified defaults for this application.

        Parameters
        ----------
        master : tk.Misc
            _description_
        width, height : int, optional
            with and height, by default 32
        border_spacing : int, optional
            border spacing which as by default been increased to 3, 
            which is required to prevent square image from peeking out the corners by default
            due to the reduced sideways restrictions.
        text : str, optional
            text to show, by default empty as it is expected that an image is used
        tooltip : MaybeObservable[str], optional
            text to show in a tooltip or none to disable tooltip (is also disabled in touchscreen mode)
            Can be an observable.
        """

        super().__init__(
            master,
            width=width,
            height=height,
            border_spacing=border_spacing,
            text=text,
            **kwargs
        )
        
        if tooltip is not None:
            self._tooltip = CTkToolTip(
                self, 
                text=tooltip,
                disabled=("touchscreen_mode" in kwargs and kwargs["touchscreen_mode"])  # disabled in touchscreen mode
            )
        else:
            self._tooltip = None
    
    @typing.override
    def _create_grid(self):
        """
        Modified version of regular _create_grid. This version removes
        the requirement of the side borders being at least the size of the border radius.
        This gives the ability to have square, icon-only buttons with the icons centered nicely
        with less than the corner radius of spacing. The danger is: when spaced too close, the
        corners of the icon (even if transparent) may peek outside the button, which has to be manually
        avoided by settings sufficient border spacing now. By doing this manually, we can get closer
        to the danger-zone ;)
        """

        # Outer rows and columns have weight of 1000 to overpower the rows and columns of the label and image with weight 1.
        # Rows and columns of image and label need weight of 1 to collapse in case of missing space on the button,
        # so image and label need sticky option to stick together in the center, and therefore outer rows and columns
        # need weight of 100 in case of other anchor than center.
        n_padding_weight, s_padding_weight, e_padding_weight, w_padding_weight = (
            1000,
            1000,
            1000,
            1000,
        )
        if self._anchor != "center":
            if "n" in self._anchor:
                n_padding_weight, s_padding_weight = 0, 1000
            if "s" in self._anchor:
                n_padding_weight, s_padding_weight = 1000, 0
            if "e" in self._anchor:
                e_padding_weight, w_padding_weight = 1000, 0
            if "w" in self._anchor:
                e_padding_weight, w_padding_weight = 0, 1000

        scaled_minsize_rows = self._apply_widget_scaling(
            max(self._border_width + 1, self._border_spacing)
        )
        # scaled_minsize_columns = self._apply_widget_scaling(max(self._corner_radius, self._border_width + 1, self._border_spacing))
        scaled_minsize_columns = self._apply_widget_scaling(
            max(self._border_width + 1, self._border_spacing)
        )

        self.grid_rowconfigure(0, weight=n_padding_weight, minsize=scaled_minsize_rows)
        self.grid_rowconfigure(4, weight=s_padding_weight, minsize=scaled_minsize_rows)
        self.grid_columnconfigure(
            0, weight=e_padding_weight, minsize=scaled_minsize_columns
        )
        self.grid_columnconfigure(
            4, weight=w_padding_weight, minsize=scaled_minsize_columns
        )

        if self._compound in ("right", "left"):
            self.grid_rowconfigure(2, weight=1)
            if self._image_label is not None and self._text_label is not None:
                self.grid_columnconfigure(
                    2,
                    weight=0,
                    minsize=self._apply_widget_scaling(self._image_label_spacing),
                )
            else:
                self.grid_columnconfigure(2, weight=0)

            self.grid_rowconfigure((1, 3), weight=0)
            self.grid_columnconfigure((1, 3), weight=1)
        else:
            self.grid_columnconfigure(2, weight=1)
            if self._image_label is not None and self._text_label is not None:
                self.grid_rowconfigure(
                    2,
                    weight=0,
                    minsize=self._apply_widget_scaling(self._image_label_spacing),
                )
            else:
                self.grid_rowconfigure(2, weight=0)

            self.grid_columnconfigure((1, 3), weight=0)
            self.grid_rowconfigure((1, 3), weight=1)

        if self._compound == "right":
            if self._image_label is not None:
                self._image_label.grid(row=2, column=3, sticky="w")
            if self._text_label is not None:
                self._text_label.grid(row=2, column=1, sticky="e")
        elif self._compound == "left":
            if self._image_label is not None:
                self._image_label.grid(row=2, column=1, sticky="e")
            if self._text_label is not None:
                self._text_label.grid(row=2, column=3, sticky="w")
        elif self._compound == "top":
            if self._image_label is not None:
                self._image_label.grid(row=1, column=2, sticky="s")
            if self._text_label is not None:
                self._text_label.grid(row=3, column=2, sticky="n")
        elif self._compound == "bottom":
            if self._image_label is not None:
                self._image_label.grid(row=3, column=2, sticky="n")
            if self._text_label is not None:
                self._text_label.grid(row=1, column=2, sticky="s")
