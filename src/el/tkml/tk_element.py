"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
20.07.25, 16:15


"""

import functools
from typing import Callable, Concatenate, Generator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from ._deps import *

# context var to track the current master widget for all subsequent calls
master_ctx = ContextVar[tk.Widget | None]("root_ctx", default=None)

#class TkE[T, R, **P]:
#
#    def __init__(self, widget_type: Callable[Concatenate[T, P], R], master: tk.Widget | None = None):
#        super().__init__()
#        self._widget_type = widget_type
#        self._master = master
#
#    def __enter__(self, *args: P.args, **kwargs: P.kwargs) -> Generator[R, None, None]:
#        print("enter context")
#        if (self._master)
#        widget = self._widget_type(master=master, *args, **kwargs)
#        pass
#
#    def __exit__(self, exc_type, exc_val, exc_tb):
#        pass


def tkc[T, R, **P](widget_type: Callable[Concatenate[T, P], R], master: tk.Widget | None = None):
    """
    creates a tkml container widget for use in a context manager
    to place child widgets inside.

    Parameters
    ----------
    widget_type : type[tk.Widget]
        widget type to create. should be a container widget like
        a frame or toplevel.
    master : tk.Widget | None
        optional master override. When passed, the master
        of the container will be the provided widget instead
        of the contextual parent container.
    
    Returns
    -------
    type[widget_type]
        Widget container context manager to create the container element.
        This is a callable that immitates the constructor of the passed
        widget type.

    Raises
    ------
    ValueError
        No contextual master could be determined and no explicit master was provided.
    """
    #@functools.wraps(func)
    @contextmanager
    def inner(*args: P.args, **kwargs: P.kwargs) -> Generator[R, None, None]:
        print("enter context")
        # determine what the master of this element should be
        # (either grab from context or use specified master)
        local_master = master if master is not None else master_ctx.get()
        if local_master is None:
            raise ValueError("Top-level tk element in context is missing master. Provide master manually or use tkr for master-less root elements.")
        # create element
        widget = widget_type(master=local_master, *args, **kwargs)
        # set it as master for the child elements
        master_token = master_ctx.set(widget)
        try:
            # run the children
            yield widget
        finally:
            print("exit context")
            # restore previous master
            master_ctx.reset(master_token)
        
    return inner