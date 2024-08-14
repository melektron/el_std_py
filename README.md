# el-std-py

el-std-py is an assortment of useful python utilities complementing some builtin and third party python packages.


## Disclaimer

1. I mainly develop this library for my own use use, and while I do thing that it might be useful to others, there is no guarantee that features work as expected and I may introduce breaking changes to APIs at any time.
2. While the ```el-std-py``` is namely related to my [```el-std-cpp```](https://github.com/melektron/el_std_cpp) library, the two are not related in any way content-wise and there is no promise of feature parity whatsoever. Both libraries are simply utility libraries for the respective languages with features I commonly use in them. They are otherwise independent.


## Versions

I am currently targeting Python 3.12 for this library. Although some things might work in earlier versions, there is no guarantee, and I will not refrain from using the latest python features.


## Features and Documentation

While I might write more comprehensive documentation for some features along the way, I will at least try to maintain an up-to-date list of all available features:

(when reading from PyPi, some links might not work. [View on GitHub](https://github.com/melektron/el_std_py#features-and-documentation) for full documentation)

- ```el.async_tools```: Utility functions for working with ```asyncio```
- ```el.errors```: More exception types for general errors I have encountered to need often. Some of them are used by el.
- ```el.terminal```: Terminal controller enabling an asynchronous command interface and a color-coded logging configuration that is a good stating point and pushes logs to stdout without disturbing the user command line.
- ```el.timers```: Async timer classes such as IntervalTimer and WDTimer for use with ```asyncio```
- ```el.typing_tools```: Utility functions for working with ```typing```
- ```el.observable```: Data wrapper classes allowing the observation and chaining of value change events and thus declaratively defining data paths
- ```el.datastore```: Zero-setup Data and configuration file handler that uses pydantic do define data models and ```asyncio``` to automatically store/load them to/from disc in the background without having to touch filepaths or files.
- [```el.bindantic```](docs/bindantic.md): An unofficial "extension" (one could call it a "mod") for [pydantic](https://pydantic.dev/) that adds support for defining, dumping and validating binary data structures (like in C), while maintaining all pydantic features.


## Contribution

Despite all these disclaimers, if you have utilities, changes, fixes, etc. that you think might be nice to include here, feel free to create issues/PRs.

