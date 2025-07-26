"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
09.10.24, 18:38

Functions to add hover tooltips to tkinter elements.
Inspired by the tkinter_tooltip package, matplotlib's tooltip 
implementation and based on Akascape's CTkToolTip library 
(licensed under Creative Commons Zero v1.0 Universal, available
at: https://github.com/Akascape/CTkToolTip)
"""

import sys
import time
from ._deps import *
from typing import Literal
from el.observable import Observable, MaybeObservable, maybe_observe

ColorType = str | list[str] | tuple[str, str]


class CTkToolTip(ctk.CTkToplevel):
    """
    Creates a ToolTip (pop-up) widget for customtkinter.
    """

    def __init__(
        self,
        widget: tk.BaseWidget,
        text: MaybeObservable[str],
        delay: float = 0.2,
        follow: bool = True,
        x_offset: int = +20,
        y_offset: int = +10,
        bg_color: ColorType = None,
        corner_radius: int = 10,
        border_width: int = 0,
        border_color: ColorType = None,
        alpha: float = 0.95,
        padding: tuple = (10, 2),
        disabled: MaybeObservable[bool] = False,
        **message_kwargs
    ):
        self._widget = widget
        super().__init__(master=self._widget.winfo_toplevel())

        self.withdraw()
        # Disable ToolTip's title bar
        self.overrideredirect(True)

        # on windows you define a specific color to be transparent (use the toplevel fg by default)
        if sys.platform.startswith("win"):
            self._transparent_color = self._widget._apply_appearance_mode(ctk.ThemeManager.theme["CTkToplevel"]["fg_color"])
            self.attributes("-transparentcolor", self._transparent_color)
            self.transient()
        # on Mac there is the special "systemTransparent" color
        elif sys.platform.startswith("darwin"):
            self._transparent_color = 'systemTransparent'
            self.attributes("-transparent", True)
            self.transient(self.master)
        # Transparency not supported on Linux
        else:
            self._transparent_color = '#000001'
            corner_radius = 0   # disable border radius so it doesn't look weird
            self.transient()

        self.resizable(width=True, height=True)
        # Make the window background transparent (if possible)
        super().configure(background=self._transparent_color)

        # StringVar instance for msg string
        self.message_var = ctk.StringVar()
        maybe_observe(text, self.message_var.set)

        self._delay = delay
        self._follow = follow
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._corner_radius = corner_radius
        self._alpha = alpha
        self._border_width = border_width
        self._padding = padding
        self._bg_color: ColorType = ctk.ThemeManager.theme["CTkFrame"]["fg_color"] if bg_color is None else bg_color
        self._border_color = border_color
        self._disable = disabled.value if isinstance(disabled, Observable) else disabled

        # visibility status of the ToolTip inside|outside|visible
        self._status: Literal["inside", "outside"] = "outside"
        self._last_moved: int = 0
        self.attributes('-alpha', self._alpha)

        # If we are on windows and we want to set our actual color to the one we just configured as transparent
        # we need to change the transparent color to a different one (namely #000001 in this case)
        if sys.platform.startswith("win"):
            if self._widget._apply_appearance_mode(self._bg_color) == self._transparent_color:
                self._transparent_color = "#000001"
                self.config(background=self._transparent_color)
                self.attributes("-transparentcolor", self._transparent_color)

        # add a main background frame that is always transparent (therefore using tk Frame)
        self._transparent_frame = tk.Frame(self, bg=self._transparent_color)
        self._transparent_frame.pack(padx=0, pady=0, fill="both", expand=True)

        # add the CTkFrame which actually forms the shape and color of the toplevel
        self._frame = ctk.CTkFrame(self._transparent_frame, bg_color=self._transparent_color,
                                            corner_radius=self._corner_radius,
                                            border_width=self._border_width, fg_color=self._bg_color,
                                            border_color=self._border_color)
        self._frame.pack(padx=0, pady=0, fill="both", expand=True)

        # add the label containing the text
        self.message_label = ctk.CTkLabel(self._frame, textvariable=self.message_var, **message_kwargs)
        self.message_label.pack(fill="both", padx=self._padding[0] + self._border_width,
                                pady=self._padding[1] + self._border_width, expand=True)

        # If we are on top of another widget with the same color, we want to use the 
        # secondary frame color in order to be distinguishable from the widget.
        if self._widget.winfo_name() != "tk":
            if self._frame.cget("fg_color") == self._widget.cget("bg_color"):
                if not bg_color:    # don't do this if the user manually assigned the color
                    self._top_fg_color = ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
                    # if any of the colors in the theme are the transparent color, we don't do this
                    update_blocked = False
                    if isinstance(self._top_fg_color, (tuple, list)):
                        for c in self._top_fg_color:
                            if c == self._transparent_color: update_blocked = True
                    else:
                        if self._top_fg_color == self._transparent_color:
                            update_blocked = True
                    if not update_blocked:
                        self._frame.configure(fg_color=self._top_fg_color)

        # Add bindings to the widget without overriding the existing ones to 
        # detect when to show the tooltip
        self._widget.bind("<Enter>", self._on_enter, add="+")
        self._widget.bind("<Leave>", self._on_leave, add="+")
        self._widget.bind("<Motion>", self._on_enter, add="+")
        self._widget.bind("<B1-Motion>", self._on_enter, add="+")
        self._widget.bind("<Destroy>", lambda _: self.hide(), add="+")

        # add listener for disabled observable if applicable
        def set_disabled(v: bool):
            if v:
                self.hide()
            else:
                self.show()
        maybe_observe(disabled, set_disabled)

    def show(self) -> None:
        """
        Enable the widget.
        """
        self._disable = False

    def _on_enter(self, event: tk.Event) -> None:
        """
        Processes motion within the widget including entering and moving.
        """

        if self._disable:
            return
        self._last_moved = time.time()

        # Set the status as inside for the very first time
        if self._status == "outside":
            self._status = "inside"

        # If the follow flag is not set, motion within the widget will make the ToolTip disappear
        if not self._follow:
            self._status = "inside"
            self.withdraw()

        # Calculate available space on the right side of the widget relative to the screen
        root_width = self.winfo_screenwidth()
        widget_x = event.x_root
        space_on_right = root_width - widget_x

        # Calculate the width of the tooltip's text based on the length of the message string
        text_width = self.message_label.winfo_reqwidth()

        # Calculate the offset based on available space and text width to avoid going off-screen on the right side
        offset_x = self._x_offset
        if space_on_right < text_width + 20:  # Adjust the threshold as needed
            offset_x = -text_width - 20  # Negative offset when space is limited on the right side

        # Offsets the ToolTip using the coordinates od an event as an origin
        self.geometry(f"+{event.x_root + offset_x}+{event.y_root + self._y_offset}")

        # show the tooltip after the configured delay time
        # Time is in integer: milliseconds
        self.after(int(self._delay * 1000), self._show)

    def _on_leave(self, event: tk.Event | None = None) -> None:
        """
        Hides the ToolTip temporarily.
        """

        if self._disable: return
        self._status = "outside"
        self.withdraw()

    def _show(self) -> None:
        """
        Displays the ToolTip.
        """

        if not self._widget.winfo_exists():
            self.hide()
            self.destroy()

        if self._status == "inside" and time.time() - self._last_moved >= self._delay:
            self._status = "visible"
            self.deiconify()

    def hide(self) -> None:
        """
        Disable the widget from appearing.
        """
        if not self.winfo_exists():
            return
        self.withdraw()
        self._disable = True

    def is_disabled(self) -> None:
        """
        Return the window state
        """
        return self._disable

    def get(self) -> None:
        """
        Returns the text on the tooltip.
        """
        return self.message_var.get()

    def configure(self, message: str | None = None, delay: float | None = None, bg_color: ColorType | None = None):
        """
        Set new message or configure the label parameters.
        """
        if delay is not None:
            self._delay = delay
        if bg_color is not None:
            self._frame.configure(fg_color=bg_color)
            self._bg_color = bg_color
        if message is not None:
            self.message_var.set(message)