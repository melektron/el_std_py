"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 21:58
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Helper base class to simplify representing files as models and loading/saving
them from/to disk.
"""

import typing
import functools
from pathlib import Path

from ._deps import *


class ModelDumpJsonOptions(typing.TypedDict):
    indent: int | None = None,
    include: pydantic.main.IncEx | None = None,
    exclude: pydantic.main.IncEx | None = None,
    context: typing.Any | None = None,
    by_alias: bool = False,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    round_trip: bool = False,
    warnings: bool | typing.Literal['none', 'warn', 'error'] = True,
    serialize_as_any: bool = False,


class SavableModel(pydantic.BaseModel):
    """
    Model base class that adds functions to easily load models from
    files on disk and save them to files on disk.
    """

    @typing.override
    def model_post_init(self, __context):
        # cache the path of the instance on disk
        self._model_file_path: Path | None = None
        return super().model_post_init(__context)
    
    @property
    def model_file_path(self):
        return self._model_file_path
    
    @model_file_path.setter
    def model_file_path(self, v: Path | None):
        self._model_file_path = v

    @classmethod
    def model_load_from_disk(cls, filepath: Path) -> typing.Self:
        """
        Creates a model instance from the file on disk 
        specified in the "filepath" parameter.

        Raises:
            FileExistsError if the provided file doesn't exist
            ValueError if the provided file cannot be parsed

        Parameters
        ----------
        filepath : Path
            The path on disk to load the model from.
            This is saved in the returned model instance.

        Returns
        -------
        typing.Self
            A model instance initialized with the validated
            content of the provided file.

        Raises
        ------
        FileExistsError
            File does not exist.
        pydantic.ValidationError
            File structure could not be parsed correctly.
        """

        # check that the file exists and read it
        if not filepath.exists() or not filepath.is_file():
            raise FileExistsError(f"File {filepath} doesn't exist")
        inst = cls.model_validate_json(filepath.read_text())
        inst._model_file_path = filepath  # save the file path we loaded from
        return inst

    def model_save_to_disk(self, **kwargs: typing.Unpack[ModelDumpJsonOptions]) -> bool:
        """
        Saves the model to the file path it was loaded from.
        All kwargs are forwarded to model_dump_json()

        Returns
        -------
        bool
            True if successful
            False if no file path is set, e.g. because the model was not 
            previously loaded or saved (need to use save_to_disk_as() instead).

        Raises
        ------
        any errors from writing
        """

        if self._model_file_path is None:
            return False
        # create directory if not already present
        self._model_file_path.parent.mkdir(parents=True, exist_ok=True)

        # attempt to write to file
        self._model_file_path.write_text(self.model_dump_json(**kwargs))

        return True
    
    def model_save_to_disk_as(self, new_file_path: Path, **kwargs: typing.Unpack[ModelDumpJsonOptions]):
        """
        Saves the model to the provided file path. If successful, the
        file path is stored as the new location of the model instance.
        All kwargs are forwarded to model_dump_json()

        Raises
        ------
        any errors from writing
        """

        # create directory if not already present
        new_file_path.parent.mkdir(parents=True, exist_ok=True)
        # attempt to write to file
        new_file_path.write_text(self.model_dump_json(**kwargs))
        # if successful, save the path
        self._model_file_path = new_file_path
    
    def model_delete_from_disk(self, new_file_path: Path, **kwargs: typing.Unpack[ModelDumpJsonOptions]):
        """
        Deletes the current model file on disk and clears
        the internal model file path.
        If the file already does not exist, nothing happens

        Raises
        ------
        any errors from writing
        """
        if self._model_file_path is not None and self._model_file_path.is_file():
            self._model_file_path.unlink(missing_ok=True)



