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


import pytest
import pydantic

from el.datastore import *


async def test_closure_value_capturing():
    """
    This checks that the values passed to specialized_file decorator
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
    
    assert f1.__actual_file__._path == ["tf1base"]
    assert f1.__actual_file__._extension == "txt"
    assert f1.__actual_file__._autosave_interval == 5
    assert f2.__actual_file__._path == ["tf2base"]
    assert f2.__actual_file__._extension == "json"
    assert f2.__actual_file__._autosave_interval == 4


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

    
