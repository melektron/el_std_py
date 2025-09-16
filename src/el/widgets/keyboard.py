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
from el.base import filter_kwargs

from ._deps import *


_log = logging.getLogger(__name__)


@dataclasses.dataclass
class _EditTarget:
    """
    Internal representation of an entry or textbox that is 
    editable using the keyboard.
    This also includes some methods to interact with the actual
    widget, regardless of it's type
    """
    id: RegistrationID
    entry: ex.CTkEntryEx | ex.CTkTextboxEx
    select_all_on_begin: bool
    abort_on_focus_out: bool
    disable_focus_pull: bool
    on_begin: typing.Callable[[], None] | None
    on_submit: typing.Callable[[], None] | None
    on_abort: typing.Callable[[], None] | None
    focus_in_reg: RegistrationID
    focus_out_reg: RegistrationID

    def pull_focus_out(self) -> None:
        """Pulls the focus of the entry onto it's master"""
        self.entry.master.focus()
    
    @property
    def is_disabled(self) -> bool:
        """True if the entry is disabled, False otherwise"""
        return self.entry.cget("state") == "disabled"

    def get_text(self) -> str:
        """Returns the text in the entry"""
        if isinstance(self.entry, ex.CTkEntryEx):
            return self.entry.get()
        if isinstance(self.entry, ex.CTkTextboxEx):
            return self.entry.text.value
    
    def set_text(self, text: str) -> None:
        """Replaces text in the entry with text"""
        if isinstance(self.entry, ex.CTkEntryEx):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)
        if isinstance(self.entry, ex.CTkTextboxEx):
            self.entry.text.value = text
    
    def select_all(self) -> None:
        """Selects the entire text and places cursor at end"""
        if isinstance(self.entry, ex.CTkEntryEx):
            self.entry.select_all()
        if isinstance(self.entry, ex.CTkTextboxEx):
            self.entry.select_all()
            self.entry.see("insert")
    
    def select_clear(self) -> None:
        """Clears the selection (selects nothing)"""
        if isinstance(self.entry, ex.CTkEntryEx):
            self.entry.select_clear()
        if isinstance(self.entry, ex.CTkTextboxEx):
            self.entry.tag_remove("sel", "1.0", tk.END)

    def backspace(self) -> None:
        """
        Performs the action of the backspace key:
        Delete selection if present, otherwise delete a character.
        """
        try:
            # delete selection if present
            sel_start = self.entry.index("sel.first")
            sel_end = self.entry.index("sel.last")
            self.entry.delete(sel_start, sel_end)
        except Exception:
            # otherwise delete one character
            if isinstance(self.entry, ex.CTkEntryEx):
                cursor_index = self.entry.index(ctk.INSERT)
                self.entry.delete(max(cursor_index - 1, 0), cursor_index)
            if isinstance(self.entry, ex.CTkTextboxEx):
                cursor_index = self.entry.index(ctk.INSERT)
                if cursor_index != "1.0":  # avoid deleting before start
                    self.entry.delete(f"{cursor_index} -1c", cursor_index)
    
    def insert_text(self, text: str) -> None:
        """Inserts text at the cursor or selection"""
        if isinstance(self.entry, ex.CTkEntryEx):
            if self.entry.select_present():
                self.entry.delete(ctk.SEL_FIRST, ctk.SEL_LAST)
                self.entry.insert(ctk.ANCHOR, text)
            else:
                self.entry.insert(ctk.INSERT, text)
        if isinstance(self.entry, ex.CTkTextboxEx):
            if self.entry.tag_ranges("sel"):
                self.entry.delete("sel.first", "sel.last")
                self.entry.insert(ctk.INSERT, text)
            else:
                self.entry.insert(ctk.INSERT, text)


class SpecialFunction(enum.Enum):
    """Enum of special key functions"""
    DELETE = enum.auto()
    ABORT = enum.auto()
    SUBMIT = enum.auto()


@dataclasses.dataclass(frozen=True, eq=False)
class Key[CAT = str]:
    value: str | SpecialFunction | CAT
    h: int = 1
    w: int = 1
    text: str | None = None
    icon: ctk.CTkImage | None = None
    color: ctku.Color | None = None
    hover_color: ctku.Color | None = None


@dataclasses.dataclass
class KeyOverlay[CAT = str]:
    """
    Class used for keyboard layer maps to change the visual
    and functional properties of certain keys when an overlay
    layer is active.
    """
    value: str | SpecialFunction | CAT | None = None
    text: str | None = None
    icon: ctk.CTkImage | None = None
    color: ctku.Color | None = None
    hover_color: ctku.Color | None = None


type OverlayLayerType[CAT = str] = dict[str | SpecialFunction | CAT, KeyOverlay[CAT]]


LAYOUT_DEFAULT: list[list[Key]] = [
    [Key("1"),              Key("2"),   Key("3"),   Key(SpecialFunction.DELETE, text="D")       ],
    [Key("4"),              Key("5"),   Key("6"),   Key(SpecialFunction.ABORT, text="X")        ],
    [Key("7"),              Key("8"),   Key("9"),   Key(SpecialFunction.SUBMIT, h=2, text="R")  ],
    [Key("0", w=2), ...,    Key("."),   ...,        ...                                         ],
]


class Keyboard[CAT = str](ex.CTkFrameEx, AbstractRegistry):
    
    def __init__(self, 
        master: tk.Misc,
        btn_width: int = 28,
        btn_height: int = 28,
        gap_size: int = 3,
        layout: list[list[Key[CAT]]] = LAYOUT_DEFAULT,
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
        self._child_buttons: dict[Key[CAT], ToolbarButton] = {}

        self._active_overlay_layer: OverlayLayerType[CAT] | None = None

        self._next_target_reg_id: RegistrationID = 0
        self._targets: dict[RegistrationID, _EditTarget] = {}
        self._active_target: _EditTarget | None = None
        self._restore_text: str = ""

        # Hook called when any target starts to be edited. Called just before the target-specific hook
        self.on_edit_begin = CallbackManager()
        # Hook called when the editing ends, whether via submit or abort. Called just after target-specific hook.
        self.on_edit_end = CallbackManager()
        # Hook called when a key is pressed without an active target, may be used to activate a target.
        self.on_keypress_fallback = CallbackManager[str | SpecialFunction | CAT]()
        # Hook called just before text is inserted
        self.on_pre_insert = CallbackManager[str]()
        # Hook called just after text is inserted
        self.on_post_insert = CallbackManager[str]()
        # Hook called when a key with custom action is pressed in an active target
        self.on_custom_action = CallbackManager[CAT]()

        self._draw_buttons()

    @staticmethod
    def _select_button_text(
        value: str | SpecialFunction | CAT,
        text: str | None, 
        icon: ctk.CTkImage | None = None
    ) -> str:
        """Selects the text of a button depending on value, text and icon"""
        return (
            text  if text is not None 
            else (
                str(value) if icon is None 
                else ""
            )
        )

    def _draw_buttons(self) -> None:
        # in case of redraw
        for btn in self._child_buttons.values():
            btn.destroy()
        self._child_buttons.clear()

        # all cells equal weights
        self.grid_rowconfigure(list(range(self._rows)), weight=1, minsize=self._btn_height)
        self.grid_columnconfigure(list(range(self._cols)), weight=1, minsize=self._btn_width)

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
                        width=self._btn_width * key.w + self._gap_size * (key.w - 1),
                        height=self._btn_height * key.h + self._gap_size * (key.h - 1),
                        text=self._select_button_text(key.value, key.text, key.icon),
                        image=key.icon,
                        fg_color=key.color,
                        hover_color=key.hover_color,
                        touchscreen_mode=self._touchscreen_mode,
                    )
                button.configure(command=lambda k=key: self._handle_key(k))
                button.grid(
                    row=row,
                    rowspan=key.h,
                    column=col,
                    columnspan=key.w,
                    padx=(
                        0 if col == 0 else self._gap_size,
                        0, 
                    ),
                    pady=(
                        0 if row == 0 else self._gap_size,
                        0, 
                    )
                )
                self._child_buttons[key] = button

    def _update_buttons_from_overlay(self) -> None:
        # go through all the buttons and update their visual properties
        for key, button in self._child_buttons.items():
            if (
                self._active_overlay_layer is not None
                and key.value in self._active_overlay_layer
            ):
                # load overlays if an overlay layer is enabled
                overlay = self._active_overlay_layer[key.value]
                value = overlay.value if overlay.value is not None else key.value
                text = overlay.text if overlay.text is not None else key.text
                icon = overlay.icon if overlay.icon is not None else key.icon
                color = overlay.color if overlay.color is not None else key.color
                hover_color = overlay.hover_color if overlay.hover_color is not None else key.hover_color
                
                button.configure(
                    text=self._select_button_text(value, text, icon),
                    image=icon,
                    fg_color=color if color is not None else ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                    hover_color=hover_color if hover_color is not None else ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                )
            else:
                # otherwise just load the normal key values
                button.configure(
                    text=self._select_button_text(key.value, key.text, key.icon),
                    image=key.icon,
                    fg_color=key.color if key.color is not None else ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                    hover_color=key.hover_color if key.hover_color is not None else ctk.ThemeManager.theme["CTkButton"]["hover_color"],
                )
                

    def set_overlay_layer(
        self, overlay: OverlayLayerType[CAT] | None
    ) -> None:
        """
        Sets or disables a keyboard overlay layer to change the function or look 
        of certain keys on the keyboard (e.g. to implement modifiers like shift or alt)

        Parameters
        ----------
        overlay : dict[str  |  SpecialFunction  |  CAT, KeyOverlay[CAT]] | None
            The overlay to apply. This comes in the form of dictionary that maps
            the key values of the keyboard layout to potential KeyOverlay object,
            that overrides certain properties (visual and/or functional). 
            When setting this to None, the default layout is shown again (initial condition).
        """
        self._active_overlay_layer = overlay
        self._update_buttons_from_overlay()

    @property
    def active_overlay_layer(self) -> OverlayLayerType[CAT] | None:
        """the active overlay layer or None if none is active"""
        return self._active_overlay_layer

    def register_target(
        self, 
        entry: ex.CTkEntryEx | ex.CTkTextboxEx,
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
        entry : ex.CTkEntryEx | ex.CTkTextboxEx
            entry to be edited 
            (must be an CTkEntryEx or CTkTextboxEx, normal CTk widgets don't work)
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
            Entry already registered or invalid type
        """
        if not isinstance(entry, (ex.CTkEntryEx, ex.CTkTextboxEx)):
            raise ValueError(f"Entry {entry} is an unsupported widget type: {type(entry)}")
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
            id=id,
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
        # if the entry is disabled, we don't start editing it
        if t.is_disabled:
            # also we focus-pull out of the entry, so it isn't 
            # already focused when enabled (which would prevent
            # you from editing it unless it is de-focused first)
            if not t.disable_focus_pull:
                t.pull_focus_out()
            return
        # another one is active -> end it first
        if self._active_target is not None:
            self._end_editing_entry()
        # activate the new target and save initial text
        self._active_target = t
        self._restore_text = self._active_target.get_text()
        # if enabled, when we first get focus, we select the entire text content.
        # This makes it easier to edit number entries on the touchscreen
        if self._active_target.select_all_on_begin:
            self._active_target.select_all()
        # call the generic edit begin hook
        self.on_edit_begin.notify_all()
        # call the target-specific edit begin handler if one is defined
        if self._active_target.on_begin is not None:
            self._active_target.on_begin()

    def _end_editing_entry(self, focus_pull: bool = False) -> None:
        # pull focus out of entry if enabled and wanted
        if not self._active_target.disable_focus_pull and focus_pull:
            self._active_target.pull_focus_out()
        # clear selection and remove active entry
        self._active_target.select_clear()
        self._active_target = None

    def _perform_abort(self) -> None:
        # restore text to initial value and call abort callback
        self._active_target.set_text(self._restore_text)
        if self._active_target.on_abort is not None:
            self._active_target.on_abort()
        # call the generic edit end hook
        self.on_edit_end.notify_all()

    def _perform_submit(self) -> None:
        # call submit callback
        if self._active_target.on_submit is not None:
            self._active_target.on_submit()
        # call the generic edit end hook
        self.on_edit_end.notify_all()

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

    @property
    def active_target_id(self) -> RegistrationID | None:
        """
        Returns
        -------
        RegistrationID | None
            The registration ID of the target that is currently being edited
            or None if no target is currently being edited.
        """
        if self._active_target is None:
            return None
        return self._active_target.id

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

    def _handle_key(self, key: Key[CAT]) -> None:
        # apply overlay if applicable
        if (self._active_overlay_layer is not None 
            and key.value in self._active_overlay_layer
            and (aol := self._active_overlay_layer[key.value]) is not None
        ):
            value = aol.value
        else:
            value = key.value
        
        # if no target is active, we call the fallback handler at the
        # beginning, which may cause a specific entry to be activated
        if self._active_target is None:
            self.on_keypress_fallback.notify_all(value)

        # then we check for specific actions that would apply to active entries

        if value == SpecialFunction.SUBMIT:
            if self._active_target is not None:
                self._perform_submit()
                self._end_editing_entry(focus_pull=True)

        elif value == SpecialFunction.ABORT:
            if self._active_target is not None:
                self._perform_abort()
                self._end_editing_entry(focus_pull=True)

        elif value == SpecialFunction.DELETE:
            if self._active_target is not None:
                self._active_target.backspace()

        elif isinstance(value, str):   # insert
            self.on_pre_insert.notify_all(value)
            if self._active_target is not None:
                self._active_target.insert_text(value)
            self.on_post_insert.notify_all(value)
        
        else:   # custom action, forward to custom action handler
            self.on_custom_action.notify_all(value)


    @typing.override
    def destroy(self):
        self._lifetime.end()
        self._active_target = None
        self._targets.clear()
        return super().destroy()
