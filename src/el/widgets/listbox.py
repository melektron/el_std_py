"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
31.10.24, 18:45
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

A fully dynamic and fully typed CTkListBox widget based on the concepts
of Akascape's CtkListbox widget: https://github.com/Akascape/CTkListbox/

Although based on the concept, this is a completely independent 
implementation that is focused on fixing some of the annoyances with Akascape's 
widget.
"""


import sys
from typing import Any, Optional, Union, Literal, Hashable
from itertools import zip_longest
from dataclasses import dataclass
#import cProfile
#import pstats

from ._deps import *
from el.callback_manager import CallbackManager
from el.observable import Observable

@dataclass
class OptionEntry[DT]:
    user_data: DT
    label: str
    disabled: bool = False
    icon: ctk.CTkImage | None = None
    selected: bool = False

@dataclass
class _InternalOptionEntry[DT](OptionEntry[DT]):
    button: ctk.CTkButton = ...


# DT is the internal user-specified data that can be stored with each option
# to uniquely identify it independent of the index and the displayed text.
# This must be hashable to be contained in the selection set
class CTkListbox[DT: Hashable](ctk.CTkScrollableFrame):
    def __init__(
        self,
        master: Any,
        width: int = 100,
        height: int = 150,

        corner_radius: Optional[Union[int, str]] = None,
        border_width: Optional[Union[int, str]] = None,

        bg_color: Union[str, tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_color: Optional[Union[str, tuple[str, str]]] = None,
        scrollbar_fg_color: Optional[Union[str, tuple[str, str]]] = None,
        scrollbar_button_color: Optional[Union[str, tuple[str, str]]] = None,
        scrollbar_button_hover_color: Optional[Union[str, tuple[str, str]]] = None,

        option_fg_color: Optional[Union[str, tuple[str, str]]] = None,
        option_hover_color: Optional[Union[str, tuple[str, str]]] = None,
        option_selected_color: Optional[Union[str, tuple[str, str]]] = None,
        option_text_color: Optional[Union[str, tuple[str, str]]] = None,
        option_text_color_disabled: Optional[Union[str, tuple[str, str]]] = None,
        option_text_font: Optional[Union[tuple, ctk.CTkFont]] = None,
        option_compound: Literal["top", "left", "bottom", "right"] = "left",
        option_anchor: Literal["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"] = "w",
        option_hover: bool = True,     # Whether to enable hover effects

#        multiple_selection: bool = False,
#        listvariable=None,
#        command=None,
        ):

        super().__init__(
            master=master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            scrollbar_fg_color=scrollbar_fg_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
        )
        self.grid_columnconfigure(0, weight=1)

        # fix mouse wheel on Linux (wild botch)
        # https://github.com/TomSchimansky/CustomTkinter/issues/1356#issuecomment-1474104298
        if sys.platform.startswith("linux"):
            self.bind_all("<Button-4>", lambda e: self._parent_canvas.yview("scroll", -1, "units"))
            self.bind_all("<Button-5>", lambda e: self._parent_canvas.yview("scroll", 1, "units"))

        # self._scrollbar.grid_configure(padx=(0, border_width + 4))
        # self._scrollbar.configure(width=12)

        # by default, make option buttons the same color as the frame
        self._option_fg_color = (
            self._parent_frame._fg_color if option_fg_color is None else option_fg_color
        )
        self._option_hover_color = (
            ctk.ThemeManager.theme["CTkButton"]["hover_color"]
            if option_hover_color is None
            else option_hover_color
        )
        self._option_selected_color = (
            ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            if option_selected_color is None
            else option_selected_color
        )
        self._option_text_color = (
            ctk.ThemeManager.theme["CTkButton"]["text_color"]
            if option_text_color is None
            else option_text_color
        )
        self._option_text_color_disabled = (
            ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"]
            if option_text_color_disabled is None
            else option_text_color_disabled
        )
        self._option_text_font = option_text_font
        self._option_compound = option_compound
        self._option_anchor = option_anchor
        self._option_hover = option_hover

        # internal list of option entries representing the state
        # that is actually currently shown on the UI. No references
        # to this list or it's elements are ever to be returned to the user.
        self._internal_options: list[_InternalOptionEntry[DT]] = []

        # callback whenever an entry is clicked.
        # parameters: index of the element in the listbox and option entry data
        self.on_option_clicked = CallbackManager[int, OptionEntry]()
        # observable list of all selected indices (max 1 if multiselect is disabled)
        self.selected_indices = Observable[set[int]]([])
        # observable list of all selected data objects (max 1 if multiselect is disabled)
        self.selected_data = Observable[set[DT]]([])

    def _create_public_option_object(self, option: _InternalOptionEntry) -> OptionEntry:
        """
        Returns a public option data object representing the internal one.
        User data is not deep-copied, so it may be referencing the same instance.
        """
        return OptionEntry(
            user_data=option.user_data,
            label=option.label,
            disabled=option.disabled,
            icon=option.icon,
            selected=option.selected,
        )

    def get_options(self) -> list[OptionEntry]:
        """
        Generates a list of all current options. This list contains
        a copy of the option elements, so mutating it will not
        affect the UI until calling set_options() with the
        modified list.
        """
        return [
            self._create_public_option_object(option)
            for option in self._internal_options
        ]

    def set_options(self, new_options: list[OptionEntry[DT]]) -> None:
        """
        Sets the options of the listbox, replacing the old ones.
        This granularly walks through the existing options, comparing differences 
        and only updating tk elements where necessary in an effort to keep slow tk 
        calls to a minimum.
        """

        created_options: list[_InternalOptionEntry[DT]] = []
        deleted_options_from: int = len(self._internal_options) # by default delete no items, i.e. delete starting after the list

        for index, (old_option, new_option) in enumerate(zip_longest(self._internal_options, new_options, fillvalue=None)):
            # if this is a new entry past the existing list extent, create a new button
            if old_option is None:
                btn = self._create_option_button(index, new_option)
                created_options.append(_InternalOptionEntry(
                    user_data=new_option.user_data,
                    label=new_option.label,
                    disabled=new_option.disabled,
                    icon=new_option.icon,
                    selected=new_option.selected,
                    button=btn,
                ))

            # If there is an old option but no matching new one in the position, delete the old button
            elif new_option is None:
                old_option.button.grid_forget()
                old_option.button.destroy()
                old_option.button = None
                # save the first index that we need to delete
                if deleted_options_from > index:
                    deleted_options_from = index

            # if there is an old and a new option, see if there are any changes and update the button if required
            else:
                changes: dict[str, Any] = {}
                require_redraw: bool = False
                need_new_button: bool = False

                if old_option.user_data != new_option.user_data:
                    old_option.user_data = new_option.user_data
                if old_option.label != new_option.label:
                    old_option.label = new_option.label
                    changes["text"] = new_option.label
                if old_option.disabled != new_option.disabled:
                    old_option.disabled = new_option.disabled
                    changes["state"] = "disabled" if new_option.disabled else "normal"
                if old_option.icon is not new_option.icon:   # compare instances, because CTkImage will never equal each other
                    # ctk unfortunately does not properly handle removing icons,
                    # so we need to create a new button when removing images
                    if old_option.icon is not None and new_option.icon is None:
                        need_new_button = True
                    old_option.icon = new_option.icon
                    changes["image"] = new_option.icon
                    require_redraw = True   # image does not automatically trigger redraw
                if old_option.selected != new_option.selected:
                    old_option.selected = new_option.selected
                    changes["fg_color"] = (
                        self._option_selected_color
                        if new_option.selected
                        else self._option_fg_color
                    )
                
                if need_new_button:
                    old_option.button.grid_forget()
                    old_option.button.destroy()
                    old_option.button = self._create_option_button(index, old_option)
                elif len(changes) != 0:
                    old_option.button.configure(require_redraw=require_redraw, **changes)


        # delete no longer existing entries and add new ones
        self._internal_options = self._internal_options[:deleted_options_from] + created_options
        # update selection sets
        self.selected_indices.value = set(
            i for i, option in enumerate(self._internal_options) if option.selected
        )
        self.selected_data.value = set(
            option.user_data for option in self._internal_options if option.selected
        )

        #cProfile.runctx("self.update()", globals(), locals(), "my_func_stats")
        #p = pstats.Stats("my_func_stats")
        #p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
    
    def _create_option_button(self, index: int, option: OptionEntry) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            master=self,
            fg_color=self._option_selected_color if option.selected else self._option_fg_color,
            hover_color=self._option_hover_color,
            text_color=self._option_text_color,
            text_color_disabled=self._option_text_color_disabled,

            text=option.label,
            font=self._option_text_font,
            image=option.icon,
            state="disabled" if option.disabled else "normal",
            hover=self._option_hover,
            compound=self._option_compound,
            anchor=self._option_anchor,

            command=lambda i=index: self._on_option_clicked(i)
        )
        # place with bottom padding to get space between buttons
        btn.grid(row=index, column=0, padx=0, pady=(0, 5), sticky="nsew")
        return btn

    def _on_option_clicked(self, index: int) -> None:
        """ Option button click event handler """
        option = self._internal_options[index]
        # disabled button should not produce cb in the first place
        # but check anyway just to make sure
        if option.disabled:
            return
        if self.on_option_clicked.has_callbacks:
            self.on_option_clicked.notify_all(index, self._create_public_option_object(option))
        self._update_selected(index, option, not option.selected)

    def _update_selected(self, index: int, option: _InternalOptionEntry[DT], selected: bool) -> None:
        """ updates the selected state and reconfigures the button accordingly """
        option.selected = selected

        # add/remove element from selection sets
        if option.selected:
            if index not in self.selected_indices.value:
                self.selected_indices.value.add(index)
                self.selected_indices.force_notify()
            if option.user_data not in self.selected_data.value:
                self.selected_data.value.add(option.user_data)
                self.selected_data.force_notify()
        else:
            if index in self.selected_indices.value:
                self.selected_indices.value.remove(index)
                self.selected_indices.force_notify()
            if option.user_data in self.selected_data.value:
                self.selected_data.value.remove(option.user_data)
                self.selected_data.force_notify()

        # update button
        option.button.configure(
            fg_color=(
                self._option_selected_color
                if option.selected
                else self._option_fg_color
            )
        )
