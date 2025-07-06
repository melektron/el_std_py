"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 12:37
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Support for versioning and assisted migration of datastore file data models
"""

import typing

from ._deps import *

# dummy type to identify when migrate() is not overridden and the migration
# chain is therefore interrupted
type OriginFormatVersion = None


class VersionedModel(pydantic.BaseModel):
    """
    Extension of pydantic.BaseModel that includes functionality to easily define
    migrators to migrate the model from earlier versions of the format 
    while validating. This is useful in combination with ```el.datastore.specialized_file```
    to automatically migrate old file formats to new ones upon opening.

    To use this, inherit your model from ```VersionedBaseModel``` instead of ```pydantic.BaseModel```.
    This adds a "format_version" field. In each version of the model, change the default value
    of that field to identify the version:

    ```python
    class MyModelV1(VersionedBaseModel):
        format_version: int = 1
        username: str
        age: int

    class MyModelV2(VersionedBaseModel):
        format_version: int = 2
        name: str
        oldness: int
    
    class MyModelV3(pydantic.BaseModel):
        format_version: int = 3
        first_name: str
        years_alive: int
    ```

    Now to connect the model versions together, add a migrator to each model that migrates
    from the previous version to it's own:


    ```python
    class MyModelV1(VersionedBaseModel):
        format_version: int = 1
        username: str
        age: int

    class MyModelV2(VersionedBaseModel):
        format_version: int = 2
        name: str
        oldness: int

        @typing.override
        @classmethod
        def migrate(cls, old: MyModelV1) -> typing.Self:
            return MyModelV2(
                name=old.username,
                oldness=old.age,
            )
    
    class MyModelV3(pydantic.BaseModel):
        format_version: int = 3
        first_name: str
        years_alive: int

        @typing.override
        @classmethod
        def migrate(cls, old: MyModelV2) -> typing.Self:
            return MyModelV3(
                first_name=old.name,
                years_alive=old.oldness,
            )
    ```

    The migrator method MUST take an argument called "old" that is annotated with the previous
    version type, as that annotation is how ```VersionedBaseModel``` identifies the migration chain.

    Now, you can use MyModelV3 in your code, however whenever it is called with 
    data indicating a previous version, the chain of migrators is called to automatically migrate
    to the desired newer version:

    ```python
    m = MyModelV3(format_version=1, username="Bob", age=20)
    assert m.format_version == 3
    assert m.first_name == "Bob"
    assert m.years_alive == 20
    ```

    The first version obviously does not need a migrator specified. It marks the start of the version
    chain. If any model in the middle of the chain is missing a migrator this breaks the chain of migration.
    Version numbers don't need to be sequential, as the order of versions is identified by their links.
    It is however advised to number the versions in order.
    """
    
    format_version: int

    @pydantic.model_validator(mode='before')
    @classmethod
    def check_for_migration(cls, data: typing.Any) -> typing.Any:
        # get the format version we want to have
        target_fv = cls.model_fields["format_version"].default
        # see what format version we are parsing
        input_fv: int = ...
        if isinstance(data, dict):  # in case of dict parsing, json parsing or direct initialization
            # if the format version is explicitly passed (e.g. when loading from JSON file)
            # we use that value. otherwise (likely when doing direct instantiation where we use the default value)
            # we use that default, effectively disabling migration.
            if "format_version" in data:
                input_fv = data["format_version"]
            else:
                input_fv = target_fv
        elif isinstance(data, pydantic.BaseModel):  # in case of parsing from another model
            # same thing as above
            if hasattr(data, "format_version"):
                input_fv = getattr(data, "format_version")
            else:
                input_fv = target_fv
        else:
            raise ValueError("Input to versioned model validation is not supported")
        # make sure the value is still an integer
        assert isinstance(input_fv, int), f"format_version must be an integer but is of type {type(input_fv)}"
        
        # if we have the right version, proceed with normal validation (no migration needed)
        if input_fv == target_fv:
            return data

        # make sure a migrator is properly defined if there is one
        if "old" not in cls.migrate.__annotations__:
            raise pydantic_core.PydanticCustomError(
                "migration_error",
                f"""
                Migrator for versioned model {cls.__qualname__} has an invalid function signature or missing annotation.
                The migrator must take one argument called "old" that is annotated with the model of the previous format version. 
                """
            )
        # make sure a migrator is defined (if the signature of VersionedBaseModel.migrator is detected
        # no migrator was defined)
        if cls.migrate.__annotations__["old"] is OriginFormatVersion:
            raise pydantic_core.PydanticCustomError(
                "migration_error",
                f"""
                Version migration for versioned model {cls.__qualname__} failed: migrator chain interrupted.
                Migrator from format version {input_fv} to {target_fv} is missing or version {input_fv} is invalid.
                """
            )
        # extract the previous version model and use it to parse the value.
        # if it is still not the right version, it will call it's predecessor until 
        # we have either reached the correct version or the migrator chain is interrupted
        previous_version_model: type[pydantic.BaseModel] = cls.migrate.__annotations__["old"]
        return cls.migrate(previous_version_model.model_validate(data)).model_dump()
    
    @classmethod
    def migrate(cls, old: OriginFormatVersion) -> typing.Self:
        """
        default that must be overridden by children to support migration last version
        """
