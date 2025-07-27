"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
20.07.25, 16:15

Adapters to use regular tk widgets and containers in a markup-like
way by using the TKML context manager syntax and system. This does not
provide any tkinter widget replacements.
"""

import logging
import functools
from typing import Callable, Concatenate, Generator, Any, Never, overload
from contextlib import contextmanager
from contextvars import ContextVar, Token

from el.observable import Observable
from ._deps import *
from ._context import _master_ctx, _grid_next_row_ctx, _grid_next_column_ctx

_log = logging.getLogger(__name__)


def tkr[R, **P](widget_type: Callable[P, R]):
    """
    creates a **TKML root** widget (e.g. tk.Tk) for use in a context manager
    to place child widgets inside. This root widget is expected to not
    require any master, hence why this may be used at a top-level context.

    Parameters
    ----------
    widget_type : type[tk.Widget]
        widget type to create. Most likely tk.Tk or ctk.CTk.
        
    Returns
    -------
    type[widget_type]
        Widget container context manager to create the container element.
        This is a callable that imitates the constructor of the passed
        widget type.
    """
    #@functools.wraps(func)
    @contextmanager
    def inner(*args: P.args, **kwargs: P.kwargs) -> Generator[R, None, None]:
        # create element
        widget = widget_type(*args, **kwargs)
        # set it as master for the child elements
        master_token = _master_ctx.set(widget)
        # new root container means new grid layout, so we rest grid context
        grid_next_column_token = _grid_next_column_ctx.set(0)
        grid_next_row_token = _grid_next_row_ctx.set(0)
        try:
            # run the children
            yield widget
        finally:
            # restore previous master (this should in most cases clear the variable here)
            _master_ctx.reset(master_token)
            # restore other previous context
            _grid_next_column_ctx.reset(grid_next_column_token)
            _grid_next_row_ctx.reset(grid_next_row_token)
        
    return inner


def tkc[T, R, **P](
    widget_type: Callable[Concatenate[T, P], R], 
    master: tk.Widget | None = None,
    placement: Callable[[R], Any] | None = None
):
    """
    creates a **TKML container** widget for use in a context manager
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
    placement : Callable[[R], Any] | None
        optional placement function. When provided, this function is
        executed after creation of the widget but while still in the
        parent context, so the widget can be properly placed with 
        context-dependent placement systems (`el.tkml.grid`, ...).
    
    Returns
    -------
    type[widget_type]
        Widget container context manager to create the container element.
        This is a callable that imitates the constructor of the passed
        widget type.

    Raises
    ------
    ValueError
        No contextual master could be determined and no explicit master was provided.
    """
    #@functools.wraps(func)
    @contextmanager
    def inner(*args: P.args, **kwargs: P.kwargs) -> Generator[R, None, None]:
        # determine what the master of this element should be
        # (either grab from context or use specified master)
        local_master = master if master is not None else _master_ctx.get()
        if local_master is None:
            raise ValueError("TKML container node is missing a contextual master. Provide master manually or use tkr() for master-less root widgets.")
        
        # create element
        widget = widget_type(master=local_master, *args, **kwargs)
        # if a placement is provided, use it now to place the element
        # before modifying the context
        if placement is not None:
            placement(widget)

        # set it as master for the child elements
        master_token = _master_ctx.set(widget)
        # new container means new grid layout, so we rest grid context
        grid_next_column_token = _grid_next_column_ctx.set(0)
        grid_next_row_token = _grid_next_row_ctx.set(0)
        try:
            # run the children
            yield widget
        finally:
            # restore previous context
            _master_ctx.reset(master_token)
            _grid_next_column_ctx.reset(grid_next_column_token)
            _grid_next_row_ctx.reset(grid_next_row_token)
        
    return inner


def tkl[T, R, **P](widget_type: Callable[Concatenate[T, P], R]):
    """
    creates a "TKML leaf" widget using the master from context.
    This may not be used in a context manager. No children can be placed
    below it.

    Parameters
    ----------
    widget_type : type[tk.Widget]
        widget type to create.
    
    Returns
    -------
    type[widget_type]
        Callable that imitates the constructor of the passed
        widget type but with the master passed from context.

    Raises
    ------
    ValueError
        No contextual master could be determined.
    """

    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        # determine what the master of this element should be
        local_master = _master_ctx.get()
        if local_master is None:
            raise ValueError("TKML leaf node is missing a contextual master. Place node in a container or create the widget manually to specify the master.")
        # create element
        return widget_type(master=local_master, *args, **kwargs)
        
    return inner


@contextmanager
def tku[T](master: T, new_grid: bool = True):
    """
    context manager that doesn't create a new container widget
    but instead **uses** an existing widget passed to **`master`** as a 
    TKML container for all it's children. The master is also 
    yielded to the "as" clause of the context manager.

    Parameters
    ----------
    master : tk.Widget
        Widget to use as the master (container) for the children.
    new_grid: bool, optional
        Whether a new grid context should be started for the children.
        By default true, but can be set to false to keep the grid context
        of the parent.
    """
    # set master for the child elements
    master_token = _master_ctx.set(master)
    if new_grid:
        # new container means new grid layout, so we rest grid context
        grid_next_column_token = _grid_next_column_ctx.set(0)
        grid_next_row_token = _grid_next_row_ctx.set(0)
    try:
        # run the children
        yield master
    finally:
        # restore previous context
        _master_ctx.reset(master_token)
        if new_grid:
            _grid_next_column_ctx.reset(grid_next_column_token)
            _grid_next_row_ctx.reset(grid_next_row_token)


@overload
def tkvar_adapter[VT: tk.StringVar](
    obs: Observable[str],
    var_type: type[VT],
    master: tk.Misc | None = None,
    name: str | None = None
) -> VT:
    ...

@overload
def tkvar_adapter[VT: tk.IntVar](
    obs: Observable[int],
    var_type: type[VT],
    master: tk.Misc | None = None,
    name: str | None = None
) -> VT:
    ...

@overload
def tkvar_adapter[VT: tk.DoubleVar](
    obs: Observable[float],
    var_type: type[VT],
    master: tk.Misc | None = None,
    name: str | None = None
) -> VT:
    ...

@overload
def tkvar_adapter[VT: tk.BooleanVar](
    obs: Observable[bool],
    var_type: type[VT],
    master: tk.Misc | None = None,
    name: str | None = None
) -> VT:
    ...

def tkvar_adapter[VT: tk.StringVar | tk.IntVar | tk.DoubleVar | tk.BooleanVar](
    obs: Observable[str] | Observable[int] | Observable[float] | Observable[bool],
    var_type: type[VT],
    master: tk.Misc | None = None,
    name: str | None = None
) -> VT:
    """
    Creates tkinter variable of the provided type that 
    is bidirectionally bound to (synced with) the 
    provided observable.

    Parameters
    ----------
    obs : Observable[str] | Observable[int] | Observable[float] | Observable[bool]
        An observable whose datatype should match with the type
        of tkinter variable to create.
    var_type: type[VT]
        tkinter variable type to instantiate
    master: tk.Misc | None, optional
        An optional explicit master to use for the tkinter variable.
        If none is provided, the current master from TKML context will be used.
    name: str | None, optional
        Optional explicit TCL variable name to pass to the tkinter variable.
        
    Returns
    -------
    VT
        A tkinter variable of the provided type.

    Raises
    ------
    ValueError
        Master was not provided and could not be determined from the TKML context
    """
    local_master = master if master is not None else _master_ctx.get()
    if local_master is None:
        raise ValueError("TKML variable adapter is missing a contextual master. Provide master manually or use in valid TKML context.")
    
    var = var_type(
        master=local_master,
        value=obs.value if obs.value != ... else None,
        name=name
    )
    # obs -> var 
    obs.observe(var.set, initial_update=False)
    # obs <- var
    def var_cb(self, *_):
        # this doesn't cause recursion because value assignment
        # only propagates when value differs
        obs.value = var.get()
    var.trace_add("write", var_cb)

    return var

def stringvar_adapter(
    obs: Observable[str],
    master: tk.Misc | None = None,
    name: str | None = None
):
    """ shortcut to create a StringVar adapter with `tkvar_adapter` """
    return tkvar_adapter(obs, tk.StringVar, master, name)

def intvar_adapter(
    obs: Observable[int],
    master: tk.Misc | None = None,
    name: str | None = None
):
    """ shortcut to create a IntVar adapter with `tkvar_adapter` """
    return tkvar_adapter(obs, tk.IntVar, master, name)

def doublevar_adapter(
    obs: Observable[float],
    master: tk.Misc | None = None,
    name: str | None = None
):
    """ shortcut to create a DoubleVar adapter with `tkvar_adapter` """
    return tkvar_adapter(obs, tk.DoubleVar, master, name)

def boolvar_adapter(
    obs: Observable[bool],
    master: tk.Misc | None = None,
    name: str | None = None
):
    """ shortcut to create a BooleanVar adapter with `tkvar_adapter` """
    return tkvar_adapter(obs, tk.BooleanVar, master, name)
