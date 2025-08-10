"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.08.25, 02:39
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Enhanced scrollable frame with improved scrollbar, options and automatic transparent 
color detection by using other ctkex widgets under the hood.
"""


import sys
import typing

from el.ctk_utils.types import *

from .._deps import *
from ._frame_ex import CTkFrameEx


class _CTkScrollableFramePassthroughArgs(typing.TypedDict, total=False):
    width: int
    height: int
    corner_radius: typing.Optional[int]
    border_width: typing.Optional[int]

    bg_color: Color
    fg_color: typing.Optional[Color]
    border_color: typing.Optional[Color]
    scrollbar_fg_color: typing.Optional[Color]
    scrollbar_button_color: typing.Optional[Color]
    scrollbar_button_hover_color: typing.Optional[Color]
    label_fg_color: typing.Optional[Color]
    label_text_color: typing.Optional[Color]

    label_text: str
    label_font: typing.Optional[FontArgType]
    label_anchor: AnchorType
    orientation: typing.Literal["vertical", "horizontal"]

class CTkScrollableFrameExPassthroughArgs(_CTkScrollableFramePassthroughArgs, total=False):
    round_width_to_even_numbers: bool
    round_height_to_even_numbers: bool
    # with the following options be careful as it is possible to make the corners of the
    # scrollable area peak out the frame if you make the border spacing too small. The default
    # uses the border radius, meaning it is always safe but a bit large.
    border_spacing_horizontal: int | None  # optional argument to reduce border spacing on the side (left/right)
    border_spacing_vertical: int | None  # option argument to reduce border spacing on the top/bottom


class CTkScrollableFrameEx(ctk.CTkScrollableFrame):

    def __init__(
        self,
        master: tk.Misc,
        width: int = 200,
        height: int = 200,
        corner_radius: typing.Optional[int] = None,
        border_width: typing.Optional[int] = None,

        bg_color: Color = "transparent",
        fg_color: typing.Optional[Color] = None,
        border_color: typing.Optional[Color] = None,
        scrollbar_fg_color: typing.Optional[Color] = None,
        scrollbar_button_color: typing.Optional[Color] = None,
        scrollbar_button_hover_color: typing.Optional[Color] = None,
        label_fg_color: typing.Optional[Color] = None,
        label_text_color: typing.Optional[Color] = None,

        label_text: str = "",
        label_font: typing.Optional[FontArgType] = None,
        label_anchor: AnchorType = "center",
        orientation: typing.Literal["vertical", "horizontal"] = "vertical",

        round_width_to_even_numbers: bool = True,
        round_height_to_even_numbers: bool = True,
        border_spacing_horizontal: int | None = None,
        border_spacing_vertical: int | None = None,
    ):
        # This __init__ is a complete replacement for super().__init__(). This way we can
        # change the types of some of the widget components.

        self._orientation = orientation
        self._border_spacing_horizontal = border_spacing_horizontal
        self._border_spacing_vertical = border_spacing_vertical

        # dimensions independent of scaling
        self._desired_width = width  # _desired_width and _desired_height, represent desired size set by width and height
        self._desired_height = height

        # modification in ctkex: change from CTkFrame to CTkFrameEx and pass the rounding args
        self._parent_frame = CTkFrameEx(
            master=master, width=0, height=0, corner_radius=corner_radius,
            border_width=border_width, bg_color=bg_color, fg_color=fg_color, border_color=border_color,
            round_width_to_even_numbers=round_width_to_even_numbers,
            round_height_to_even_numbers=round_height_to_even_numbers,
        )
        self._parent_canvas = tk.Canvas(master=self._parent_frame, highlightthickness=0)
        self._set_scroll_increments()

        if self._orientation == "horizontal":
            self._scrollbar = ctk.CTkScrollbar(master=self._parent_frame, orientation="horizontal", command=self._parent_canvas.xview,
                                           fg_color=scrollbar_fg_color, button_color=scrollbar_button_color, button_hover_color=scrollbar_button_hover_color)
            self._parent_canvas.configure(xscrollcommand=self._scrollbar.set)
        elif self._orientation == "vertical":
            self._scrollbar = ctk.CTkScrollbar(master=self._parent_frame, orientation="vertical", command=self._parent_canvas.yview,
                                           fg_color=scrollbar_fg_color, button_color=scrollbar_button_color, button_hover_color=scrollbar_button_hover_color)
            self._parent_canvas.configure(yscrollcommand=self._scrollbar.set)

        self._label_text = label_text
        self._label = ctk.CTkLabel(self._parent_frame, text=label_text, anchor=label_anchor, font=label_font,
                               corner_radius=self._parent_frame.cget("corner_radius"), text_color=label_text_color,
                               fg_color=ctk.ThemeManager.theme["CTkScrollableFrame"]["label_fg_color"] if label_fg_color is None else label_fg_color)

        tk.Frame.__init__(self, master=self._parent_canvas, highlightthickness=0)
        CTkAppearanceModeBaseClass.__init__(self)
        CTkScalingBaseClass.__init__(self, scaling_type="widget")

        self._create_grid()

        self._parent_canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                                      height=self._apply_widget_scaling(self._desired_height))

        self.bind("<Configure>", lambda e: self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all")))
        self._parent_canvas.bind("<Configure>", self._fit_frame_dimensions_to_canvas)
        self.bind_all("<MouseWheel>", self._mouse_wheel_all, add="+")
        self.bind_all("<KeyPress-Shift_L>", self._keyboard_shift_press_all, add="+")
        self.bind_all("<KeyPress-Shift_R>", self._keyboard_shift_press_all, add="+")
        self.bind_all("<KeyRelease-Shift_L>", self._keyboard_shift_release_all, add="+")
        self.bind_all("<KeyRelease-Shift_R>", self._keyboard_shift_release_all, add="+")
        # modification in ctkex: fix mouse wheel on Linux
        # https://github.com/TomSchimansky/CustomTkinter/issues/1356#issuecomment-1474104298
        if sys.platform.startswith("linux"):
            # self.bind("<Button-4>", lambda e: self._parent_canvas.yview("scroll", -1, "units"))
            # self.bind("<Button-5>", lambda e: self._parent_canvas.yview("scroll", 1, "units"))
            def scroll(e: tk.Event, up: bool) -> None:
                # patch the delta into the events
                # the _mouser_wheel_all internally inverts this again
                e.delta = 1 if up else -1
                # sometimes the event widget is a string and does not have a master which is a problem
                # (we catch this here because ctk's internal functions don't)
                if not hasattr(e.widget, "master"): return
                # use this function as it provides the complete scrolling feature set
                self._mouse_wheel_all(e)    
            self.bind_all("<Button-4>", lambda e: scroll(e, True), add=True)
            self.bind_all("<Button-5>", lambda e: scroll(e, False), add=True)

        self._create_window_id = self._parent_canvas.create_window(0, 0, window=self, anchor="nw")

        if self._parent_frame.cget("fg_color") == "transparent":
            tk.Frame.configure(self, bg=self._apply_appearance_mode(self._parent_frame.cget("bg_color")))
            self._parent_canvas.configure(bg=self._apply_appearance_mode(self._parent_frame.cget("bg_color")))
        else:
            tk.Frame.configure(self, bg=self._apply_appearance_mode(self._parent_frame.cget("fg_color")))
            self._parent_canvas.configure(bg=self._apply_appearance_mode(self._parent_frame.cget("fg_color")))

        self._shift_pressed = False

    @typing.override
    def _create_grid(self):
        """
        A modified version of super()._create_grid() that 
        allows reducing the border spacing at the risk of corners
        peaking out if reduced too much.
        """
        # here we removed the erroneous widget scaling. It is needed for the dimensions
        # of self._parten_canvas (which is a tk.Canvas) but not for scrollbar or label
        # which are already tk widgets and re-apply that scaling internally.
        border_spacing_auto = self._parent_frame.cget("corner_radius") + self._parent_frame.cget("border_width")
        # we use the auto spacing if no explicit spacing was provided
        border_spacing_horizontal = border_spacing_auto if self._border_spacing_horizontal is None else self._border_spacing_horizontal
        border_spacing_vertical = border_spacing_auto if self._border_spacing_vertical is None else self._border_spacing_vertical

        if self._orientation == "horizontal":
            self._parent_frame.grid_columnconfigure(0, weight=1)
            self._parent_frame.grid_rowconfigure(1, weight=1)
            self._parent_canvas.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=self._apply_widget_scaling(border_spacing_horizontal),
                pady=(self._apply_widget_scaling(border_spacing_vertical), 0),
            )
            # scrollbar always uses automatic border spacing bc. it is right at the border so any reduction
            # would cause peeking of the corners
            self._scrollbar.grid(row=2, column=0, sticky="nsew", padx=border_spacing_auto)

            if self._label_text is not None and self._label_text != "":
                self._label.grid(row=0, column=0, sticky="ew", padx=border_spacing_horizontal, pady=border_spacing_vertical)
            else:
                self._label.grid_forget()

        elif self._orientation == "vertical":
            self._parent_frame.grid_columnconfigure(0, weight=1)
            self._parent_frame.grid_rowconfigure(1, weight=1)
            self._parent_canvas.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=(self._apply_widget_scaling(border_spacing_horizontal), 0),
                pady=self._apply_widget_scaling(border_spacing_vertical),
            )
            # scrollbar always uses automatic border spacing bc. it is right at the border so any reduction
            # would cause peeking of the corners
            self._scrollbar.grid(row=1, column=1, sticky="nsew", pady=border_spacing_auto)

            if self._label_text is not None and self._label_text != "":
                self._label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=border_spacing_horizontal, pady=border_spacing_vertical)
            else:
                self._label.grid_forget()
