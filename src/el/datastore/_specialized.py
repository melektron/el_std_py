"""
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
02.09.23, 23:34
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 


Decorator to create "specialized" datastore
file classes directly from pydantic data models.
"""

import typing
import pydantic
import logging

from ._deps import *
from ._file import File

_log = logging.getLogger(__name__)

OT = typing.TypeVar("OT", bound=pydantic.BaseModel) # outer type
IT = typing.TypeVar("IT", bound=pydantic.BaseModel) # inner type


# Dummy class used for type-checking that has function signatures
# and doc comments of the specialized file class for type hints.
# This basically tells the type checker that when this object is instantiated it
# actually creates an object of type OT despite takeing different initializer
# arguments.
# For some reason (probably weirdness with the pydantic pylance integration) we need
# to put the doc comment both in the class to have it shown when instantiating
# and also in __init__ to have it shown on hover of the type (like what??? that makes no sense...)
class SpecializedFile(pydantic.BaseModel, typing.Generic[OT]):
    """
    Creates a datastore file object (with the specific type) from a datastore path.
    This path may be interpreted as a file path to determine the
    storage location of the operating system file containing the
    datastore "file" data.

    Parameters
    ----------
    All noted defaults assume they are not overridden using
    the specialized_file decorator. When parameters are specified
    in the decorator, those will be the default values.

    path : DSPath
        The location or identification to store the file data under.
        This consists of one or more string values that define a hierarchical location
        for sorting like a file system path, although it is not guaranteed for these to
        determine the actual file system path that the file is stored in. Also, the typical
        limitations associated with filesystem paths such as no slashes do not exist here.
        Any string can be used and the implementation will make sure to encode it an a valid way.
        The base_path from the specialized_file is prefixed to this.
    extension : str, optional
        The file extension to use for the actual file saved on a storage backend
        if applicable on that backend. By default "json".
    autosave : bool, optional
        Whether to initially enable autosave, by default True. Autosave can be disabled/enabled
        later on using set_autosave().
    autosave_interval : float, optional
        Interval between autosaves in seconds. By default 5.

    Raises
    ------
    ValueError
        Datastore path is empty.
    RuntimeError
        Datastore path points to an existing directory on the storage backend 
        which can and should not be replaced by a file automatically.
    """
    # Init method to get the correct type-hints and description when instantiating
    def __init__(
        self, 
        path: DSPath = None,
        extension: str = "json",
        autosave: bool = True,
        autosave_interval: float = 5,
    ) -> None:
        """
        Creates a datastore file object (with the specific type) from a datastore path.
        This path may be interpreted as a file path to determine the
        storage location of the operating system file containing the
        datastore "file" data.

        Parameters
        ----------
        All noted defaults assume they are not overridden using
        the specialized_file decorator. When parameters are specified
        in the decorator, those will be the default values.

        path : DSPath
            The location or identification to store the file data under.
            This consists of one or more string values that define a hierarchical location
            for sorting like a file system path, although it is not guaranteed for these to
            determine the actual file system path that the file is stored in. Also, the typical
            limitations associated with filesystem paths such as no slashes do not exist here.
            Any string can be used and the implementation will make sure to encode it an a valid way.
            The base_path from the specialized_file is prefixed to this.
        extension : str, optional
            The file extension to use for the actual file saved on a storage backend
            if applicable on that backend. By default "json".
        autosave : bool, optional
            Whether to initially enable autosave, by default True. Autosave can be disabled/enabled
            later on using set_autosave().
        autosave_interval : float, optional
            Interval between autosaves in seconds. By default 5.

        Raises
        ------
        ValueError
            Datastore path is empty.
        RuntimeError
            Datastore path points to an existing directory on the storage backend 
            which can and should not be replaced by a file automatically.
        """
        ...
    
    # New method to get the correct class type after instantiation which is the actual
    # data model type.
    # The return type is a Union with File, which is sort of a hack to emulate the behavior
    # of a product type using a sum type (union) for intellisense (so you get recommended the attributes
    # of both OT and File). This is however quite a hack and will not play nicely with mypy, so might have
    # to revisit that in the future.
    def __new__(
        cls, 
        # we need to explicitly mention all the parameters here again to get full intellisense when initializing
        path: DSPath = None,
        extension: str = "json",
        autosave: bool = True,
        autosave_interval: float = 5,
    ) -> OT | File:
        ...


# We need @overload decorator to get conditional types working as python doesn't support that directly:
# https://stackoverflow.com/questions/44233913/is-there-a-way-to-specify-a-conditional-type-hint-in-python
# https://mypy.readthedocs.io/en/stable/more_types.html#function-overloading


# decorator used without arguments, target class passed directly type[OT]: #
@typing.overload
def specialized_file(model_type: type[OT]) -> type[SpecializedFile[OT]]:
    ...


# decorator used with arguments, target class not passed and instead the function needs to return the actual decorator
@typing.overload
def specialized_file(
    base_path: DSPath = None, 
    extension: str = "json",
    autosave: bool = True,
    autosave_interval: float = 5,
) -> typing.Callable[[type[IT]], type[SpecializedFile[IT]]]:
    ...


def specialized_file(
    model_type: type[OT] = None, *, 
    base_path: DSPath = None, 
    extension: str = "json",
    autosave: bool = True,
    autosave_interval: float = 5,
) -> typing.Union[
    type[SpecializedFile[OT]], typing.Callable[[type[IT]], type[SpecializedFile[IT]]]
]:
    """
    A class decorator to create "specialized" datastore file classes directly from pydantic
    data models.

    Parameters
    ----------
    All Parameters are optional. When decorating without calling,
    the defaults are used. When providing them, most parameters
    (except base_path) serve as default values for the specialized 
    file class that is emitted.

    base_path : DSPath, optional
        A path prefix prepended to the path passed when instantiating
        the resulting specialized file. This can be used to group all files of a type
        in a certain folder. For single-use files this can also specify the full path, 
        so no path has to be passed at all when instantiating the file.
    extension : str, optional
        The default file extension to use for the actual file saved on a storage backend
        if applicable on that backend. By default "json".
    autosave : bool, optional
        Whether to initially enable autosave, by default True. Autosave can be disabled/enabled
        later on using set_autosave().
    autosave_interval : float | optional
        Default interval between autosaves in seconds. By default 5.

    Returns
    -------
    typing.Union[ type[SpecializedFile[OT]], typing.Callable[[type[IT]], type[SpecializedFile[IT]]] ]
        _description_

    Usage
    -------

    ```python
    @specialized_file
    class UserDataFile(pydantic.BaseModel):
        user_name: str = ""
        join_data: int = 0
        followers: int = 0
    ```

    SpecializedFile classes behave like the decorated model class, except they take the file 
    path as the initialization parameter. Type-Checkers will even believe that it is
    just the regular model after instantiation so all intellisense features will still work!
    
    So you can simply instantiate the above defined model and pass it the file path to store it. 
    After that you can use it like the regular data model but it will automatically save the data to disk:

    ```python
    user_data = UserDataFile(["user123423"])
    user_data.followers = 5
    ```

    Additionally, the specialized file decorator allows specifying a base path. This path will be prepended
    in front of the regular path passed to the file during instantiation:

    ```python
    @specialized_file(base_path=["users"])
    class UserDataFileOrganized(pydantic.BaseModel):
        user_name: str = ""
        join_data: int = 0
        followers: int = 0
    ```

    This is useful because you may want to group all datastore files of the same type together
    so they are more organized. For example, you might want to store every UserDataFile in a folder
    named "users", naming the file by the user name:

    ```python
    user_data_org = UserDataFileOrganized(["user123423"])
    user_data_org.followers = 5

    # Equivalent to the following without base path:
    user_data = UserDataFile(["users", "user123423"])
    user_data.followers = 5
    ```

    The two above variations are functionally equivalent, but with the base
    path you don't need to remember to specify the same base path everywhere a user file
    is accessed, which reduces the risk of bugs.

    By default the files are saved with a .json extension. This can be changed using the
    "extension" parameter:

    ```python
    @specialized_file(base_path=["users"], extension="user")
    class UserDataFileOrganized(pydantic.BaseModel):
        user_name: str = ""
        join_data: int = 0
        followers: int = 0

    # This will create a file called "users/user123423.user"
    user_data_org = UserDataFileOrganized(["user123423"])
    ```
    """

    # The function which actually decorates the class
    def decorator_fn(model_type_inner: type[IT]) -> type[SpecializedFile[IT]]:
        class SpecializedFile:
            """
            A small class containing the file object that simply forwards all
            attribute access to the file content after initialization.
            """

            # This specialized file is only allowed to have the __actual_file__ member:
            __slots__ = ("__actual_file__")

            def __init__(
                self,
                path: DSPath = None,
                extension: str = extension,
                autosave: bool = autosave,
                autosave_interval: float = autosave_interval,
            ) -> None:
                """asdfadsf

                Parameters
                ----------
                path : DSPath, optional
                    _description_, by default None
                """
                # If the path is not provided, use just the base path
                if path is None: path = []
                # Add the base path if it is given
                if base_path is not None:
                    path = base_path + path
                
                # construct the actual file object
                self.__actual_file__ = File(
                    path, 
                    model_type_inner, 
                    extension=extension,
                    autosave=autosave,
                    autosave_interval=autosave_interval,
                )
            
            def __getattr__(self, __name: str) -> typing.Any:
                # When the __actual_file__ slot has not been defined yet, make it become
                # None for __setattr__ (this branch is only true before first assign of 
                # __actual_file__ bc __getattr__ is not called for a slot after it is first assigned)
                if __name == "__actual_file__":
                    return None
                # Pass all public attributes of File to the actual file instance.
                # (this is a hack to sort of create a product type of Field and the file's content)
                if not __name.startswith("_") and hasattr(self.__actual_file__, __name):
                    return getattr(self.__actual_file__, __name)
                # For all other cases, just forward the call to the file content
                return getattr(self.__actual_file__.content, __name)

            def __setattr__(self, __name: str, __value: typing.Any) -> None:
                # When __actual_file__ is first initialized in __init__ (before it exists),
                # it will be None because __getattr__ sets it to that. For this first time, we
                # pass the setattr call to the regular object setattr.
                if self.__actual_file__ is None:
                    return super().__setattr__(__name, __value)
                # Pass all public attributes of File to the actual file instance.
                # (this is a hack to sort of create a product type of Field and the file's content)
                if not __name.startswith("_") and hasattr(self.__actual_file__, __name):
                    return setattr(self.__actual_file__, __name, __value)
                # After that, we just redirect all setattr calls to the file content
                return setattr(self.__actual_file__.content, __name, __value)

        return SpecializedFile

    # If the function is called as a decorator directly with no args,
    # we need to run the decorator function and return the result
    if model_type is not None:
        return decorator_fn(model_type_inner=model_type)

    # If the function is called with arguments, we need to return the decorator
    # function so it can be called outside
    return decorator_fn
