"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
09.10.24, 18:38

Functions to add hover tooltips to tkinter elements.
Inspired by the tkinter_tooltip package and matplotlib's tooltip 
implementation
"""

from ._deps import *
from el.observable import Observable


def add_tooltip(widget: tk.Widget, text: str | Observable[str]) -> None:
    """
    Registers a toplevel with a (possibly dynamic) tooltip text to be
    shown when hovering over the specified tkinter widget.
    """
    tip_window: tk.Toplevel = None
    tip_label: tk.Label = None

    # Observe text if it is an observable
    if isinstance(text, Observable):

        def text_changed(v: str) -> None:
            if tip_label is not None:
                tip_label.configure(text=v)

        text >> text_changed

    def showtip(event: tk.Event):
        """Display text in tooltip window."""
        nonlocal tip_window, tip_label

        if tip_window or not text:
            return

        x, y, _, _ = widget.bbox("insert")
        x = x + widget.winfo_rootx() + widget.winfo_width()
        y = y + widget.winfo_rooty()
        tip_window = ctk.CTkToplevel(widget)
        tip_window.overrideredirect(1)
        tip_window.geometry(f"+{x}+{y}")

        try:  # For Mac OS
            tip_window.tk.call(
                "::tk::unsupported::MacWindowStyle",
                "style",
                tip_window._w,
                "help",
                "noActivates",
            )
        except tk.TclError:
            pass

        tip_label = ctk.CTkLabel(
            tip_window, text=text, justify=tk.LEFT
        )
        tip_label.pack(padx=4)

    def hidetip(event: tk.Event):
        nonlocal tip_window

        if tip_window:
            tip_window.destroy()
        tip_window = None

    widget.bind("<Enter>", showtip)
    widget.bind("<Leave>", hidetip)
