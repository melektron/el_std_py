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
  - keymap can define hover color
  - keymap (and overlays) can enable/disable keys
- `el.datastore.SavableModel`
  - added ClassVar `model_dump_default_options` to  to specify default options used for saving files (like indentation).
  - added flags `create_if_missing` and `backup_on_error` to `model_load_from_disk` method
- `el.widgets.ctkex`
  - ctkex widgets requiring cursor manipulation for touchscreen mode have been improved to reduce flickering caused by cursor changes (for some reason) by not performing redundant cursor changes.
- `el.widgets.ctkex.CTkEntryEx`
  - `select_all()` and Ctrl+A selection by default
- `el.widgets.ctkex.CTkButtonEx`
  - added `dark_when_disabled` option: Makes button fg the hover_color when it is in disabled state
  - added `wraplength` option from Tkinter labels for the button text
- `el.widgets.ctkex.CTkScrollableFrameEx`
  - added touchscreen mode
- `el.widgets.listbox.CTkListBox`:
  - added methods `select_single_by_index`, `select_single_by_id`, `deselect_all`
  - added touchscreen mode
- `el.widgets.spinbox.SpinBox`
  - removed `command` parameter as it is redundant and the spinbox should be observed instead
  - added `on_increment` and `on_decrement` callback managers to detect changes initiated by buttons
  - added `reformat_on_increment`, `reformat_on_decrement`, `reformat_on_change` and `reformat_on_edit` parameters to more closely control when the entry value is reformatted. This mitigates issues of the value being reformatted while typing, causing problems.
- `el.observable.Observable` and `el.observable.ComposedObservable`
  - `force_notify()` now propagates force updates recursively to all descendant observables, composed observables and observers, mitigating issues where forcing an update after value mutation (e.g. appending to a list) only propagated to the first layer (direct observers). This was achieved by adding the `force_recursive` kwarg throughout the entire value update call path, optionally including observer functions.
  - When registering or unregistering observers to an Observable in it's own callback, the resulting exception is now enhanced with more helpful information
- `el.ctk_utils`
  - Added `flag_to_state` function to convert boolean enable flag to state string in non-dynamic settings
  - Added some more `types` to support new CTkEx widgets

## New Features

- added `el.base` module
  - `filter_kwargs` helper to only pass non-None kwargs on another function
  - `filter_string` helper to remove characters from string
- added `el.widgets.ctkex.CTkTextBoxEx`
  - touchscreen mode (including CTkScrollbarEx)
  - `select_all()` and Ctrl+A selection by default
  - ability to exclude corners from radius
  - ability to change background corner colors
  - ability to control width/height rounding
- `el.widgets.ctkex.CTkScrollbarEx`
  - touchscreen mode support
- `el.numbers`
  - added `clamp` function to clamp value between a minimum and maximum
- `el.ctk_utils`
  - added `apply_enabled` function to more easily set widget "state" from boolean value
  - added `invert_apm` function to invert the appearance mode (i.e. swap light/dark colors)
- `el.errors`
  - added `DuplicateError`: Indicates that an operation couldn't be completed because of a duplicate object/entry
- `el.async_tools`
  - added `call_soon`: shortcut to "asyncio.get_event_loop().call_soon"
- `el.path_utils`
  - added `abspath`: shortcut for using os.path.abspath with pathlib paths