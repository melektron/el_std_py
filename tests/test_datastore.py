"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 01:01
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

tests for el.datastore
"""


import abc
import pytest
import typing
import logging
import pydantic
import pydantic_core

from el.datastore import *
from el.datastore import VersionedModel


_log = logging.getLogger(__name__)


async def test_file_value_passing():
    """
    This checks that the specialized_file properly sets default file
    arguments and passes base path.
    This also checks that the values passed to specialized_file decorator
    are properly captured internally and are not affected by
    subsequent calls.
    """

    @specialized_file(base_path=["tf1base"], extension="txt")
    class TestFile1(pydantic.BaseModel):
        username: str = "Bob"
        age: int = 20

    @specialized_file(base_path=["tf2base"], autosave_interval=4)
    class TestFile2(pydantic.BaseModel):
        name: str = "Alice"
        hight: int = 180

    f1 = TestFile1()
    f2 = TestFile2()
    f3 = TestFile2(path = ["sub"], extension="cfg", autosave=False)
    
    assert f1.__actual_file__._path == ["tf1base"]
    assert f1.__actual_file__._extension == "txt"
    assert f1.__actual_file__._autosave_interval == 5
    assert f2.__actual_file__._path == ["tf2base"]
    assert f2.__actual_file__._extension == "json"
    assert f2.__actual_file__._autosave_interval == 4
    assert f3.__actual_file__._path == ["tf2base", "sub"]
    assert f3.__actual_file__._extension == "cfg"
    assert f3.__actual_file__._autosave == False
    assert f3.__actual_file__._autosave_interval == 4


async def test_attribute_delegation():
    """
    This checks that attribute access is directly delegated to the
    public API of File if available and the content Model otherwise.
    """

    @specialized_file(base_path=["tf"])
    class TestFile(pydantic.BaseModel):
        username: str = "Bob"
        age: int = 20

    f = TestFile()
    f.save_to_disk()
    f.set_autosave(True)
    assert f.content.username == f.username
    assert f.username == "Bob"
    assert f.age == 20
    #f.model_fields["aasdf"].default

    
async def test_version_migration():
    
    class MyModelV1(VersionedModel):
        format_version: int = 1
        username: str
        age: int

    class MyModelV2(VersionedModel):
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
    
    class MyModelV3(VersionedModel):
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

    m3 = MyModelV3(format_version=1, username="Bob", age=20)
    assert m3.format_version == 3
    assert m3.first_name == "Bob"
    assert m3.years_alive == 20

    # gest migration from an older instance
    m1 = MyModelV1(username="Alice", age=25)
    m3 = MyModelV3.model_validate(m1)
    assert m3.format_version == 3
    assert m3.first_name == "Alice"
    assert m3.years_alive == 25
    