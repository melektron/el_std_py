## Bugfixes


## Enhancements
- `el.widgets.keyboard.Keyboard`
  - ability to see what if any target is currently being edited using the `active_target_id` property
  - added custom key actions and overlay layer support
  - added pre and post insert hooks
  - generalized implementation to support multiple target types
    - added support for `CTkTextBoxEx` targets
  - added global `on_edit_begin` and `on_edit_end` hooks, e.g. to show/hide keyboard when editing begins/ends
  - keyboard now detects disabled entries and doesn't start editing them when clicked
- `el.datastore.SavableModel`
  - added ClassVar `model_dump_default_options` to  to specify default options used for saving files (like indentation).
- `el.widgets.ctkex.CTkEntryEx`
  - `select_all()` and Ctrl+A selection by default
- `el.widgets.ctkex.CTkButtonEx`
  - added `dark_when_disabled` option: Makes button fg the hover_color when it is in disabled state
- `el.widgets.listbox.CTkListBox`:
  - added methods `select_single_by_index`, `select_single_by_id`, `deselect_all`


## New Features

- added `el.base` module
  - `filter_kwargs` helper to only pass non-None kwargs on another function
- added `el.widgets.ctkex.CTkTextBoxEx`
  - touchscreen mode
  - `select_all()` and Ctrl+A selection by default
  - ability to exclude corners from radius
  - ability to change background corner colors
  - ability to control width/height rounding
