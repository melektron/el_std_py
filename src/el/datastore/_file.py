"""
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
31.08.23, 21:44
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Class representing a data store "file" instance which can contain multiple
cells. 
"""

import pathlib
import shutil
import logging
import typing
import weakref

from el.timers import IntervalTimer
from ._deps import *

_log = logging.getLogger(__name__)

STORAGE_ENCODING = "UTF8"
STORAGE_CONFIG = {"indent": 4}

# Model Type can be any pydantic data model
MT = typing.TypeVar("MT", bound=pydantic.BaseModel)

_global_datastore_root = pathlib.Path("data")
def set_datastore_root(path: pathlib.Path) -> None:
    """
    Configures the root filesystem path that datastore objects paths
    are relative to. This should be the folder in which datastore objects
    should be saved.
    """
    global _global_datastore_root
    _global_datastore_root = path


class File(typing.Generic[MT]):
    # Dict of all currently accessed files. If multiple file instances with the same path are created,
    # they should all point to the same instance ensuring that the "instances" are "synced" live.
    __all_files__: dict[str, "File"] = weakref.WeakValueDictionary()

    def __new__(cls, path: DSPath, model: type[MT], extension: str = "json", *args, **kwargs):
        """
        Creates a new instance of a File if it is is necessary or returns
        a reference to an existing File instance if one pointing to the same path
        already exists. If the new model type does not match the model type of the
        existing file a type error is raised.
        """

        strpath = str(path) + extension

        # check for existing files
        file = cls.__all_files__.get(strpath)

        # no existing file, create a new one
        if file is None:
            file = super().__new__(cls)
            cls.__all_files__[str(strpath)] = file  # add to weak dict
            return file

        # file exists, check for same model
        if file._model_type is not model:
            raise TypeError(
                f"Same Datastore Files cannot have different data models. Existing file has model {file._model_type}, cannot create instance with same path but model {model}"
            )

        # add flag to tell __init__ that no re-initialization is needed
        file.__file_already_initialized__ = True
        return file

    def __init__(self, 
        path: DSPath, 
        model: type[MT], 
        extension: str = "json",
        autosave: bool = True,
        autosave_interval: float = 5,
    ) -> None:
        """
        Creates a datastore file object from a datastore path.
        This path may be interpreted as a file path to determine the
        storage location of the operating system file containing the
        datastore "file" data.

        Parameters
        ----------
        path : DSPath
            The location or identification to store the file data under.
            This consists of one or more string values that define a hierarchical location
            for sorting like a file system path, although it is not guaranteed for these to
            determine the actual file system path that the file is stored in. Also, the typical
            limitations associated with filesystem paths such as no slashes do not exist here.
            Any string can be used and the implementation will make sure to encode it an a valid way.
        model : type[MT]
            The pydantic Model type describing the structure of the file content.
        extension : str, optional
            the file extension to use for the actual file saved on a storage backend
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

        # if creating reference instance to existing instance we don't need to
        # initialize again (set in __new__)
        if hasattr(self, "__file_already_initialized__"):
            _log.debug("(same file, no re-init)")
            return

        self._path = path
        self._model_type = model
        self._extension = extension
        self._autosave = autosave
        self._autosave_interval = autosave_interval

        # the actual data object reference holding the content
        self._data_content: MT = None
        # copy of above used for comparing to find changes
        self._data_content_copy: MT = None
        # flag set whenever the data content is accessed to note that it might have been changed
        self._data_may_have_changed: bool = False

        if not len(self._path):
            raise ValueError("Datastore path must not be empty.")

        # convert path to the actual location the file is stored in
        self._storage_path = self._get_storage_location_from_path(self._path, self._extension)
        _log.debug(f"Initializing datastore file stored in: {self._storage_path}")

        # create all the directories leading up to the file if not existing already
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

        # If the specified storage path exists but is a directory, that isn't valid
        if self._storage_path.is_dir():
            raise RuntimeError(
                "Datastore storage path is not allowed to point to an existing directory"
            )

        # If the file doesn't exist jet we create it for the first time and populate it with default data
        elif not self._storage_path.exists():
            self._create_default_file()

        # If the file does exist, we open it and try to load the previous values from it
        else:
            try:
                with self._storage_path.open("r", encoding=STORAGE_ENCODING) as f:
                    self._data_content = self._model_type.model_validate_json(f.read())

            except pydantic.ValidationError:
                _log.error(f"Could not load datastore file from {self._storage_path}")
                _log.info(
                    "The faulty file will be backed up and replaced with the default data"
                )

                # back up the corrupt data
                shutil.copy(
                    self._storage_path, self._storage_path.with_suffix(".json.invalid")
                )
                # create new default data and store it
                self._create_default_file()

        # create a copy of data content for comparison
        self._data_content_copy = self._data_content.model_copy(deep=True)

        _log.debug(
            f"Successfully loaded datastore file {self._path} with data: {self._data_content}"
        )

        # setup save timer to periodically check for changes
        self._save_timer = IntervalTimer(self._autosave_interval)
        self._save_timer.on_interval(self._save_timer_cb, weakref.ref(self))
        if self._autosave is not None:
            self._save_timer.start()

    @property
    def content(self):
        """
        property to access the data content object (_data_content should
        never be accessed directly). This will prevent it from being re-assigned.

        Note: Don't save a reference to the returned object, as accessing the
        data via such a reference will circumvent change detection and will cause
        the data to not be saved. 
        """

        # Set flag whenever data is accessed to prevent unnecessary compares
        # when data was never even accessed
        self._data_may_have_changed = True
        return self._data_content

    @staticmethod
    def _sanitize_path_char(char: str) -> str:
        """
        Sanitizes a SINGLE CHARACTER of a path element and converts
        it to an allowed format if it is not allowed.
        """

        if len(char) != 1:
            raise ValueError("Only a single character is allowed")

        # allow certain characters
        if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.":
            return char

        # encode others as hex
        return f"{ord(char):x}"

    @staticmethod
    def _sanitize_path_element(element: str) -> str:
        """
        Sanitizes any string to be one valid path element
        e.g. one folder name or file name. This does NOT sanitize
        an entire path. If the provided string contains e.g. a slash (/)
        it will be converted in a way that it doesn't count as a path separator
        anymore.
        """

        # sanitize individual characters
        element = "".join(map(__class__._sanitize_path_char, element))

        # protect against special dot usage
        if element == ".." or element == ".":
            element = "_" + element

        return element

    @classmethod
    def _get_storage_location_from_path(cls, path: DSPath, extension: str) -> pathlib.Path:
        """
        convert the logical path into an actual storage location. ATM the files
        are stored as regular filesystem files and the path mostly specifies the
        filesystem path relative to the data directory.
        """

        # Add a dot extension to the last path element so extension-replacement doesn't modify
        # the path if it contains dots
        path = path.copy()
        path[-1] += ".ext"

        storage_path = _global_datastore_root
        for el in path:
            storage_path = storage_path / cls._sanitize_path_element(el)
        return storage_path.with_suffix(f".{extension}")

    def _create_default_file(self):
        """
        Initializes (and overwrites) the file system file where the datastore file is stored
        with the default data for the data model.
        """
        self._data_content = self._model_type()  # default init
        self._dump_to_disk()

    def _dump_to_disk(self):
        """
        Opens _storage_path in w mode and writes the current data content to it.
        (no error checking, just for internal use)
        """
        with self._storage_path.open("w", encoding=STORAGE_ENCODING) as f:
            f.write(self._data_content.model_dump_json(**STORAGE_CONFIG))

    def save_to_disk(self):
        """
        writes the current data of the file to disk so it is permanently
        stored. This can be called explicitly, however it is not necessary
        most of the time as saving happens automatically in the background.
        """
        if self._storage_path is None:
            raise RuntimeError("Tried to save datastore file with uninitialized storage location")

        self._data_may_have_changed = False
        self._data_content_copy = self._data_content.model_copy(deep=True)
        self._dump_to_disk()

        _log.debug(f"Saved datastore file {self._path}")
    
    def set_autosave(self, enabled: bool) -> None:
        """
        enable or disable autosave
        """
        self._autosave = enabled
        if enabled:
            self._save_timer.start()
        else:
            self._save_timer.stop()

    @staticmethod
    async def _save_timer_cb(weak_self: weakref.ReferenceType["File"]):
        """
        Called periodically by save timer to check for any
        changes that may need to be saved. 
        (Self is passed as a weak ref to prevent a circular 
        reference that isn't detected by cpython)
        """

        self = weak_self()
        if self is None:    # instance may have been gc-ed already
            return
        
        # If data wasn't ever accessed, don't even bother checking for changes
        if not self._data_may_have_changed:
            _log.debug(f"(Datastore File {self._path} wasn't accessed since last save)")
            return
        
        # If data was accessed, check for changes and don't save if there are no changes
        if self._data_content == self._data_content_copy:
            _log.debug(f"(Datastore File {self._path} has not changed since last save)")
            # Reset the may have changed flag as there are definitely no changes
            self._data_may_have_changed = False
            return
        
        # Otherwise attempt to save the file (this will also reset the above checks)
        self.save_to_disk()

    def __del__(self):
        """
        before deletion save the datastore
        """
        if self._autosave_interval is not None:
            self._save_timer.stop()
        self.save_to_disk()
