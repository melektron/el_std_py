"""
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
02.09.23, 23:34

Decorator to create "specialized" datastore
file classes directly from pydantic data models.
"""

import typing
import pydantic
import logging

from ._file import File

_log = logging.getLogger(__name__)

OT = typing.TypeVar("OT", bound=pydantic.BaseModel) # outer type
IT = typing.TypeVar("IT", bound=pydantic.BaseModel) # inner type


# Dummy class used for type-checking that has function signatures
# and doc comments of the specialized file class for type hints.
# This basically tells the type checker that when this object is instantiated it
# actually creates an object of type OT despite takeing different initializer
# arguments.
class SpecializedFile(pydantic.BaseModel, typing.Generic[OT]):
    # Init method to get the correct type-hints and description when instantiating
    def __init__(self, path: list[str] = None) -> None:
        """
        Datastore file class that is specialized to a specific model data type.
        This class inherits from and is functionally equivalent to the File class except that it
        doesn't take a model parameter during instantiation. Additionally, a base path specified
        at definition may be prepended to the path during instantiation.
        """
        ...
    
    # New method to get the correct class type after instantiation which is the actual
    # data model type
    def __new__(cls, path: list[str] = None) -> OT:
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
    base_path: list[str],
) -> typing.Callable[[type[IT]], type[SpecializedFile[IT]]]:
    ...


def specialized_file(
    model_type: type[OT] = None, *, base_path: list[str] = None
) -> typing.Union[
    type[SpecializedFile[OT]], typing.Callable[[type[IT]], type[SpecializedFile[IT]]]
]:
    """
    A class decorator to create "specialized" datastore file classes directly from pydantic
    data models:

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

            def __init__(self, path: list[str] = None) -> None:
                # If the path is not provided, use just the base path
                if path is None: path = []
                # Add the base path if it is given
                if base_path is not None:
                    path = base_path + path
                
                # construct the actual file object
                self.__actual_file__ = File(path, model_type_inner)
            
            def __getattr__(self, __name: str) -> typing.Any:
                # When __actual_file__ has not been defined jet, make it become
                # None for __setattr__
                if __name == "__actual_file__":
                    return None
                # For all other cases, just forward the call to the file content
                return getattr(self.__actual_file__.content, __name)

            def __setattr__(self, __name: str, __value: typing.Any) -> None:
                # When __actual_file__ is first initialized in __init__ (before it exists),
                # it will be None because __getattr__ sets it to that. For this first time, we
                # pass the setattr call to the regular object setattr.
                if self.__actual_file__ is None:
                    return super().__setattr__(__name, __value)
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
