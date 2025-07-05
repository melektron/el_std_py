"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
05.07.25, 19:56
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Framework for managing multiple versions of custom json-based file-formats
including lifecycle and migrations using pydantic-
"""

import typing
import functools

from el.errors import SetupError

try:
    import pydantic
except ImportError:
    raise SetupError("el.file_manager requires pydantic. Please install it before using el.file_manager.")


class FileMetadata(pydantic.BaseModel):
    """
    Base class of the file structure model that includes the minimal fields 
    required for management using file_manager.

    Example Use:

    ```python
    class MyFile(FileMetadata):
        format_version = (2, 5)

        my_content1: str
        my_content2: int
    ```

    You must specify the format version in the 
    """
    # extra options are ignored by default so small changes like removing fields
    # or adding fields with default values do not count as a new version and don't 
    # need a migration
    model_config = {"extra": "ignore"}

    # version numbers (major, minor) to identify files before migration.
    # major version changes are incompatible with each other while minor
    # versions are compatible to some extent, but allow the developer to specify
    # some code to modify the file in-place when opening if necessary
    format_version: tuple[int, int]



OT = typing.TypeVar("OT", bound=pydantic.BaseModel) # outer type
IT = typing.TypeVar("IT", bound=pydantic.BaseModel) # inner type


# Dummy class used for type-checking that has function signatures
# and doc comments of the specialized file class for type hints.
# This basically tells the type checker that when this object is instantiated it
# actually creates an object of type OT despite takeing different initializer
# arguments.
class WrappedFile(pydantic.BaseModel, typing.Generic[OT]):
    # Init method to get the correct type-hints and description when instantiating
    #def __init__(self, path: list[str] = None) -> None:
    #    """
    #    Datastore file class that is specialized to a specific model data type.
    #    This class inherits from and is functionally equivalent to the File class except that it
    #    doesn't take a model parameter during instantiation. Additionally, a base path specified
    #    at definition may be prepended to the path during instantiation.
    #    """
    #    ...
    
    # New method to get the correct class type after instantiation which is the actual
    # data model type
    def __new__(cls, path: list[str] = None) -> OT:
        ...



class FileManager:
    # map storing all the format versions managed by this manager.
    # this is to be populated either manually or using the decorator
    format_versions: dict[int, dict[int, FileMetadata]] = {}

    @classmethod
    def register_version(cls, major: int, minor: int) -> typing.Callable[[type[IT]], type[WrappedFile[IT]]]: 
        """
        registers the decorated class as the specified
        file format format version and adds that version to 
        as the default value in the file format.
        """

        def decorator[T](wrapped: T):

            # create subclass with version added as default
            #@functools.wraps(wrapped, updated=())   # https://stackoverflow.com/a/65470430
            class WrappedFile(wrapped):
                format_version: tuple[int, int] = (major, minor)
            
            # save it for migration purposes
            if major not in cls.format_versions:
                cls.format_versions[major] = {}
            cls.format_versions[major][minor] = WrappedFile
            
            return WrappedFile
        
        return decorator

    def __init__(self):
        pass