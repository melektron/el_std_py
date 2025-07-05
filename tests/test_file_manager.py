"""
ELEKTRON © 2025 - now
Written by melektron
www.elektron.work
06.07.25, 01:01
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

tests for el.file_manager
"""


import pytest

from el.file_manager import *


def test_transparent_wrapping():
    """
    This checks if the decorator properly wraps the file class
    in a transparent manner (see https://stackoverflow.com/a/65470430)
    """
    class TestFileManager(FileManager):
        ...

    @TestFileManager.register_version(1, 2)
    class TestFile(FileMetadata):
        """some doc comment"""
        username: str
        age: int

    assert TestFile.__name__ == "TestFile"
    assert TestFile.__doc__ == "some doc comment"
    assert hasattr(TestFile, "__wrapped__")


def test_register_fv():
    class TestFileManager(FileManager):
        ...

    @TestFileManager.register_version(1, 2)
    class TestFileV1(FileMetadata):
        """test hii???"""
        username: str
        age: int

    TestFileV1()

    #class WrappedFileHi(TestFileV1):
    #    format_version: tuple[int, int] = (1, 2)

    #WrappedFileHi()
    
    @TestFileManager.register_version(3, 4)
    class TestFileV2(FileMetadata):
        name: str
        oldness: int

    
    assert TestFileManager.format_versions == {1: {0: TestFileV1}}, "Proper registration"


