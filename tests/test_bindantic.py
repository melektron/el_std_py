"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
08.08.24, 18:18
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

tests for bindantic
"""

import pytest
import enum
import sys
import pydantic
import annotated_types
from collections import deque
from typing import Annotated, Any, Literal
import typing

from el.bindantic import *


class KnownGoodEnumUnsigned(enum.Enum):
    FIRST = 0
    SECOND = 1
    THIRD = 2
    FOURTH = 3
    FIFTH = 4

class KnownGoodEnumSigned(enum.Enum):
    FIRST = -2
    SECOND = -1
    THIRD = 0
    FOURTH = 1
    FIFTH = 2


## Common testing functions ##

def get_actual_type(tp: Any) -> Any:
    origin = typing.get_origin(tp)
    return origin if origin is not None else tp

def assert_general_field_checks(
    f: BaseField, 
    annotation_type: type,
    hierarchy_field_name: str,
    top_level: bool,
    outlet: bool,
    struct_code: str, 
    element_cons: int, 
    byte_cons: int, 
):
    assert f.type_annotation is f.pydantic_field.annotation
    assert f.annotation_metadata is f.pydantic_field.metadata
    assert get_actual_type(f.type_annotation) is annotation_type
    assert f.hierarchy_location_with_self_string == hierarchy_field_name
    assert f.is_top_level == top_level
    assert f.is_outlet == outlet
    assert f.supported_py_types
    assert f.struct_code == struct_code
    assert f.element_consumption == element_cons
    assert f.bytes_consumption == byte_cons

def assert_validation_error(
    exc_info: pytest.ExceptionInfo[pydantic.ValidationError], 
    type: str, 
    input: Any | None = None, 
    ctx: dict[str, Any] | None = None
):
    e = exc_info.value
    assert e.error_count() == 1
    assert e.errors()[0]["type"] == type
    if input is not None: 
        assert e.errors()[0]["input"] == input
    if ctx is not None:
        assert e.errors()[0]["ctx"] == ctx

def assert_missing_config_error(
    exc_info: pytest.ExceptionInfo[pydantic.ValidationError], 
    item: str, 
):
    e = str(exc_info.value).lower()
    assert "missing required config option" in e
    assert item.lower() in e


## Integer testing

def assert_general_integer_checks(
    f: IntegerField, 
    signed: bool
):
    assert f.signed == signed


def test_intU8():
    class TestStructure(BaseStruct):
        some_field: Uint8 = 578
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False,"B", 1, 1)
    assert_general_integer_checks(f, False)

    # range limits    
    tv = 2**8
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})


def test_intU16():
    class TestStructure(BaseStruct):
        some_field: Uint16
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "H", 1, 2)
    assert_general_integer_checks(f, False)

    # range limits
    tv = 2**16
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})


def test_intU32():
    class TestStructure(BaseStruct):
        some_field: Uint32
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "I", 1, 4)
    assert_general_integer_checks(f, False)

    # range limits
    tv = 2**32
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})
    

def test_intU64():
    class TestStructure(BaseStruct):
        some_field: Uint64
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "Q", 1, 8)
    assert_general_integer_checks(f, False)

    # range limits
    tv = 2**64
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})


def test_int8():
    class TestStructure(BaseStruct):
        some_field: Int8
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "b", 1, 1)
    assert_general_integer_checks(f, True)

    # range limits
    tv = 2**7
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    tv = -2**7 - 1
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "greater_than_equal", tv, {"ge": tv + 1})


def test_int16():
    class TestStructure(BaseStruct):
        some_field: Int16
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "h", 1, 2)
    assert_general_integer_checks(f, True)

    # range limits
    tv = 2**15
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    tv = -2**15 - 1
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "greater_than_equal", tv, {"ge": tv + 1})


def test_int32():
    class TestStructure(BaseStruct):
        some_field: Int32
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "i", 1, 4)
    assert_general_integer_checks(f, True)

    # range limits
    tv = 2**31
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    tv = -2**31 - 1
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "greater_than_equal", tv, {"ge": tv + 1})
    

def test_int64():
    class TestStructure(BaseStruct):
        some_field: Int64
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "q", 1, 8)
    assert_general_integer_checks(f, True)

    # range limits
    tv = 2**63
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    tv = -2**63 - 1
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "greater_than_equal", tv, {"ge": tv + 1})


## Integer literal tests ##

def test_litU8():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: LitU8[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False,"B", 1, 1)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x0D")
    assert_validation_error(exc_info, "literal_error")


def test_litU16():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: LitU16[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "H", 1, 2)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\0\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\x0D")
    assert_validation_error(exc_info, "literal_error")


def test_litU32():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: LitU32[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "I", 1, 4)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\x0D")
    assert_validation_error(exc_info, "literal_error")
    

def test_litU64():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: LitU64[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "Q", 1, 8)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x0D")
    assert_validation_error(exc_info, "literal_error")


def test_lit8():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Lit8[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "b", 1, 1)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x0D")
    assert_validation_error(exc_info, "literal_error")


def test_lit16():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Lit16[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "h", 1, 2)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\0\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\x0D")
    assert_validation_error(exc_info, "literal_error")


def test_lit32():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Lit32[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "i", 1, 4)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\x0D")
    assert_validation_error(exc_info, "literal_error")
    

def test_lit64():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Lit64[Literal[12]] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "q", 1, 8)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=12)
    assert inst.some_field == 12
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x0C")
    assert inst.some_field == 12

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=13)
    assert_validation_error(exc_info, "literal_error", 13)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x0D")
    assert_validation_error(exc_info, "literal_error")


## Enumeration field ##

def assert_enum_out_of_range_error(
    exc_info: pytest.ExceptionInfo[ValueError],
    int_type: Literal["Uint8", "Uint16", "Uint24", "Uint32", "Int8", "Int16", "Int24", "Int32"]
):
    msg = str(exc_info.value).lower()
    assert "EnumField".lower() in msg
    assert "overflows".lower() in msg
    assert "Limit.FIRST = ".lower() in msg  # this ensures that the enum identifier is properly formatted, even for IntEnum and derivatives
    assert int_type.lower() in msg


def test_enumU8():
    class TestStructure(BaseStruct):
        some_field: EnumU8[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "TestStructure.some_field", True, False,"B", 1, 1)
    assert_general_integer_checks(f, False)

    TestStructure(some_field=2)     # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -1
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU8[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint8")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**8
        class UpperLimitStructure(BaseStruct):
            some_field: EnumU8[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Uint8")


def test_enumU16():
    class TestStructure(BaseStruct):
        some_field: EnumU16[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "TestStructure.some_field", True, False, "H", 1, 2)
    assert_general_integer_checks(f, False)

    TestStructure(some_field=2)     # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -1
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU16[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint16")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**16
        class UpperLimitStructure(BaseStruct):
            some_field: EnumU16[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Uint16")


def test_enumU32():
    class TestStructure(BaseStruct):
        some_field: EnumU32[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "TestStructure.some_field", True, False, "I", 1, 4)
    assert_general_integer_checks(f, False)

    TestStructure(some_field=2)     # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -1
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU32[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint32")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**32
        class UpperLimitStructure(BaseStruct):
            some_field: EnumU32[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Uint32")
    

def test_enumU64():
    class TestStructure(BaseStruct):
        some_field: EnumU64[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "TestStructure.some_field", True, False, "Q", 1, 8)
    assert_general_integer_checks(f, False)

    TestStructure(some_field=2)     # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -1
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU64[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint64")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**64
        class UpperLimitStructure(BaseStruct):
            some_field: EnumU64[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Uint64")


def test_enum8():
    class TestStructure(BaseStruct):
        some_field: Enum8[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "TestStructure.some_field", True, False, "b", 1, 1)
    assert_general_integer_checks(f, True)

    TestStructure(some_field=1)     # valid enum value
    TestStructure(some_field=-2)    # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -2**7 - 1
        class LowerLimitStructure(BaseStruct):
            some_field: Enum8[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Int8")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**7
        class UpperLimitStructure(BaseStruct):
            some_field: Enum8[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Int8")


def test_enum16():
    class TestStructure(BaseStruct):
        some_field: Enum16[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "TestStructure.some_field", True, False, "h", 1, 2)
    assert_general_integer_checks(f, True)

    TestStructure(some_field=1)     # valid enum value
    TestStructure(some_field=-2)    # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -2**15 - 1
        class LowerLimitStructure(BaseStruct):
            some_field: Enum16[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Int16")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**15
        class UpperLimitStructure(BaseStruct):
            some_field: Enum16[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Int16")


def test_enum32():
    class TestStructure(BaseStruct):
        some_field: Enum32[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "TestStructure.some_field", True, False, "i", 1, 4)
    assert_general_integer_checks(f, True)

    TestStructure(some_field=1)     # valid enum value
    TestStructure(some_field=-2)    # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -2**31 - 1
        class LowerLimitStructure(BaseStruct):
            some_field: Enum32[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Int32")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**31
        class UpperLimitStructure(BaseStruct):
            some_field: Enum32[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Int32")
    

def test_enum64():
    class TestStructure(BaseStruct):
        some_field: Enum64[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "TestStructure.some_field", True, False, "q", 1, 8)
    assert_general_integer_checks(f, True)

    TestStructure(some_field=1)     # valid enum value
    TestStructure(some_field=-2)    # valid enum value
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Enum):
            FIRST = -2**63 - 1
        class LowerLimitStructure(BaseStruct):
            some_field: Enum64[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Int64")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.Enum):
            FIRST = 2**63
        class UpperLimitStructure(BaseStruct):
            some_field: Enum64[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Int64")


def test_enum_variant_int_enum():
    class TestIntEnum(enum.IntEnum):
        FIRST = 0
        SECOND = 1
        THIRD = 2
        FOURTH = 3
        FIFTH = 4

    class TestStructure(BaseStruct):
        some_field: Enum64[TestIntEnum]

    TestStructure(some_field=1)     # valid enum value
    inst = TestStructure(some_field=4)    # valid enum value
    assert isinstance(inst.some_field, int)

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=10)    # invalid enum value
    assert_validation_error(exc_info, "enum", 10)

    # make sure the overflow error message is properly formatted for Int variants of enum
    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.IntEnum):
            FIRST = -1
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU16[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint16")

    with pytest.raises(ValueError) as exc_info:
        class UpperLimit(enum.IntEnum):
            FIRST = 2**8
        class UpperLimitStructure(BaseStruct):
            some_field: EnumU8[UpperLimit]
    assert_enum_out_of_range_error(exc_info, "Uint8")


def test_enum_variant_flag():
    # make sure flag can be used and is properly serialized
    class TestFlag(enum.Flag):
        FIRST = enum.auto()
        SECOND = enum.auto()
        THIRD = enum.auto()
        FOURTH = enum.auto()
        FIFTH = enum.auto()

    class TestStructure(BaseStruct):
        some_field: EnumU8[TestFlag]

    inst = TestStructure(some_field=1)     # valid enum value
    assert inst.some_field == TestFlag.FIRST
    assert inst.struct_dump_bytes() == b"\x01"
    inst = TestStructure(some_field=6)     # valid enum value
    assert inst.some_field == TestFlag.THIRD | TestFlag.SECOND
    assert inst.struct_dump_bytes() == b"\x06"
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=104)    # invalid enum value
    assert_validation_error(exc_info, "enum", 104)

    # make sure the limit message is properly formatted for flags
    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.Flag):
            FIRST = 256
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU8[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint8")
    

def test_enum_variant_int_flag():
    # make sure IntFlag can be used and is properly serialized
    class TestIntFlag(enum.IntFlag):
        FIRST = enum.auto()
        SECOND = enum.auto()
        THIRD = enum.auto()
        FOURTH = enum.auto()
        FIFTH = enum.auto()

    class TestStructure(BaseStruct):
        some_field: EnumU8[TestIntFlag]

    inst = TestStructure(some_field=1)     # valid enum value
    assert inst.some_field == TestIntFlag.FIRST
    assert inst.struct_dump_bytes() == b"\x01"
    inst = TestStructure(some_field=6)     # valid enum value
    assert inst.some_field == TestIntFlag.THIRD | TestIntFlag.SECOND
    assert inst.struct_dump_bytes() == b"\x06"
    # IntFlag does not error when assigning invalid values
    inst = TestStructure(some_field=104)    # invalid enum value

    # make sure the limit message is properly formatted for IntFlags
    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.IntFlag):
            FIRST = 256
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU8[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint8")


def test_enum_variant_str():
    # make sure StrEnum is forbidden
    class TestStrEnum(enum.StrEnum):
        FIRST = "1"
        SECOND = "2"
        THIRD = "3"
        FOURTH = "4"
        FIFTH = "5"
    # make sure the limit message is properly formatted
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: EnumU8[TestStrEnum]
    assert "StrEnum" in str(exc_info.value)


## Enumeration literals ##

def test_enumU8_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: EnumU8[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False,"B", 1, 1)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enumU16_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: EnumU16[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "H", 1, 2)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\0\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enumU32_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: EnumU32[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "I", 1, 4)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 
    

def test_enumU64_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: EnumU64[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "Q", 1, 8)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enum8_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Enum8[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "b", 1, 1)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enum16_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Enum16[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "h", 1, 2)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\0\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enum32_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Enum32[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "i", 1, 4)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 
    

def test_enum64_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Enum64[Literal[KnownGoodEnumUnsigned.THIRD]] = 2
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False, "q", 1, 8)
    assert_general_integer_checks(f, True)

    # check correct literal values 
    inst = TestStructure(some_field=KnownGoodEnumUnsigned.THIRD)
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD
    inst = TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x02")
    assert inst.some_field == KnownGoodEnumUnsigned.THIRD

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=2)    # pydantic unfortunately doesn't coerce ints to enum literals
    assert_validation_error(exc_info, "literal_error", 2)
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\0\0\0\0\0\0\0\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enum_literal_variant_int_enum():
    class TestIntEnum(enum.IntEnum):
        FIRST = 0
        SECOND = 1
        THIRD = 2
        FOURTH = 3
        FIFTH = 4

    class TestStructure(BaseStruct):
        some_field: EnumU8[Literal[TestIntEnum.THIRD]]

    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False,"B", 1, 1)
    assert_general_integer_checks(f, False)

    # check correct literal values 
    inst = TestStructure(some_field=TestIntEnum.THIRD)
    assert inst.some_field == TestIntEnum.THIRD
    inst = TestStructure.struct_validate_bytes(b"\x02")
    assert inst.some_field == TestIntEnum.THIRD
    # int enum literal should also support initializing from integer unlike normal enum
    TestStructure(some_field=2)
    assert inst.some_field == TestIntEnum.THIRD
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x03")
    assert_validation_error(exc_info, "literal_error")
    
    with pytest.raises(StructPackingError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x06")    # not a valid enum value
    assert "ValueError" in str(exc_info.value) 
    assert "is not a valid" in str(exc_info.value) 


def test_enum_literal_variant_str():
    # make sure StrEnum is forbidden
    class TestStrEnum(enum.StrEnum):
        FIRST = "1"
        SECOND = "2"
        THIRD = "3"
        FOURTH = "4"
        FIFTH = "5"
    # make sure the limit message is properly formatted
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: EnumU8[Literal[TestStrEnum.THIRD]]
    assert "StrEnum" in str(exc_info.value)
    assert "Type of Literal value" in str(exc_info.value)


def test_enum_literal_wrong_type():
    # make sure  any other type doesn't work and
    # make sure the limit message is properly formatted
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: EnumU8[Literal["Hi"]]
    assert "<class 'str'>" in str(exc_info.value)
    assert "Type of Literal value" in str(exc_info.value)


## Float Testing ##

def test_float32():
    class TestStructure(BaseStruct):
        some_field: Float32
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), FloatField)
    assert_general_field_checks(f, float, "TestStructure.some_field", True, False, "f", 1, 4)

    inst = TestStructure(some_field=2)     # cast to float
    assert type(inst.some_field) is float
    assert inst.some_field == 2.0


def test_float64():
    class TestStructure(BaseStruct):
        some_field: Float64
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), FloatField)
    assert_general_field_checks(f, float, "TestStructure.some_field", True, False, "d", 1, 8)

    inst = TestStructure(some_field=2)     # cast to float
    assert type(inst.some_field) is float
    assert inst.some_field == 2.0


## Char testing ##

def test_char():
    class TestStructure(BaseStruct):
        some_field: Char
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), CharField)
    assert_general_field_checks(f, str, "TestStructure.some_field", True, False, "c", 1, 1)
    # check that the pydantic length constraint is present
    assert any((m.max_length == 1 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 1 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)

    inst = TestStructure(some_field="A")    # valid char
    assert type(inst.some_field) is str
    assert inst.some_field == "A"
    assert isinstance(inst.struct_dump_elements()[0], bytes)
    assert inst.struct_dump_bytes() == b"A"
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field="AB")  # too long
    assert_validation_error(exc_info, "string_too_long", "AB")

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field="")    # too short
    assert_validation_error(exc_info, "string_too_short", "")


def test_char_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: LitChar[Literal["A", "B"]] = "A"
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), CharField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False,"c", 1, 1)

    # check correct literal values 
    inst = TestStructure(some_field="A")
    assert inst.some_field == "A"
    inst = TestStructure.struct_validate_bytes(b"B")
    assert inst.some_field == "B"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"C")
    assert_validation_error(exc_info, "literal_error")

    inst = TestStructure(some_field="A")
    assert inst.struct_dump_bytes() == b"A"


## Bool testing ##

def test_bool():
    class TestStructure(BaseStruct):
        some_field: Bool
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BoolField)
    assert_general_field_checks(f, bool, "TestStructure.some_field", True, False, "?", 1, 1)

    inst = TestStructure(some_field=1)    # coerced to bool
    assert type(inst.some_field) is bool
    assert inst.some_field == True
    inst = TestStructure(some_field="1")    # coerced to bool
    assert type(inst.some_field) is bool
    assert inst.some_field == True
    inst = TestStructure(some_field=False)
    assert type(inst.some_field) is bool
    assert inst.some_field == False

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field="2")    # not coercible to bool
    assert_validation_error(exc_info, "bool_parsing", "2")
    

## Bytes testing ##

def test_bytes_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[Bytes, Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BytesField)
    assert_general_field_checks(f, bytes, "TestStructure.some_field", True, False, "5s", 1, 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    inst = TestStructure(some_field=b"Hihi")    # valid bytes
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hihi"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=b"Hihihi")   # too long
    assert_validation_error(exc_info, "bytes_too_long", b"Hihihi")


def test_bytes_no_len():
    # bytes without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: Bytes
    assert_missing_config_error(exc_info, "Len")


def test_bytes_exact():
    class TestStructure(BaseStruct):
        some_field: Annotated[Bytes, Len(5, min="same")]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BytesField)

    # should have both min and max
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 5 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field=b"Hihia")    # valid bytes
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hihia"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=b"Hihi")   # too short
    assert_validation_error(exc_info, "bytes_too_short", b"Hihi")


def test_bytes_explicit_min():
    class TestStructure(BaseStruct):
        some_field: Annotated[Bytes, Len(5, min=3)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BytesField)

    # should have both min and max
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 3 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field=b"Hihi")    # valid bytes
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hihi"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=b"Hi")   # too short
    assert_validation_error(exc_info, "bytes_too_short", b"Hi")


def test_bytes_ignore_with_min():
    class TestStructure(BaseStruct):
        some_field: Annotated[Bytes, Len(5, min="same", ignore=True)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BytesField)

    # should have neither min nor max but instead custom leninfo
    assert not any(isinstance(m, annotated_types.MaxLen) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    assert any(isinstance(m, LenInfo) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field=b"Hihia6<s")    # still valid
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hihia6<s"
    inst.struct_dump_elements() # should not error

    inst = TestStructure(some_field=b"Hi")    # still valid
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hi"
    inst.struct_dump_elements() # should not error


def test_bytes_ignore():
    class TestStructure(BaseStruct):
        some_field: Annotated[Bytes, Len(5, ignore=True)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BytesField)

    # should have neither min nor max but instead custom leninfo
    assert not any(isinstance(m, annotated_types.MaxLen) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    assert any(isinstance(m, LenInfo) for m in f.annotation_metadata)
    inst = TestStructure(some_field=b"Hihia6<s")    # still valid
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hihia6<s"
    inst.struct_dump_elements() # should not error

    inst = TestStructure(some_field=b"Hi")    # still valid
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hi"
    inst.struct_dump_elements() # should not error


## String testing ##

def test_string_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[String, Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)
    assert_general_field_checks(f, str, "TestStructure.some_field", True, False, "5s", 1, 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    inst = TestStructure(some_field="Hihi")    # valid string
    assert type(inst.some_field) is str
    assert inst.some_field == "Hihi"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field="Hihihi")   # too long
    assert_validation_error(exc_info, "string_too_long", "Hihihi")


def test_string_no_len():
    # string without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: String
    assert_missing_config_error(exc_info, "Len")


def test_string_exact():
    class TestStructure(BaseStruct):
        some_field: Annotated[String, Len(5, min="same")]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)

    # should have both min and max
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 5 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field="Hihia")    # valid string
    assert type(inst.some_field) is str
    assert inst.some_field == "Hihia"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field="Hihi")   # too short
    assert_validation_error(exc_info, "string_too_short", "Hihi")


def test_string_explicit_min():
    class TestStructure(BaseStruct):
        some_field: Annotated[String, Len(5, min=3)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)

    # should have both min and max
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 3 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field="Hihi")    # valid string
    assert type(inst.some_field) is str
    assert inst.some_field == "Hihi"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field="Hi")   # too short
    assert_validation_error(exc_info, "string_too_short", "Hi")


def test_string_ignore_with_min():
    class TestStructure(BaseStruct):
        some_field: Annotated[String, Len(5, min="same", ignore=True)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)

    # should have neither min nor max but instead custom leninfo
    assert not any(isinstance(m, annotated_types.MaxLen) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    assert any(isinstance(m, LenInfo) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field="Hihia6<s")    # still valid
    assert type(inst.some_field) is str
    assert inst.some_field == "Hihia6<s"
    inst.struct_dump_elements() # should not error

    inst = TestStructure(some_field="Hi")    # still valid
    assert type(inst.some_field) is str
    assert inst.some_field == "Hi"
    inst.struct_dump_elements() # should not error


def test_string_ignore():
    class TestStructure(BaseStruct):
        some_field: Annotated[String, Len(5, ignore=True)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)

    # should have neither min nor max but instead custom leninfo
    assert not any(isinstance(m, annotated_types.MaxLen) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    assert any(isinstance(m, LenInfo) for m in f.annotation_metadata)
    inst = TestStructure(some_field="Hihia6<s")    # still valid
    assert type(inst.some_field) is str
    assert inst.some_field == "Hihia6<s"
    inst.struct_dump_elements() # should not error

    inst = TestStructure(some_field="Hi")    # still valid
    assert type(inst.some_field) is str
    assert inst.some_field == "Hi"
    inst.struct_dump_elements() # should not error


def test_string_literal():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Annotated[LitString[Literal["Hello", "You"]], Len(8, ignore=True)] = 12
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)
    assert_general_field_checks(f, Literal, "TestStructure.some_field", True, False,"8s", 1, 8)

    # check correct literal values 
    inst = TestStructure(some_field="Hello")
    assert inst.some_field == "Hello"
    inst = TestStructure.struct_validate_bytes(b"You\0\0\0\0\0")
    assert inst.some_field == "You"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"Hey!\0\0\0\0")
    assert_validation_error(exc_info, "literal_error")

    inst = TestStructure(some_field="Hello")
    assert inst.struct_dump_bytes() == b"Hello\0\0\0"


## Padding tests ##

def test_padding_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[Padding, Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), PaddingField)
    assert_general_field_checks(f, type(None), "TestStructure.some_field", True, False, "5x", 0, 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    inst = TestStructure()    # not required
    assert inst.some_field is None

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field="Hihihi")   # need none to init
    assert_validation_error(exc_info, "none_required", "Hihihi")


def test_padding_no_len():
    # padding without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: Padding
    assert_missing_config_error(exc_info, "Len")


## Array testing ##

def test_array_list_common():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[Uint16], Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, list, "TestStructure.some_field", True, False, "HHHHH", 5, 10)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    
    # array element has to be a non-top-level integer field
    assert isinstance(el := f.element_field, IntegerField)
    assert_general_field_checks(el, int, "TestStructure.some_field.__element__", False, False, "H", 1, 2)

    inst = TestStructure(some_field=(1, 2, 3))    # should coerce to list
    assert type(inst.some_field) is list
    assert inst.some_field == [1, 2, 3]
    assert type(inst.some_field[0]) is int

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=[1, 2, 3, 4, 8, 9])   # too long
    assert_validation_error(exc_info, "too_long")


def test_array_no_len():
    # string without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: ArrayList[Uint16]
    assert_missing_config_error(exc_info, "Len")


def test_array_exact():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[Uint16], Len(5, min="same")]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)

    # should have both min and max
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 5 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)
    
    TestStructure(some_field=(1, 2, 3, 6, 8))    # ok

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=[1, 2, 3, 4, 8, 9])   # too long
    assert_validation_error(exc_info, "too_long")

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=[1, 2])   # too short
    assert_validation_error(exc_info, "too_short")


def test_array_explicit_min():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[Uint16], Len(5, min=3)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)

    # should have both min and max
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 3 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)
    
    TestStructure(some_field=(1, 2, 3, 6, 4))    # ok

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=[1, 2, 3, 4, 8, 9])   # too long
    assert_validation_error(exc_info, "too_long")

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=[1, 2])   # too short
    assert_validation_error(exc_info, "too_short")


def test_array_ignore_no_filler():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[Uint16], Len(5, min="same", ignore=True)]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)

    # should have neither min nor max but instead custom leninfo
    assert not any(isinstance(m, annotated_types.MaxLen) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    assert any(isinstance(m, LenInfo) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field=[1, 2, 3, 4, 8, 9]) # still valid
    assert type(inst.some_field) is list
    assert inst.some_field == [1, 2, 3, 4, 8, 9]
    inst.struct_dump_elements() # should not error

    inst = TestStructure(some_field=[1, 2]) # still valid
    assert type(inst.some_field) is list
    assert inst.some_field == [1, 2]
    with pytest.raises(StructPackingError) as exc_info:
        inst.struct_dump_elements() # should now error because filler is missing
    e = str(exc_info.value).lower()
    assert "only 2".lower() in e
    assert "no Filler".lower() in e


def test_array_ignore_with_filler():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[Uint16], Len(5, min="same", ignore=True), Filler()]
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)

    # should have neither min nor max but instead custom leninfo
    assert not any(isinstance(m, annotated_types.MaxLen) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    assert any(isinstance(m, LenInfo) for m in f.annotation_metadata)
    
    inst = TestStructure(some_field=[1, 2, 3, 4, 8, 9]) # still valid
    assert type(inst.some_field) is list
    assert inst.some_field == [1, 2, 3, 4, 8, 9]
    inst.struct_dump_elements() # should not error

    inst = TestStructure(some_field=[1, 2]) # still valid
    assert type(inst.some_field) is list
    assert inst.some_field == [1, 2]
    inst.struct_dump_elements() # should now work and fill with default constructor


def test_array_of_arrays():
    """
    Complex 3 dimensional array with string elements
    """
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[
            Annotated[ArrayList[
                Annotated[ArrayList[
                    Annotated[String, Len(10)]
                ], Len(5), Filler()]    # default filler mode
            ], Len(5), Filler()]    # same
        ], Len(5), Filler()]    # same

    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, list, "TestStructure.some_field", True, False, "".join(["10s" * 5 * 5 * 5]), 5 * 5 * 5, 10 * 5 * 5 * 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    # check that the array contains another array (not top level)
    assert isinstance(f := f.element_field, ArrayField)
    assert_general_field_checks(f, list, "TestStructure.some_field.__element__", False, False, "".join(["10s" * 5 * 5]), 5 * 5, 10 * 5 * 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    # check that this array contains yet another array (not top level)
    assert isinstance(f := f.element_field, ArrayField)
    assert_general_field_checks(f, list, "TestStructure.some_field.__element__.__element__", False, False, "".join(["10s" * 5]), 5, 10 * 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    # check that this last array contains strings (not top level)
    assert isinstance(f := f.element_field, StringField)
    assert_general_field_checks(f, str, "TestStructure.some_field.__element__.__element__.__element__", False, False, "10s", 1, 10)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 10 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    test_data = [   # valid, filled with filler
        [
            ["Hello", "These", "are", "words"],
            ["And", "even", "more", "words"],
            ['']
        ],
        [
            [],
            ["Next", "2D", "element"]
        ],
    ]
    inst = TestStructure(some_field=test_data)
    assert type(inst.some_field) is list
    bytes_rep = inst.struct_dump_bytes()
    assert len(bytes_rep) == (10 * 5 * 5 * 5) # should not error

    # recover array
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field[0][0][0] == "Hello"
    assert unpacked.some_field[0][0][1] == "These"
    assert unpacked.some_field[0][0][2] == "are"
    assert unpacked.some_field[0][0][3] == "words"
    assert unpacked.some_field[0][1][0] == "And"
    assert unpacked.some_field[0][1][1] == "even"
    assert unpacked.some_field[0][1][2] == "more"
    assert unpacked.some_field[0][1][3] == "words"
    assert unpacked.some_field[1][1][0] == "Next"
    assert unpacked.some_field[1][1][1] == "2D"
    assert unpacked.some_field[1][1][2] == "element"
    # make sure the trailing empty fillers are stripped but not leading ones
    assert len(unpacked.some_field) == 2
    assert len(unpacked.some_field[0]) == 2
    assert len(unpacked.some_field[0][0]) == 4
    assert len(unpacked.some_field[0][1]) == 4
    assert len(unpacked.some_field[1]) == 2, "Leading fillers must not be removed"
    assert len(unpacked.some_field[1][1]) == 3


def test_array_tuple():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayTuple[Uint8], Len(5), Filler()]  # default filler mode

    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, tuple, "TestStructure.some_field", True, False, "BBBBB", 5, 5)

    inst = TestStructure(some_field=(1, 2, 3))
    inst2 = TestStructure(some_field=[1, 2, 3]) # should coerce
    assert type(inst.some_field) is tuple
    assert type(inst2.some_field) is tuple
    assert inst == inst2

    # packing
    bytes_rep = inst.struct_dump_bytes()
    assert len(bytes_rep) == 5
    assert bytes_rep == b"\x01\x02\x03\0\0"

    # recover array
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == (1, 2, 3) # trailing fillers stripped


def test_array_set():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArraySet[Uint8], Len(5), Filler()]    # default filler mode

    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, set, "TestStructure.some_field", True, False, "BBBBB", 5, 5)

    inst = TestStructure(some_field=set((1, 0, 2, 3)))  # zero (==int()) Filler should be stripped after parsing
    inst2 = TestStructure(some_field=[1, 2, 0, 3]) # should coerce
    assert type(inst.some_field) is set
    assert type(inst2.some_field) is set
    assert inst == inst2  # zero (==int()) Filler should be stripped after parsing

    # packing
    bytes_rep = inst.struct_dump_bytes()
    assert len(bytes_rep) == 5
    assert set(bytes_rep) == set(b"\x01\x02\x03\0\0")

    # recover array
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == set((1, 2, 3))    # there should be no zero filler


def test_array_frozenset():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayFrozenSet[Uint8], Len(5), Filler()]  # default filler mode

    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, frozenset, "TestStructure.some_field", True, False, "BBBBB", 5, 5)

    inst = TestStructure(some_field=frozenset((1, 0, 2, 3)))  # zero (==int()) Filler should be stripped after parsing
    inst2 = TestStructure(some_field=[1, 2, 0, 3]) # should coerce
    assert type(inst.some_field) is frozenset
    assert type(inst2.some_field) is frozenset
    assert inst == inst2  # zero (==int()) Filler should be stripped after parsing

    # packing
    bytes_rep = inst.struct_dump_bytes()
    assert len(bytes_rep) == 5
    assert set(bytes_rep) == frozenset(b"\x01\x02\x03\0\0")

    # recover array
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == frozenset((1, 2, 3))  # there should be no zero filler


def test_array_deque():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayDeque[Uint8], Len(5), Filler()]

    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, deque, "TestStructure.some_field", True, False, "BBBBB", 5, 5)

    inst = TestStructure(some_field=deque((1, 2, 3)))
    inst2 = TestStructure(some_field=[1, 2, 3]) # should coerce
    assert type(inst.some_field) is deque
    assert type(inst2.some_field) is deque
    assert inst == inst2

    # packing
    bytes_rep = inst.struct_dump_bytes()
    assert len(bytes_rep) == 5
    assert bytes_rep == b"\x01\x02\x03\0\0"

    # recover array
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == deque((1, 2, 3))  # trailing fillers stripped


def test_array_filler_keep():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayTuple[Uint8], Len(6), Filler(6, parse_mode="keep")]

    # additional filler (value "6") should be generated at end
    inst = TestStructure(some_field=(6, 1, 6, 2, 3))
    bytes_rep = inst.struct_dump_bytes()
    assert bytes_rep == b"\x06\x01\x06\x02\x03\x06"

    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == (6, 1, 6, 2, 3, 6), "all filler should be kept"


def test_array_filler_remove():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayTuple[Uint8], Len(6), Filler(6, parse_mode="remove")]

    # additional filler (value "6") should be generated at end
    inst = TestStructure(some_field=(6, 1, 6, 2, 3))
    bytes_rep = inst.struct_dump_bytes()
    assert bytes_rep == b"\x06\x01\x06\x02\x03\x06"
    
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == (1, 2, 3), "all filler should be removed"


def test_array_filler_strip_leading():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayTuple[Uint8], Len(6), Filler(6, parse_mode="strip-leading")]

    # additional filler (value "6") should be generated at end
    inst = TestStructure(some_field=(6, 1, 6, 2, 3))
    bytes_rep = inst.struct_dump_bytes()
    assert bytes_rep == b"\x06\x01\x06\x02\x03\x06"
    
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == (1, 6, 2, 3, 6), "only leading filler should be stripped"


def test_array_filler_strip_trailing():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayTuple[Uint8], Len(6), Filler(6, parse_mode="strip-trailing")]

    # additional filler (value "6") should be generated at end
    inst = TestStructure(some_field=(6, 1, 6, 2, 3))
    bytes_rep = inst.struct_dump_bytes()
    assert bytes_rep == b"\x06\x01\x06\x02\x03\x06"
    
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == (6, 1, 6, 2, 3), "only trailing filler should be stripped"


def test_array_filler_skip_both():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayTuple[Uint8], Len(6), Filler(6, parse_mode="strip-both")]

    # additional filler (value "6") should be generated at end
    inst = TestStructure(some_field=(6, 1, 6, 2, 3))
    bytes_rep = inst.struct_dump_bytes()
    assert bytes_rep == b"\x06\x01\x06\x02\x03\x06"
    
    unpacked = TestStructure.struct_validate_bytes(bytes_rep)
    assert unpacked.some_field == (1, 6, 2, 3), "only leading and trailing filler should be stripped"


## Combined struct test ##

def test_combined_struct():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        uint8: Uint8
        uint16: Uint16
        uint32: Uint32
        uint64: Uint64
        int8: Int8
        int16: Int16
        int32: Int32
        int64: Int64
        enumu8: EnumU8[KnownGoodEnumUnsigned]
        enumu16: EnumU16[KnownGoodEnumUnsigned]
        enumu32: EnumU32[KnownGoodEnumUnsigned]
        enumu64: EnumU64[KnownGoodEnumUnsigned]
        enum8: Enum8[KnownGoodEnumSigned]
        enum16: Enum16[KnownGoodEnumSigned]
        enum32: Enum32[KnownGoodEnumSigned]
        enum64: Enum64[KnownGoodEnumSigned]
        float32: Float32
        float64: Float64
        char: Char
        bool: Bool
        string: Annotated[String, Len(10)]
        bytes: Annotated[Bytes, Len(11)]
        padding: Annotated[Padding, Len(3)]
        array_list: Annotated[ArrayList[Int8], Len(2)]
        array_tuple: Annotated[ArrayTuple[Int8], Len(2)]
        array_set: Annotated[ArraySet[Int8], Len(2)]
        array_frozenset: Annotated[ArrayFrozenSet[Int8], Len(3)]
        array_deque: Annotated[ArrayDeque[Int8], Len(3)]
    
    # test combined structure config
    assert TestStructure.__bindantic_element_consumption__ == 34
    assert TestStructure.__bindantic_byte_consumption__ == 110
    assert TestStructure.__bindantic_struct_code__ == ">BHIQbhiqBHIQbhiqfdc?10s11s3xbbbbbbbbbbbb"

    # test instantiation
    inst = TestStructure(
        uint8=0x8F,
        uint16=0x43 | 0x56 << 8,
        uint32=0x43 | 0x56 << 8 | 0x89 << 16 | 0x94 << 24,
        uint64=0x43 | 0x56 << 8 | 0x89 << 16 | 0x94 << 24 | 0x43 << 32 | 0x56 << 40 | 0x89 << 48 | 0x94 << 56,
        int8=0x19,
        int16=0x43 | 0x56 << 8,
        int32=0x43 | 0x56 << 8 | 0x89 << 16 | 0x14 << 24,
        int64=0x43 | 0x56 << 8 | 0x89 << 16 | 0x94 << 24 | 0x43 << 32 | 0x56 << 40 | 0x89 << 48 | 0x14 << 56,
        enumu8=KnownGoodEnumUnsigned.FIRST,
        enumu16=KnownGoodEnumUnsigned.SECOND,
        enumu32=KnownGoodEnumUnsigned.THIRD,
        enumu64=KnownGoodEnumUnsigned.FOURTH,
        enum8=KnownGoodEnumSigned.FIRST,
        enum16=KnownGoodEnumSigned.SECOND,
        enum32=KnownGoodEnumSigned.THIRD,
        enum64=KnownGoodEnumSigned.FOURTH,
        float32=267.5,  # 0x4385c000
        float64=740.2348,   # 0x408721e0ded288ce
        char="C",
        bool=True,
        string="Hello",
        bytes=b"Goodbye\0\0\0\0",   # would be padded but compare would otherwise fail
        array_list=[1, 2],
        array_tuple=(3, 4),
        array_set=[5, 6],
        array_frozenset=[7, 8, 9],
        array_deque=[10, 11, 12]
    )
    
    # binary verification
    byte_rep = inst.struct_dump_bytes()
    offset = 0
    def get_bytes(n: int):
        nonlocal offset
        b = byte_rep[offset:(offset + n)]
        offset += n
        return b
    
    assert get_bytes(1) == b"\x8F"
    assert get_bytes(2) == b"\x56\x43"
    assert get_bytes(4) == b"\x94\x89\x56\x43"
    assert get_bytes(8) == b"\x94\x89\x56\x43\x94\x89\x56\x43"
    assert get_bytes(1) == b"\x19"
    assert get_bytes(2) == b"\x56\x43"
    assert get_bytes(4) == b"\x14\x89\x56\x43"
    assert get_bytes(8) == b"\x14\x89\x56\x43\x94\x89\x56\x43"
    assert get_bytes(1) == b"\x00"
    assert get_bytes(2) == b"\x00\x01"
    assert get_bytes(4) == b"\x00\x00\x00\x02"
    assert get_bytes(8) == b"\x00\x00\x00\x00\x00\x00\x00\x03"
    assert get_bytes(1) == b"\xFE"      # two's complement -2
    assert get_bytes(2) == b"\xFF\xFF"  # two's complement -1
    assert get_bytes(4) == b"\x00\x00\x00\x00"
    assert get_bytes(8) == b"\x00\x00\x00\x00\x00\x00\x00\x01"
    assert get_bytes(4) == b"\x43\x85\xc0\x00"
    assert get_bytes(8) == b"\x40\x87\x21\xe0\xde\xd2\x88\xce"
    assert get_bytes(1) == "C".encode("utf-8")  # utf-8 is default encoding for bindantic (and also python)
    assert get_bytes(1) == b"\x01"
    assert get_bytes(10) == b"Hello\0\0\0\0\0"
    assert get_bytes(11) == b"Goodbye\0\0\0\0"
    assert get_bytes(3) == b"\0\0\0"    # padding
    assert get_bytes(4) == b"\x01\x02\x03\x04"
    assert set(get_bytes(2)) == set(b"\x05\x06")        # set element order can change
    assert set(get_bytes(3)) == set(b"\x07\x08\x09")    # set element order can change
    assert get_bytes(3) == b"\x0A\x0B\x0C"

    # test unpacking
    reconstruction = TestStructure.struct_validate_bytes(byte_rep)
    assert reconstruction == inst


## Byteorder tests ##

def test_byteorder_native_aligned():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="native-aligned")
        some_field: Uint16
    
    assert TestStructure.__bindantic_struct_code__ == "@H"
    data = TestStructure(some_field=1 << 8 | 2).struct_dump_bytes()

    # for a single uint16 alignment does not matter. We cannot easily test
    # architecture native alignment.
    if sys.byteorder == "big":
        assert data == b"\x01\x02"
    else:
        assert data == b"\x02\x01"


def test_byteorder_native():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="native")
        some_field: Uint16
    
    assert TestStructure.__bindantic_struct_code__ == "=H"
    data = TestStructure(some_field=1 << 8 | 2).struct_dump_bytes()

    if sys.byteorder == "big":
        assert data == b"\x01\x02"
    else:
        assert data == b"\x02\x01"


def test_byteorder_big_endian():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
    
    assert TestStructure.__bindantic_struct_code__ == ">H"
    data = TestStructure(some_field=1 << 8 | 2).struct_dump_bytes()
    assert data == b"\x01\x02"


def test_byteorder_little_endian():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="little-endian")
        some_field: Uint16
    
    assert TestStructure.__bindantic_struct_code__ == "<H"
    data = TestStructure(some_field=1 << 8 | 2).struct_dump_bytes()
    assert data == b"\x02\x01"


def test_byteorder_network():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="network")
        some_field: Uint16
    
    assert TestStructure.__bindantic_struct_code__ == "!H"
    data = TestStructure(some_field=1 << 8 | 2).struct_dump_bytes()
    assert data == b"\x01\x02"


## Outlet tests ##

def test_outlet_default():
    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        double_outlet: Outlet[Uint16]

        @pydantic.computed_field
        def double(self) -> Uint16:
            return self.some_field * 2
    
    # normal field
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "H", 1, 2)
    
    # outlet field
    assert isinstance(f := TestStructure.struct_fields.get("double"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.double", True, True, "H", 1, 2)

    # together
    assert TestStructure.__bindantic_struct_code__ == ">HH"
    data = TestStructure(some_field=3).struct_dump_elements()
    assert data == (3, 6)

    # when parsing, the value should be ignored
    parsed = TestStructure.struct_validate_elements((3, 5))
    assert parsed.double == 6, "double must be computed and not parsed"


def test_outlet_type_mismatch_small():
    with pytest.raises(TypeError):
        class TestStructure(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            some_field: Uint16
            double_outlet: Outlet[Uint16]

            @pydantic.computed_field
            def double(self) -> Uint32:
                return self.some_field * 2
    

def test_outlet_type_mismatch_large():
    with pytest.raises(TypeError):
        class TestStructure(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            some_field: Uint16
            double_outlet: Outlet[Uint16]

            @pydantic.computed_field
            def double(self) -> String:
                return self.some_field * 2
    

def test_outlet_missing_source():
    with pytest.raises(NameError):
        class TestStructure(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            some_field: Uint16
            double_outlet: Outlet[Uint16]   # must error because there is no matching computed field


## nested structures ##

def test_nested_structure():
    class SubStruct(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_nested_field: Uint8

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: SubStruct
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "H", 1, 2)

    # substructure should be a special field
    assert isinstance(f := TestStructure.struct_fields.get("substructure"), NestedStructField)
    assert_general_field_checks(f, SubStruct, "TestStructure.substructure", True, False, "1s", 1, 1)

    # substructure should contain integer as normal
    assert isinstance(f := f.type_annotation.struct_fields.get("some_nested_field"), IntegerField)
    assert_general_field_checks(f, int, "SubStruct.some_nested_field", True, False, "B", 1, 1)
    
    # instantiation
    inst = TestStructure(
        some_field=0x56,
        substructure={"some_nested_field": 0x78}
    )
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\x78"

    # parsing
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert reconstruct == inst

    
def test_nested_structure_inline():

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        class SubStruct(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            some_nested_field: Uint8
        substructure: SubStruct
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "H", 1, 2)

    # substructure should be a special field
    assert isinstance(f := TestStructure.struct_fields.get("substructure"), NestedStructField)
    assert_general_field_checks(f, TestStructure.SubStruct, "TestStructure.substructure", True, False, "1s", 1, 1)

    # substructure should contain integer as normal
    assert isinstance(f := f.type_annotation.struct_fields.get("some_nested_field"), IntegerField)
    assert_general_field_checks(f, int, "SubStruct.some_nested_field", True, False, "B", 1, 1)
    
    # instantiation
    inst = TestStructure(
        some_field=0x56,
        substructure={"some_nested_field": 0x78}
    )
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\x78"

    # parsing
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert reconstruct == inst


def test_array_of_nested_structures():
    class SubStruct(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_nested_field: Uint8
        wider_variable: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructures: Annotated[ArrayList[SubStruct], Len(3)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "TestStructure.some_field", True, False, "H", 1, 2)

    # substructure should now be a list
    assert isinstance(f := TestStructure.struct_fields.get("substructures"), ArrayField)
    assert_general_field_checks(f, list, "TestStructure.substructures", True, False, "3s3s3s", 3, 9)

    # substructure list should contain substructure
    assert isinstance(f := f.element_field, NestedStructField)
    assert_general_field_checks(f, SubStruct, "TestStructure.substructures.__element__", False, False, "3s", 1, 3)

    # substructure should contain integers as normal
    assert isinstance(i := f.type_annotation.struct_fields.get("some_nested_field"), IntegerField)
    assert_general_field_checks(i, int, "SubStruct.some_nested_field", True, False, "B", 1, 1)
    assert isinstance(i := f.type_annotation.struct_fields.get("wider_variable"), IntegerField)
    assert_general_field_checks(i, int, "SubStruct.wider_variable", True, False, "H", 1, 2)
    
    # instantiation
    inst = TestStructure(
        some_field=0x56,
        substructures=[
            {"some_nested_field": 0x78, "wider_variable": 0x00},
            {"some_nested_field": 0x79, "wider_variable": 0x00},
            {"some_nested_field": 0x7A, "wider_variable": 0x00},
        ]
    )
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\x78\0\0\x79\0\0\x7A\0\0"

    # parsing
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert reconstruct == inst
    # check that dict elements are properly converted
    assert reconstruct.substructures[0] == SubStruct(some_nested_field=0x78, wider_variable=0x0)


## Union testing ##

def test_union_int_literal():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: Lit8[Literal[2]] = 2
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: Lit8[Literal[3]] = 3
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    assert isinstance(f := TestStructure.struct_fields.get("substructure"), UnionField)
    assert_general_field_checks(f, typing.Union, "TestStructure.substructure", True, False, "3s", 1, 3)

    ## instantiation with SubStructA
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": 2}
    )
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\xAB\x02\0"
    
    # unpack and validate again
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructA
    assert reconstruct.substructure.disc == 2
    assert reconstruct == inst

    # with SubStructB should export other layout
    inst.substructure = SubStructB(short=0xAB)
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\x03\0\xAB"

    # unpack and validate again. This should now select SubStructB
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructB
    assert reconstruct.substructure.disc == 3
    assert reconstruct == inst


def test_union_enum_literal():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: EnumU8[Literal[KnownGoodEnumUnsigned.SECOND]] = KnownGoodEnumUnsigned.SECOND
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: EnumU8[Literal[KnownGoodEnumUnsigned.THIRD]] = KnownGoodEnumUnsigned.THIRD
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    assert isinstance(f := TestStructure.struct_fields.get("substructure"), UnionField)
    assert_general_field_checks(f, typing.Union, "TestStructure.substructure", True, False, "3s", 1, 3)

    ## instantiation with SubStructA
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": KnownGoodEnumUnsigned.SECOND}  # pydantic doesn't properly support validating numbers to enum literals
    )
    #inst = TestStructure.model_validate_json("{\"some_field\":86, \"substructure\": {\"short\": 171, \"disc\": 1}}")
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\xAB\x01\0"
    
    # unpack and validate again
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructA
    assert reconstruct.substructure.disc == KnownGoodEnumUnsigned.SECOND
    assert reconstruct == inst

    # with SubStructB should export other layout
    inst.substructure = SubStructB(short=0xAB)
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\x02\0\xAB"
    
    # unpack and validate again. This should now select SubStructB
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)   # bindantic does properly support using enum literals as discriminators and converts them
    assert type(reconstruct.substructure) is SubStructB
    assert reconstruct.substructure.disc == KnownGoodEnumUnsigned.THIRD
    assert reconstruct == inst


def test_union_chr_literal():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: LitChar[Literal["2"]] = "2"
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: LitChar[Literal["3"]] = "3"
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    assert isinstance(f := TestStructure.struct_fields.get("substructure"), UnionField)
    assert_general_field_checks(f, typing.Union, "TestStructure.substructure", True, False, "3s", 1, 3)

    ## instantiation with SubStructA
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": "2"}
    )
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\xAB2\0"
    
    # unpack and validate again
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructA
    assert reconstruct.substructure.disc == "2"
    assert reconstruct == inst

    # with SubStructB should export other layout
    inst.substructure = SubStructB(short=0xAB)
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x563\0\xAB"

    # unpack and validate again. This should now select SubStructB
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructB
    assert reconstruct.substructure.disc == "3"
    assert reconstruct == inst


def test_union_string_literal():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: Annotated[LitString[Literal["Hoha"]], Len(5)] = "Hoha"
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: Annotated[LitString[Literal["No"]], Len(2)] = "No"
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    assert isinstance(f := TestStructure.struct_fields.get("substructure"), UnionField)
    assert_general_field_checks(f, typing.Union, "TestStructure.substructure", True, False, "6s", 1, 6)

    ## instantiation with SubStructA
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": "Hoha"}
    )
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56\xABHoha\0"
    
    # unpack and validate again
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructA
    assert reconstruct.substructure.disc == "Hoha"
    assert reconstruct == inst

    # with SubStructB should export other layout
    inst.substructure = SubStructB(short=0xAB)
    binary_rep = inst.struct_dump_bytes()
    assert binary_rep == b"\x00\x56No\0\xAB\0\0"

    # unpack and validate again. This should now select SubStructB
    reconstruct = TestStructure.struct_validate_bytes(binary_rep)
    assert type(reconstruct.substructure) is SubStructB
    assert reconstruct.substructure.disc == "No"
    assert reconstruct == inst


def test_union_errors_without_discriminator():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: Lit8[Literal[2]] = 2
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: Lit8[Literal[3]] = 3
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: typing.Union[SubStructA, SubStructB]
    
    # test construction with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": 6}
        )
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "literal_error"
    assert e.errors()[1]["type"] == "literal_error"

    # test parsing with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x00\x56\x06\0\xAB")
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "literal_error"
    assert e.errors()[1]["type"] == "literal_error"


def test_union_errors_with_discriminator():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: Lit8[Literal[2]] = 2
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: Lit8[Literal[3]] = 3
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    # test construction with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": 6}
        )
    e = exc_info.value
    assert e.error_count() == 1
    assert e.errors()[0]["type"] == "union_tag_invalid"

    # test parsing with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x00\x56\x06\0\xAB")
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "union_tag_invalid"
    assert e.errors()[1]["type"] == "union_tag_invalid"


def test_union_errors_without_discriminator_enums():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: EnumU8[Literal[KnownGoodEnumUnsigned.SECOND]] = KnownGoodEnumUnsigned.SECOND
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: EnumU8[Literal[KnownGoodEnumUnsigned.THIRD]] = KnownGoodEnumUnsigned.THIRD
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: typing.Union[SubStructA, SubStructB]
    
    # test construction with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": KnownGoodEnumUnsigned.FOURTH}
        )
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "literal_error"
    assert e.errors()[1]["type"] == "literal_error"

    # test construction with valid discriminator for json still fails because pydantic doesn't support
    # converting integer to enum in case of literal type
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": 1}
        )
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "literal_error"
    assert e.errors()[1]["type"] == "literal_error"

    # test parsing with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x00\x56\x06\0\xAB")
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "literal_error" # got 0 for disc which is a valid enum but not the right literal value
    assert e.errors()[1]["type"] == "struct_packing_error"  # got 6 for disc which is not even a valid enum value


def test_union_errors_with_discriminator_enums():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: EnumU8[Literal[KnownGoodEnumUnsigned.SECOND]] = KnownGoodEnumUnsigned.SECOND
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: EnumU8[Literal[KnownGoodEnumUnsigned.THIRD]] = KnownGoodEnumUnsigned.THIRD
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    # test construction with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": KnownGoodEnumUnsigned.FOURTH}
        )
    e = exc_info.value
    assert e.error_count() == 1
    assert e.errors()[0]["type"] == "union_tag_invalid"

    # test construction with valid discriminator for json still fails because pydantic doesn't support
    # converting integer to enum in case of literal type
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": 1}
        )
    e = exc_info.value
    assert e.error_count() == 1
    assert e.errors()[0]["type"] == "union_tag_invalid"

    # test parsing with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x00\x56\x06\0\xAB")
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "union_tag_invalid" # got 0 for disc which is a valid enum but not the right literal value
    assert e.errors()[1]["type"] == "struct_packing_error"  # got 6 for disc which is not even a valid enum value


def test_union_multiple_disc_values():
    class SubStructA(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        short: Uint8
        disc: Lit8[Literal[2, 5]] = 2
    
    class SubStructB(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        disc: Lit8[Literal[3, 9]] = 3
        short: Uint16

    class TestStructure(BaseStruct):
        model_config = StructConfigDict(byte_order="big-endian")
        some_field: Uint16
        substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]
    
    # all the values should work fine for SubStructA
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": 2}
    )
    assert isinstance(inst.substructure, SubStructA)
    inst = TestStructure.struct_validate_bytes(b"\x00\x56\xAB\x02\0")
    assert isinstance(inst.substructure, SubStructA)
    
    # all the values should work fine
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": 5}
    )
    assert isinstance(inst.substructure, SubStructA)
    inst = TestStructure.struct_validate_bytes(b"\x00\x56\xAB\x05\0")
    assert isinstance(inst.substructure, SubStructA)

    # all the values should work fine for SubStructB
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": 3}
    )
    assert isinstance(inst.substructure, SubStructB)
    inst = TestStructure.struct_validate_bytes(b"\x00\x56\x03\0\xAB")
    assert isinstance(inst.substructure, SubStructB)

    # all the values should work fine for SubStructB
    inst = TestStructure(
        some_field=0x56,
        substructure={"short": 0xAB, "disc": 9}
    )
    assert isinstance(inst.substructure, SubStructB)
    inst = TestStructure.struct_validate_bytes(b"\x00\x56\x09\0\xAB")
    assert isinstance(inst.substructure, SubStructB)

    # test construction with invalid discriminator should still fail
    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(
            some_field=0x56,
            substructure={"short": 0xAB, "disc": 6}
        )
    e = exc_info.value
    assert e.error_count() == 1
    assert e.errors()[0]["type"] == "union_tag_invalid"

    # test parsing with invalid discriminator
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure.struct_validate_bytes(b"\x00\x56\x06\0\xAB")
    e = exc_info.value
    assert e.error_count() == 2
    assert e.errors()[0]["type"] == "union_tag_invalid"
    assert e.errors()[1]["type"] == "union_tag_invalid"


def test_create_invalid_union():
    with pytest.raises(TypeError):
        class SubStructA(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            short: Uint8
            disc: Lit8[Literal[2]] = 2
        
        class SubStructB(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            disc: Lit8[Literal[2]] = 2
            short: Uint16

        class TestStructure(BaseStruct):
            model_config = StructConfigDict(byte_order="big-endian")
            some_field: Uint16
            substructure: Annotated[typing.Union[SubStructA, SubStructB], pydantic.Discriminator("disc")]


## len() testing ##

def test_len_on_class():
    class TestStructure(BaseStruct):
        some_field: Uint16
        field2: Uint8
    
    assert len(TestStructure) == 3

def test_len_inst_class():
    class TestStructure(BaseStruct):
        some_field: Uint16
        field2: Uint8
        
    a = TestStructure(some_field=5, field2=7)
    assert len(a) == 3