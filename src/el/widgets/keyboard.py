"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
14.07.24, 15:17
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

A highly customizable digital keyboard (On Screen Keyboard OSK) that 
can be placed anywhere on the tkinter application and has the
ability to edit registered entry widgets or trigger fallback functions.
Intended for use on touchscreens in combination with touchscreen mode.
Inspiration: https://stackoverflow.com/questions/60136473/how-to-call-and-close-a-virtual-keyboard-made-by-tkinter-using-touchscreen-displ
"""


import enum
import typing
import logging
import dataclasses

import el.widgets.ctkex as ex
import el.ctk_utils as ctku
from el.widgets.toolbar_button import ToolbarButton
from el.lifetime import LifetimeManager, AbstractRegistry, RegistrationID
from el.callback_manager import CallbackManager
from el.observable import MaybeObservable
from el.assets import builtin

from ._deps import *


_log = logging.getLogger(__name__)


@dataclasses.dataclass
class _EditTarget:
    """
    Representation of an entry that is editable using the
    keyboard.
    """
    entry: ex.CTkEntryEx
    select_all_on_begin: bool
    abort_on_focus_out: bool
    disable_focus_pull: bool
    on_begin: typing.Callable[[], None] | None
    on_submit: typing.Callable[[], None] | None
    on_abort: typing.Callable[[], None] | None
    focus_in_reg: RegistrationID
    focus_out_reg: RegistrationID


class SpecialFunction(enum.Enum):
    """Enum of special key functions"""
    DELETE = enum.auto()
    ABORT = enum.auto()
    SUBMIT = enum.auto()

_sf_to_default_asset_name = {
    SpecialFunction.DELETE: "backspace.png",
    SpecialFunction.ABORT: "cancel.png",
    SpecialFunction.SUBMIT: "enter.png",
}


@dataclasses.dataclass(frozen=True)
class Key:
    value: str | SpecialFunction
    height: int = 1
    width: int = 1
    text: str | None = None
    icon: ctk.CTkImage | None = None
    color: ctku.Color | None = None


default_layout: list[list[Key]] = [
    [Key("1"),          Key("2"),   Key("3"),   Key(SpecialFunction.DELETE, text="D")           ],
    [Key("4"),          Key("5"),   Key("6"),   Key(SpecialFunction.ABORT, text="X")            ],
    [Key("7"),          Key("8"),   Key("9"),   Key(SpecialFunction.SUBMIT, height=2, text="R") ],
    [Key("0", width=2), ...,        Key("."),   ...                                     ],
]


class Keyboard(ex.CTkFrameEx, AbstractRegistry):
    def __init__(self, 
        master: tk.Misc,
        btn_width: int = 28,
        btn_height: int = 28,
        gap_size: int = 4,
        layout: list[list[Key]] = default_layout,
        touchscreen_mode: MaybeObservable[bool] = False,
    ):
        super().__init__(master, fg_color="transparent")
        self._lifetime = LifetimeManager()

        self._btn_width = btn_width
        self._btn_height = btn_height
        self._layout = layout
        self._gap_size = gap_size
        self._touchscreen_mode = touchscreen_mode

        self._rows = len(self._layout)
        self._cols = len(self._layout[0])
        self._child_buttons: list[ToolbarButton] = []

        self._sf_icon_cache: dict[SpecialFunction, ctk.CTkImage] = {}

        self._next_target_reg_id: RegistrationID = 0
        self._targets: dict[RegistrationID, _EditTarget] = {}
        self._active_target: _EditTarget | None = None
        self._restore_text: str = ""

        self.on_keypress_fallback = CallbackManager[str | SpecialFunction]()

        self._draw_buttons()

    def _draw_buttons(self) -> None:
        # in case of redraw
        for btn in self._child_buttons:
            btn.destroy()
        self._child_buttons.clear()

        # all cells equal weights
        self.grid_rowconfigure(list(range(self._rows)), weight=1)
        self.grid_columnconfigure(list(range(self._cols)), weight=1)

        # draw all the button keys
        for row in range(self._rows):
            for col in range(self._cols):
                key = self._layout[row][col]
                # skip unpopulated cells or cells that were already populated
                # by an spanning button
                if key is ...:
                    continue
                with self._lifetime():
                    button = ToolbarButton(
                        self, 
                        width=self._btn_width * key.width + self._gap_size * (key.width - 1),
                        height=self._btn_height * key.height + self._gap_size * (key.height - 1),
                        text=key.text if key.text is not None else (str(key.value) if key.icon is None else ""),
                        image=key.icon,
                        fg_color=key.color,
                        touchscreen_mode=self._touchscreen_mode,
                    )
                button.configure(command=lambda k=key: self._handle_key(k))
                button.grid(
                    row=row,
                    rowspan=key.height,
                    column=col,
                    columnspan=key.width,
                    padx=(
                        0 if col == 0 else self._gap_size,
                        0, 
                    ),
                    pady=(
                        0 if row == 0 else self._gap_size,
                        0, 
                    )
                )

    def register_target(
        self, 
        entry: ex.CTkEntryEx,
        select_all_on_begin: bool = False,
        abort_on_focus_out: bool = False,
        disable_focus_pull: bool = False,
        on_begin: typing.Callable[[], None] | None = None,
        on_submit: typing.Callable[[], None] | None = None,
        on_abort: typing.Callable[[], None] | None = None,
    ) -> RegistrationID:
        """
        Registers a new target entry to be made editable
        using the keyboard. This registration can be 
        managed using a `LifetimeManager`.

        Parameters
        ----------
        entry : ex.CTkEntryEx
            entry to be edited (must be an CTkEntryEx)
        select_all_on_begin : bool
            Whether to select the entire content and place cursor at end
            when the entry edit is started. Usually favorable for number inputs.
        abort_on_focus_out : bool = False
            whether to abort when de-focusing the entry instead of submitting
        disable_focus_pull : bool = False
            whether to disable the focus being pulled onto the entry-master
            on submit or abort using the keys. Set this to true if you
            want to manually focus a different widget in the appropriate callbacks.
        on_begin : typing.Callable[[], None], optional
            callback when entry is first selected (focus in)
        on_submit : typing.Callable[[], None], optional
            callback when edit is submitted using the submit button 
            or de-focusing with `abort_on_focus_out`=False
        on_abort : typing.Callable[[], None], optional
            callback when edit is aborted using the abort button 
            or de-focusing with `abort_on_focus_out`=True
        
        Returns
        -------
        RegistrationID
            ID uniquely identifying this registration, for later
            use of `unregister_target()`

        Raises
        ------
        ValueError
            Entry already registered
        """
        if entry in [v.entry for v in self._targets.values()]:
            raise ValueError(f"Entry {entry} is already registered for keyboard {self}")
        # allocate ID
        id = self._next_target_reg_id
        self._next_target_reg_id += 1
        # create callbacks (use persistent interface to be not affected by external unbindings)
        with self._lifetime():
            focus_in_reg = entry.persistent_on_focus_in.register(lambda _, i=id: self._focus_in_handler(i), weak=False)
            focus_out_reg = entry.persistent_on_focus_out.register(lambda _, i=id: self._focus_out_handler(i), weak=False)
        # save configuration
        self._targets[id] = _EditTarget(
            entry=entry,
            select_all_on_begin=select_all_on_begin,
            abort_on_focus_out=abort_on_focus_out,
            disable_focus_pull=disable_focus_pull,
            on_begin=on_begin,
            on_submit=on_submit,
            on_abort=on_abort,
            focus_in_reg=focus_in_reg,
            focus_out_reg=focus_out_reg,
        )
        self._ar_register(id)

        return id

    def unregister_target(
        self,
        id: RegistrationID
    ) -> None:
        """
        Unregisters an entry from being editable by the keyboard.
        If the entry is currently active, it will be left in the
        exact state it is currently in.

        Parameters
        ----------
        id : RegistrationID
            ID of the registration to undo.
            If it is invalid, nothing happens.
        """
        if id in self._targets:
            # unbind the events. since we use the ctkex persistent callbacks, we can do that safely
            # without affecting other bindings.
            self._targets[id].entry.persistent_on_focus_in.remove(self._targets[id].focus_in_reg)
            self._targets[id].entry.persistent_on_focus_out.remove(self._targets[id].focus_out_reg)
            # if this is the active target, leave it as is (not proper end) and just remove
            # the active target.
            if self._active_target is self._targets[id]:
                self._active_target = None
            del self._targets[id]

    @typing.override
    def _ar_unregister(self, id: RegistrationID) -> None:
        return self.unregister_target(id)

    def _start_editing_entry(self, t: _EditTarget) -> None:
        # already active -> do nothing
        if self._active_target is t:
            return
        # another one is active -> end it first
        if self._active_target is not None:
            self._end_editing_entry()
        # activate the new target and save initial text
        self._active_target = t
        self._restore_text = self._active_target.entry.get()
        # if enabled, when we first get focus, we select the entire text content.
        # This makes it easier to edit number entries on the touchscreen
        if self._active_target.select_all_on_begin:
            self._active_target.entry.select_range(0, ctk.END)
            self._active_target.entry.icursor(ctk.END)
        # call the edit begin handler if one is defined
        if self._active_target.on_begin is not None:
            self._active_target.on_begin()

    def _end_editing_entry(self, focus_pull: bool = False) -> None:
        # pull focus out of entry if enabled and wanted
        if not self._active_target.disable_focus_pull and focus_pull:
            self._active_target.entry.master.focus()
        # clear selection and remove active entry
        self._active_target.entry.select_clear()
        self._active_target = None

    def _perform_abort(self) -> None:
        # restore text to initial value and call abort callback
        self._active_target.entry.delete(0, tk.END)
        self._active_target.entry.insert(0, self._restore_text)
        if self._active_target.on_abort is not None:
            self._active_target.on_abort()

    def _perform_submit(self) -> None:
        # call submit callback
        if self._active_target.on_submit is not None:
            self._active_target.on_submit()

    def start_editing(self, id: RegistrationID, focus: bool = True) -> None:
        """
        Manually triggers a certain entry to be edited.
        The entry is identified by the registration ID

        Parameters
        ----------
        id : RegistrationID
            ID of the entry to start editing
        focus : bool = True
            whether to also focus the entry we start to edit
            or not. By default true.
        """
        target = self._targets.get(id, None)
        if target is None:
            return
        if focus:
            target.entry.focus()
        self._start_editing_entry(target)

    def _focus_in_handler(self, id: RegistrationID) -> None:
        self.start_editing(id, focus=False)

    def stop_editing(self, abort: bool = False) -> None:
        """
        Manually stop the current entry from being edited.
        When `abort` is set to True, the edit is aborted,
        otherwise it is submitted

        Parameters
        ----------
        abort : bool = False
            Whether to abort instead of submitting.
        """
        if self._active_target is not None:
            if abort:
                self._perform_abort()
            else:
                self._perform_submit()
            # end editing by deselecting all
            self._end_editing_entry(focus_pull=True)

    def _focus_out_handler(self, id: RegistrationID) -> None:
        target = self._targets.get(id, None)
        if target is None:
            return
        # only respect callbacks from the active target, so no other
        # entry can accidentally cause edit ending
        if self._active_target is target:
            # self._master.focus()
            # if configured so, abort edit, otherwise submit
            if self._active_target.abort_on_focus_out:
                self._perform_abort()
            else:
                self._perform_submit()
            # end editing by deselecting all
            self._end_editing_entry()   # no focus pull, as we already are de-focused here

    def _handle_key(self, key: Key) -> None:
        # if no target is active, we call the fallback handler at the
        # beginning, which may cause a specific entry to be activated
        if self._active_target is None:
            self.on_keypress_fallback.notify_all(key.value)

        # then we check for specific actions that would apply to active entries

        if key.value == SpecialFunction.SUBMIT:
            if self._active_target is not None:
                self._perform_submit()
                self._end_editing_entry(focus_pull=True)

        elif key.value == SpecialFunction.ABORT:
            if self._active_target is not None:
                self._perform_abort()
                self._end_editing_entry(focus_pull=True)

        elif key.value == SpecialFunction.DELETE:
            if self._active_target is not None:
                # delete selection if present
                if self._active_target.entry.select_present():
                    self._active_target.entry.delete(ctk.SEL_FIRST, ctk.SEL_LAST)
                # otherwise delete one character
                else:
                    cursor_index = self._active_target.entry.index(ctk.INSERT)
                    self._active_target.entry.delete(max(cursor_index - 1, 0), cursor_index)

        else:   # insert
            if self._active_target is not None:
                if self._active_target.entry.select_present():
                    self._active_target.entry.delete(ctk.SEL_FIRST, ctk.SEL_LAST)
                    self._active_target.entry.insert(ctk.ANCHOR, key.value)
                else:
                    self._active_target.entry.insert(ctk.INSERT, key.value)

    @typing.override
    def destroy(self):
        self._lifetime.end()
        self._active_target = None
        self._targets.clear()
        return super().destroy()
