# el-std-py

el-std-py is an assortment of useful python utilities complementing some builtin and third party python packages.


## Disclaimer

1. I mainly develop this library for my own use use, and while I do think that it might be useful to others, there is no guarantee that features work as expected and I may introduce breaking changes to APIs at any time.
2. While the `el-std-py` is namely related to my [`el-std-cpp`](https://github.com/melektron/el_std_cpp) library, the two are not related in any way content-wise and there is no promise of feature parity whatsoever. Both libraries are simply utility libraries for the respective languages with features I commonly use in them. They are otherwise independent.


## Versions

I am currently targeting Python 3.13 for this library. Although some things might work in earlier versions, there is no guarantee, and I will not refrain from using the latest python features.


## Features and Documentation

While I might write more comprehensive documentation for some features along the way, I will at least try to maintain an up-to-date list of all available features:

(when reading from PyPi, some links might not work. [View on GitHub](https://github.com/melektron/el_std_py#features-and-documentation) for full documentation)

### General program logic

- `el.async_tools`: Utility functions for working with `asyncio`
- `el.terminal`: Terminal controller enabling an asynchronous command interface and a color-coded logging configuration that is a good stating point and pushes logs to stdout without disturbing the user command line.
- `el.observable`: Data wrapper classes allowing the observation and chaining of value change events and thus declaratively defining data paths
- [`el.bindantic`](docs/bindantic.md): An unofficial "extension" (one could call it a "mod") for [pydantic](https://docs.pydantic.dev/latest/) that adds support for defining, dumping and validating binary data structures (like in C), while maintaining all pydantic features.
- `el.callback_manager`: Simple callback registry class for exposing events
- `el.lifetime`: Contextual lifetime management for registries (Any object that requires to register something, like a `CallbackManager` or `Observable`)
- `el.datastore`: Zero-setup database-like data and configuration file handler that uses pydantic do define data models and `asyncio` to automatically store/load them to/from disc in the background without having to touch filepaths or files.
- `el.timers`: Async timer classes such as IntervalTimer and WDTimer for use with `asyncio`
- `el.time_utils`: Utilities for working with dates and times
- `el.errors`: More exception types for general errors I have encountered to need often. Some of them are used by el.
- `el.typing_tools`: Utility functions for working with `typing`
- `el.numbers`: Mathematical utilities for working with numbers, such as linear mapping.
- `el.containers`: Utilities for working with container objects

### UI

- `el.ctk_utils`: Utility functions and classes for working with `customtkinter`
- `el.widgets`: Additional `customtkinter` widgets
- `el.tkml`: Tkinter Markup Language: A more user-friendly way to define hierarchical UI with Tk/CTk widgets
- `el.mpl_utils`: Utilities for working with `matplotlib`
- `el.assets`: UI assest manager and some built-in assets

### Debugging/Development

- `el.analysis`: Utilities for analyzing code performance
- `el.nixos_ctk_font_fix`: Module to work around issues when using CTk on NixOS (not intended for production)

### Experimental
These might not be fully implemented (yet).

- `el.history_manager` (experimental): Utility to manage history of pydantic model instances for implementing Undo/Redo functionality


## Contribution

Despite all these disclaimers, if you have utilities, changes, fixes, etc. that you think might be nice to include here, feel free to create issues/PRs.

## 3rd party components and attribution

This library contains some third-party components requiring attribution, mainly assets for UI widgets.
These components are exempt from the terms of [LICENSE](LICENSE) and instead fall under the terms
of their respective licenses as provided by their authors.

Assets/Icons: 
- <a href="https://www.flaticon.com/free-icons/cross" title="cross icons">Cross icons created by Catalin Fertu - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/backspace" title="backspace icons">Backspace icons created by Abdul-Aziz - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/enter" title="enter icons">Enter icons created by Md Tanvirul Haque - Flaticon</a>