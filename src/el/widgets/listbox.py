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
from typing import Any, Optional, Union, Literal, Hashable, Iterable, override
from itertools import zip_longest
from dataclasses import dataclass
# import cProfile
# import pstats

from ._deps import *
from el.callback_manager import CallbackManager
from el.observable import Observable

@dataclass
class OptionEntry[IT: Hashable]:
    id: IT
    label: str
    disabled: bool = False
    icon: ctk.CTkImage | None = None

@dataclass
class _InternalOptionEntry[IT](OptionEntry[IT]):
    selected: bool = False
    button: ctk.CTkButton = ...


# IT is the user-specified option ID that can be stored with each option
# to uniquely identify it independent of the index and the displayed text.
# This must be hashable to be contained in the selection set and in dict keys
class CTkListbox[IT: Hashable](ctk.CTkScrollableFrame):
    def __init__(
        self,
        master: Any,
        multiselect_mode: Literal["disabled", "toggle", "modifier"] = "disabled",

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
        option_hover: bool = True,
        ):
        """
        ListBox Widget that can shows a set of options that the user can select.
        
        Options are configured using the set_options() method, which takes a list of OptionEntry dataclass objects. Each object represents an option and contains a unique, user defined ID of the option, the text to show in the list, an optional icon and whether the option is currently disabled. Disabled options cannot be selected. One can also use get_options() to get back a list of the current options.
        
        Each option is identified by it's unique ID, which should not change, even if new options are added to the ListBox and the position of an option therefore changes. The CTkListBox makes sure that an option with certain ID stays selected even if more options are added, causing it's position in the listbox to change.

        Options can also be identified by their index in the listbox, though, as mentioned before, those indices can change as new options are added or old ones are removed. 

        Depending on the 'multiselect_mode' parameter, the user can either select only a single option ("disabled"), can select multiple options by toggling them when clicking ("toggle") or combination of these options by using the Shift (range-select) and Ctrl (toggle-select) modifier keys. Pressing escape always clears the selection.

        A set of currently selected options can be obtained using the observable 'selected_indices' and 'selected_ids' properties.
        Developers can also register a callback using the 'on_option_clicked' callback manager to be notified when the user clicks on an option (if it is not disabled).

        Options can programmatically be selected or deselected using the set_selected_by_id() or set_selected_by_index() methods. The the by_id version is to be used if an option is to be uniquely identified, the index version should only ever be used if you want to select an option at a specific position (maybe some UI feature) and don't care about what option that is.

        
        Parameters
        ----------
        master : Any
            Master widget or window
        multiselect_mode : Literal[&quot;disabled&quot;, &quot;toggle&quot;, &quot;modifier&quot;], optional
            Behavior of multiple selection, by default "disabled".
            - "**disabled**": Only one option can be selected. When clicking on another one, the previous one is unselected. Clicking on an already selected option does nothing.
            - "**toggle**": Multiple options can be selected. Clicking on an option toggles it's selected state.
            - "**modifier**": Multiple options can be selected using modifier keys.<br> By *default* this be haves like "disabled".<br> When holding the *Control key* (or Command for Mac) it behaves like "toggle", clicked options will be added to or removed from the selection. <br> When holding the *Shift key*, it behaves like a range selection. This works as expected from other common listbox implementations. If the user first selects one option (possibly with Control to add it to the existing selection) and can then clicks another option while holding shift, all options between the two are selected. Other options previously selected are maintained. Clicking multiple times while holding shift, changes the end of the range select window, while the first point stays the same. Clicking again with Control or no modifier resets the first end of the range selection.
        width : int, optional
            width of the listbox widget, by default 100
        height : int, optional
            height of the listbox widget, by default 150
        corner_radius : Optional[Union[int, str]], optional
            corner radius of the listbox frame, by default according to theme
        border_width : Optional[Union[int, str]], optional
            border width of the listbox frame, by default according to theme
        bg_color : Union[str, tuple[str, str]], optional
            background color that the listbox is placed on, by default "transparent" (selected automatically depending on background)
        fg_color : Optional[Union[str, tuple[str, str]]], optional
            foreground (fill) color of the listbox frame, by default according to theme
        border_color : Optional[Union[str, tuple[str, str]]], optional
            border color of the listbox frame, by default according to theme
        scrollbar_fg_color : Optional[Union[str, tuple[str, str]]], optional
            foreground color AROUND the scrollbar, by default according to theme
        scrollbar_button_color : Optional[Union[str, tuple[str, str]]], optional
            color of the scrollbar button itself, by default according to theme
        scrollbar_button_hover_color : Optional[Union[str, tuple[str, str]]], optional
            color of the scrollbar button when hovered, by default according to theme
        option_fg_color : Optional[Union[str, tuple[str, str]]], optional
            foreground color of an option button in deselected state, by default the fill color of the frame
        option_hover_color : Optional[Union[str, tuple[str, str]]], optional
            foreground color of an option button when hovered, by default according to theme
        option_selected_color : Optional[Union[str, tuple[str, str]]], optional
            foreground color of selected options, by default according to theme
        option_text_color : Optional[Union[str, tuple[str, str]]], optional
            text color of options, by default according to theme
        option_text_color_disabled : Optional[Union[str, tuple[str, str]]], optional
            text color of disabled options, by default according to theme
        option_text_font : Optional[Union[tuple, ctk.CTkFont]], optional
            font of the option labels, by default according to theme
        option_compound : Literal[&quot;top&quot;, &quot;left&quot;, &quot;bottom&quot;, &quot;right&quot;], optional
            how to arrange teh optional option icon relative to the text, by default "left"
        option_anchor : Literal[&quot;n&quot;, &quot;ne&quot;, &quot;e&quot;, &quot;se&quot;, &quot;s&quot;, &quot;sw&quot;, &quot;w&quot;, &quot;nw&quot;, &quot;center&quot;], optional
            where to anchor the text in each option, by default "w"
        option_hover : bool, optional
            whether to enable hover effect on the option buttons, by default True
        
        """

        super().__init__(
            master=master,
            corner_radius=corner_radius,
            border_width=border_width,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            scrollbar_fg_color=scrollbar_fg_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
        )
        # prevent the dimensions being defined by the inner canvas
        self._parent_frame.grid_propagate(False)
        # set the dimensions here which will configure them on the parent frame, 
        # as the constructor of ScrollableFrame sets the size of the internal
        # canvas which we don't want
        self._set_dimensions(width=width, height=height)
        self.grid_columnconfigure(0, weight=1)

        # fix mouse wheel on Linux
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

        self._multiselect_mode: Literal["disabled", "toggle", "modifier"] = multiselect_mode

        # internal list of option entries representing the state
        # that is actually currently shown on the UI. No references
        # to this list or it's elements are ever to be returned to the user.
        self._internal_options: list[_InternalOptionEntry[IT]] = []
        # internal mapping to get the index of an option with particular id
        self._id_to_index: dict[IT, int] = {}

        # index of the last selected option for range-multiselect
        self._last_selected_index: int | None = None
        # the set of last range-selected options to be modified again
        self._last_range_select_set: set[int] = set()

        # callback whenever an entry is clicked.
        # parameters: index of the element in the listbox and option entry data
        self.on_option_clicked = CallbackManager[int, OptionEntry[IT]]()
        # observable set of all selected indices (max 1 if multiselect is disabled)
        self.selected_indices = Observable[set[int]]([])
        # observable set of all selected IDs (max 1 if multiselect is disabled)
        self.selected_ids = Observable[set[IT]]([])

        # bindings to detect key presses
        # self._shift_pressed is already provided by CTkScrollableFrame
        self._ctrl_pressed: bool = False
        if sys.platform.startswith("darwin"):
            # TODO: verify that this works
            self.bind_all("<KeyPress-Meta_L>", self._keyboard_ctrl_press_all, add="+")
            self.bind_all("<KeyRelease-Meta_L>", self._keyboard_ctrl_release_all, add="+")
        else:
            self.bind_all("<KeyPress-Control_L>", self._keyboard_ctrl_press_all, add="+")
            self.bind_all("<KeyPress-Control_R>", self._keyboard_ctrl_press_all, add="+")
            self.bind_all("<KeyRelease-Control_L>", self._keyboard_ctrl_release_all, add="+")
            self.bind_all("<KeyRelease-Control_R>", self._keyboard_ctrl_release_all, add="+")

        # variable to track when the listbox "has focus". The listbox is considered
        # to have focus when the user clicks anywhere inside it. As soon as the user clicks
        # outside it, it is considered no longer in focus
        self._has_focus: bool = False
        self.bind_all("<Button-1>", self._clicked_anywhere, add="+")

        # escape to clear the selection
        self.bind_all("<KeyPress-Escape>", self._keyboard_escape_press_all, add="+")

    def _keyboard_ctrl_press_all(self, e: tk.Event) -> None:
        self._ctrl_pressed = True
    def _keyboard_ctrl_release_all(self, _) -> None:
        self._ctrl_pressed = False

    def _check_if_master_is_scroll_frame(self, widget: tk.Widget):
        if widget == self._parent_frame:
            return True
        elif hasattr(widget, "master") and widget.master is not None:
            return self._check_if_master_is_scroll_frame(widget.master)
        else:
            return False

    def _clicked_anywhere(self, e: tk.Event) -> None:
        if self._check_if_master_is_scroll_frame(e.widget):
            self._has_focus = True
        else:
            self._has_focus = False

    def _keyboard_escape_press_all(self, _) -> None:
        if self._has_focus:
            # deselect all options
            for i in self.selected_indices.value:
                prev_opt = self._internal_options[i]
                prev_opt.selected = False
                self._update_button_selected(prev_opt)
            # update selection sets
            self.selected_indices.value = set()
            self.selected_ids.value = set()
    
    @override
    def _set_scaling(self, new_widget_scaling, new_window_scaling):
        # we skip the CTkScrollableFrame parent, as we don't like it's behavior
        CTkScalingBaseClass._set_scaling(new_widget_scaling, new_window_scaling)
        # changed this to the frame instead of canvas, as we want to fix the outer frame size.
        # we also can skip applying the scaling here, as the _parent_frame is already a ctk widget
        self._parent_frame.configure(
            width=self._desired_width,
            height=self._desired_height
        )

    @override
    def _set_dimensions(self, width=None, height=None):
        if width is not None:
            self._desired_width = width
        if height is not None:
            self._desired_height = height
        # changed this to the frame instead of canvas, as we want to fix the outer frame size.
        # we also can skip applying the scaling here, as the _parent_frame is already a ctk widget
        self._parent_frame.configure(
            width=self._desired_width,
            height=self._desired_height
        )

    def _create_public_option_object(self, option: _InternalOptionEntry) -> OptionEntry:
        """
        Returns a public OptionEntry object representing the internal one.
        ID and icon are not deep-copied, so it may be referencing the same instance.
        """
        return OptionEntry(
            id=option.id,
            label=option.label,
            disabled=option.disabled,
            icon=option.icon
        )

    def get_options(self) -> list[OptionEntry]:
        """Generates a list of all current options. 

        Returns
        -------
        list[OptionEntry]
            List of all current options. This list contains
            a copy of the option elements, so mutating it will not
            affect the UI until calling set_options() with the
            modified list.
        """
        return [
            self._create_public_option_object(option)
            for option in self._internal_options
        ]

    def set_options(self, new_options: list[OptionEntry[IT]]) -> None:
        """Sets the options of the listbox, replacing the old ones.
        This granularly walks through the existing options, comparing differences 
        and only updating tk elements where necessary in an effort to keep slow tk 
        calls to a minimum.

        Options are placed in the listbox in the provided order. Selection
        state is retained for objects with the same ID, even if their position has changed.
        Selected objects that have been removed from the list will also be removed from the
        selection set, notifying all observers.

        Parameters
        ----------
        new_options : list[OptionEntry[IT]]
            List of options to show in the listbox
        """

        created_options: list[_InternalOptionEntry[IT]] = []
        deleted_options_from: int = len(self._internal_options) # by default delete no items, i.e. delete starting after the list

        for index, (old_option, new_option) in enumerate(zip_longest(self._internal_options, new_options, fillvalue=None)):
            # if this is a new entry past the existing list extent, create a new button
            if old_option is None:
                btn = self._create_option_button(index, new_option)
                created_options.append(_InternalOptionEntry(
                    id=new_option.id,
                    label=new_option.label,
                    disabled=new_option.disabled,
                    icon=new_option.icon,
                    selected=new_option.id in self.selected_ids.value,
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

                if old_option.id != new_option.id:
                    old_option.id = new_option.id
                    # if the ID changed, we need to check if this ID
                    # is still one that is currently selected. This happens most
                    # commonly when element positions change
                    new_selected = new_option.id in self.selected_ids.value
                    if old_option.selected != new_selected:
                        old_option.selected = new_selected
                        changes["fg_color"] = (
                            self._option_selected_color
                            if old_option.selected
                            else self._option_fg_color
                        )
                if old_option.label != new_option.label:
                    old_option.label = new_option.label
                    changes["text"] = new_option.label
                if old_option.disabled != new_option.disabled:
                    old_option.disabled = new_option.disabled
                    changes["state"] = "disabled" if new_option.disabled else "normal"
                if old_option.icon is not new_option.icon:   # compare instances, because CTkImage will never equal each other
                    # ctk unfortunately does not properly handle removing icons,
                    # so we need to create a new button when removing the image
                    if old_option.icon is not None and new_option.icon is None:
                        need_new_button = True
                    old_option.icon = new_option.icon
                    changes["image"] = new_option.icon
                    require_redraw = True   # image does not automatically trigger redraw

                if need_new_button:
                    old_option.button.grid_forget()
                    old_option.button.destroy()
                    old_option.button = self._create_option_button(index, old_option)
                elif len(changes) != 0:
                    old_option.button.configure(require_redraw=require_redraw, **changes)

        # delete no longer existing entries and add new ones
        self._internal_options = self._internal_options[:deleted_options_from] + created_options
        # update data->index mapping
        self._id_to_index = {
            o.id: i for i, o in enumerate(self._internal_options)
        }

        # update selection sets to remove all previously selected elements that don't exist anymore
        self.selected_indices.value = set(
            i for i, option in enumerate(self._internal_options) if option.selected
        )
        self.selected_ids.value = set(
            option.id for option in self._internal_options if option.selected
        )

        # update last selected index and set so options are only kept if they are still selected and exist in the list
        if self._last_selected_index is not None and self._last_selected_index not in self.selected_indices.value:
            self._last_selected_index = None
        self._last_range_select_set = self._last_range_select_set.intersection(self.selected_indices.value)

        # cProfile.runctx("self.update()", globals(), locals(), "my_func_stats")
        # p = pstats.Stats("my_func_stats")
        # p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

    def set_selected_by_index(
        self,
        selected: bool,
        indices: Iterable[int],
        *,
        keep_last: bool = True,
        notify: bool = True,
    ) -> None:     
        """
        Selects or deselects an option or a set of options identified by their index in the listbox.

        Parameters
        ----------
        selected : bool
            Whether to select or deselect the options.
        indices : Iterable[int]
            Index or indices of the options to modify
        keep_last : bool, optional
            Whether to keep the last range-select element or override it with the newly
            selected one (None for deselect). Usually you don't want to do this during 
            programmatic selection as to not disturb user interactions, so this defaults to True.
        notify : bool, optional
            Whether to notify observers. Disable this if you whish to aggregate updates 
            of multiple calls. Defaults to True.
        
        Raises
        ------
        IndexError
            If an out-of-range option index is passed to this function
        """

        for i in indices:
            if i >= len(self._internal_options):
                raise IndexError(f"No option with index '{i}' exists in this listbox")

            if selected:
                self._perform_add_select(i, self._internal_options[i], keep_last=keep_last, notify=notify)
            else:
                self._perform_deselect(i, self._internal_options[i], keep_last=keep_last, notify=notify)

    def set_selected_by_id(
        self,
        selected: bool,
        ids: Iterable[IT],
        *,
        keep_last: bool = True,
        notify: bool = True,
    ) -> None:     
        """
        Selects or deselects an option or a set of options identified by unique ID.

        Parameters
        ----------
        selected : bool
            Whether to select or deselect the options.
        ids : Iterable[IT]
            ID or IDs of the options to modify
        keep_last : bool, optional
            Whether to keep the last range-select element or override it with the newly
            selected one (None for deselect). Usually you don't want to do this during 
            programmatic selection as to not disturb user interactions, so this defaults to True.
        notify : bool, optional
            Whether to notify observers. Disable this if you whish to aggregate updates 
            of multiple calls. Defaults to True.
        
        Raises
        ------
        KeyError
            If an invalid ID is passed to this function
        IndexError
            If an out-of-range option index is found internally (should never happen)
        """
        try:
            self.set_selected_by_index(
                selected=selected,
                indices=[self._id_to_index[id] for id in ids],
                keep_last=keep_last,
                notify=notify
            )
        except KeyError as e:
            raise KeyError(f"No option with ID {e} exists in this listbox")

    def _create_option_button(self, index: int, option: OptionEntry) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            master=self,
            fg_color=self._option_selected_color if option.id in self.selected_ids.value else self._option_fg_color,
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
        clicked_option = self._internal_options[index]
        # disabled button should not produce cb in the first place
        # but check anyway just to make sure
        if clicked_option.disabled:
            return

        if self.on_option_clicked.has_callbacks:
            self.on_option_clicked.notify_all(index, self._create_public_option_object(clicked_option))

        match self._multiselect_mode:

            # no multiselect (only one item can be selected at any point)
            case "disabled":
                self._perform_single_select(index, clicked_option)

            # multiselect by making all options toggles
            case "toggle":
                self._perform_toggle_select(index, clicked_option)

            # multiselect by usually behaving like single selection,
            # behaving like toggle selection when ctrl is pressed and
            # having special range-selection behavior if shift is pressed
            case "modifier":

                # ctrl key means "add/remove"
                if self._ctrl_pressed:
                    self._perform_toggle_select(index, clicked_option)
                    self._last_range_select_set.clear() # no range select

                # shift key means "range select"
                elif self._shift_pressed:
                    # if we don't have any previously selected element yet,
                    # simply add this one to the selection
                    if self._last_selected_index is None:
                        self._perform_add_select(index, clicked_option)

                    # otherwise we can select all items between the last and this
                    # option
                    else:
                        is_reverse = index < self._last_selected_index
                        final_selected_range = set(range(
                            self._last_selected_index,
                            index + (-1 if is_reverse else 1),
                            -1 if is_reverse else 1
                        ))
                        # see which elements are to be newly selected because they were not included
                        # in the previous range selection (if last selection operation was toggle or single,
                        # then the last set is cleared and all elements are to be selected, if the last range
                        # was greater than this new one, we might need to select no new elements)
                        to_be_selected = final_selected_range.difference(self._last_range_select_set)

                        # all the elements that were previously selected but are no longer contained
                        # in the new selection range
                        to_be_deselected = self._last_range_select_set.difference(final_selected_range)

                        # update the actual button selection
                        # here we keep the last selected index in place, so the user can modify this range
                        # again, and we don't notify the observers, as we will do one cumulative notify
                        # at the end
                        for i in to_be_deselected:
                            self._perform_deselect(i, self._internal_options[i], keep_last=True, notify=False)
                        for i in to_be_selected:
                            self._perform_add_select(i, self._internal_options[i], keep_last=True, notify=False)

                        # now notify all listeners if the selection changed
                        if final_selected_range != self._last_range_select_set:
                            self.selected_indices.force_notify()
                            self.selected_ids.force_notify()
                            # save new range selection set in case it is modified again
                            self._last_range_select_set = final_selected_range

                else:
                    self._perform_single_select(index, clicked_option)
                    self._last_range_select_set.clear() # no range select

    def _perform_single_select(self, index: int, option: _InternalOptionEntry) -> None:
        """
        selects an option and deselects all others
        """
        # deselect previously selected options
        for i in self.selected_indices.value:
            prev_opt = self._internal_options[i]
            prev_opt.selected = False
            self._update_button_selected(prev_opt)
        # select this one
        option.selected = True
        self._update_button_selected(option)
        self._last_selected_index = index
        # update selection sets all in one go
        self.selected_indices.value = set((index, ))
        self.selected_ids.value = set((option.id, ))

    def _perform_add_select(self, index: int, option: _InternalOptionEntry, *, keep_last: bool = False, notify: bool = True) -> None:
        """
        adds the provided option to the selection. If it is already selected, 
        or disabled, nothing happens.
        """
        if option.selected or option.disabled:
            return

        option.selected = True
        if not keep_last:
            self._last_selected_index = index

        # update button look
        self._update_button_selected(option)

        # add element to selection sets
        if index not in self.selected_indices.value:
            self.selected_indices.value.add(index)
            if notify:
                self.selected_indices.force_notify()
        if option.id not in self.selected_ids.value:
            self.selected_ids.value.add(option.id)
            if notify:
                self.selected_ids.force_notify()

    def _perform_deselect(self, index: int, option: _InternalOptionEntry, keep_last: bool = False, notify: bool = True) -> None:
        """
        removes the provided option from the selection. If it wasn't selected before
        or is disabled, nothing happens
        """
        if not option.selected or option.disabled:
            return

        option.selected = False
        if not keep_last:
            self._last_selected_index = None

        # update button look
        self._update_button_selected(option)

        # remove element from selection sets
        if index in self.selected_indices.value:
            self.selected_indices.value.remove(index)
            if notify:
                self.selected_indices.force_notify()
        if option.id in self.selected_ids.value:
            self.selected_ids.value.remove(option.id)
            if notify:
                self.selected_ids.force_notify()

    def _perform_toggle_select(self, index: int, option: _InternalOptionEntry) -> None:
        """
        toggles an option's selected state
        """
        option.selected = not option.selected
        # if we selected an item, we keep it as last index
        # otherwise there is no last selected index
        if option.selected:
            self._last_selected_index = index
        else:
            self._last_selected_index = None
        # update button look
        self._update_button_selected(option)

        # add/remove element from selection sets
        if option.selected:
            if index not in self.selected_indices.value:
                self.selected_indices.value.add(index)
                self.selected_indices.force_notify()
            if  option.id not in self.selected_ids.value:
                self.selected_ids.value.add(option.id)
                self.selected_ids.force_notify()
        else:
            if index in self.selected_indices.value:
                self.selected_indices.value.remove(index)
                self.selected_indices.force_notify()
            if option.id in self.selected_ids.value:
                self.selected_ids.value.remove(option.id)
                self.selected_ids.force_notify()

    def _update_button_selected(self, option: _InternalOptionEntry[IT]) -> None:
        """ updates the selected state and reconfigures the button accordingly """
        option.button.configure(
            fg_color=(
                self._option_selected_color
                if option.selected
                else self._option_fg_color
            )
        )
