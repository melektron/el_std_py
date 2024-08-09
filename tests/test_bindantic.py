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
import pydantic
import annotated_types
from collections import deque
from typing import Annotated, Any
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
    field_name: str,
    top_level: bool,
    outlet: bool,
    struct_code: str, 
    element_cons: int, 
    byte_cons: int, 
):
    assert f.type_annotation is f.pydantic_field.annotation
    assert f.annotation_metadata is f.pydantic_field.metadata
    assert get_actual_type(f.type_annotation) is annotation_type
    assert f.field_name == field_name
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


def test_create_struct_intU8():
    class TestStructure(BaseStruct):
        some_field: Uint8 = 578
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False,"B", 1, 1)
    assert_general_integer_checks(f, False)

    # range limits    
    tv = 2**8
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})


def test_create_struct_intU16():
    class TestStructure(BaseStruct):
        some_field: Uint16
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "H", 1, 2)
    assert_general_integer_checks(f, False)

    # range limits
    tv = 2**16
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})


def test_create_struct_intU32():
    class TestStructure(BaseStruct):
        some_field: Uint32
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "I", 1, 4)
    assert_general_integer_checks(f, False)

    # range limits
    tv = 2**32
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})
    

def test_create_struct_intU64():
    class TestStructure(BaseStruct):
        some_field: Uint64
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "Q", 1, 8)
    assert_general_integer_checks(f, False)

    # range limits
    tv = 2**64
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=tv)
    assert_validation_error(exc_info, "less_than", tv, {"lt": tv})

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field=-1)
    assert_validation_error(exc_info, "greater_than_equal", -1, {"ge": 0})


def test_create_struct_int8():
    class TestStructure(BaseStruct):
        some_field: Int8
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "b", 1, 1)
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


def test_create_struct_int16():
    class TestStructure(BaseStruct):
        some_field: Int16
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "h", 1, 2)
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


def test_create_struct_int32():
    class TestStructure(BaseStruct):
        some_field: Int32
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "i", 1, 4)
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
    

def test_create_struct_int64():
    class TestStructure(BaseStruct):
        some_field: Int64
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), IntegerField)
    assert_general_field_checks(f, int, "some_field", True, False, "q", 1, 8)
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


## Enumeration field ##

def assert_enum_out_of_range_error(
    exc_info: pytest.ExceptionInfo[ValueError],
    int_type: typing.Literal["Uint8", "Uint16", "Uint24", "Uint32", "Int8", "Int16", "Int24", "Int32"]
):
    msg = str(exc_info.value).lower()
    assert "EnumField".lower() in msg
    assert "overflows".lower() in msg
    assert "Limit.FIRST = ".lower() in msg  # this ensures that the enum identifier is properly formatted, even for IntEnum and derivatives
    assert int_type.lower() in msg


def test_create_struct_enumU8():
    class TestStructure(BaseStruct):
        some_field: EnumU8[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "some_field", True, False,"B", 1, 1)
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


def test_create_struct_enumU16():
    class TestStructure(BaseStruct):
        some_field: EnumU16[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "some_field", True, False, "H", 1, 2)
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


def test_create_struct_enumU32():
    class TestStructure(BaseStruct):
        some_field: EnumU32[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "some_field", True, False, "I", 1, 4)
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
    

def test_create_struct_enumU64():
    class TestStructure(BaseStruct):
        some_field: EnumU64[KnownGoodEnumUnsigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumUnsigned, "some_field", True, False, "Q", 1, 8)
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


def test_create_struct_enum8():
    class TestStructure(BaseStruct):
        some_field: Enum8[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "some_field", True, False, "b", 1, 1)
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


def test_create_struct_enum16():
    class TestStructure(BaseStruct):
        some_field: Enum16[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "some_field", True, False, "h", 1, 2)
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


def test_create_struct_enum32():
    class TestStructure(BaseStruct):
        some_field: Enum32[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "some_field", True, False, "i", 1, 4)
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
    

def test_create_struct_enum64():
    class TestStructure(BaseStruct):
        some_field: Enum64[KnownGoodEnumSigned]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), EnumField)
    assert_general_field_checks(f, KnownGoodEnumSigned, "some_field", True, False, "q", 1, 8)
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


def test_struct_enum_test_int_enum():
    class TestIntEnum(enum.IntEnum):
        FIRST = 0
        SECOND = 1
        THIRD = 2
        FOURTH = 3
        FIFTH = 4

    class TestStructure(BaseStruct):
        some_field: Enum64[TestIntEnum]

    TestStructure(some_field=1)     # valid enum value
    TestStructure(some_field=4)    # valid enum value
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


def test_struct_enum_test_flag():
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
    

def test_struct_enum_test_int_flag():
    # make sure IntFlag can be used and is properly serialized
    class TestFlag(enum.IntFlag):
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
    # IntFlag does not error when assigning invalid values
    inst = TestStructure(some_field=104)    # invalid enum value

    # make sure the limit message is properly formatted for IntFlags
    with pytest.raises(ValueError) as exc_info:
        class LowerLimit(enum.IntFlag):
            FIRST = 256
        class LowerLimitStructure(BaseStruct):
            some_field: EnumU8[LowerLimit]
    assert_enum_out_of_range_error(exc_info, "Uint8")


def test_struct_enum_test_str():
    # make sure StrEnum is forbidden
    class TestFlag(enum.StrEnum):
        FIRST = "1"
        SECOND = "2"
        THIRD = "3"
        FOURTH = "4"
        FIFTH = "5"
    # make sure the limit message is properly formatted for IntFlags
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: EnumU8[TestFlag]
    assert "StrEnum" in str(exc_info.value)


## Float Testing ##

def test_create_struct_float32():
    class TestStructure(BaseStruct):
        some_field: Float32
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), FloatField)
    assert_general_field_checks(f, float, "some_field", True, False, "f", 1, 4)

    inst = TestStructure(some_field=2)     # cast to float
    assert type(inst.some_field) is float
    assert inst.some_field == 2.0


def test_create_struct_float64():
    class TestStructure(BaseStruct):
        some_field: Float64
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), FloatField)
    assert_general_field_checks(f, float, "some_field", True, False, "d", 1, 8)

    inst = TestStructure(some_field=2)     # cast to float
    assert type(inst.some_field) is float
    assert inst.some_field == 2.0


## Char testing ##

def test_create_struct_char():
    class TestStructure(BaseStruct):
        some_field: Char
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), CharField)
    assert_general_field_checks(f, str, "some_field", True, False, "c", 1, 1)
    # check that the pydantic length constraint is present
    assert any((m.max_length == 1 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert any((m.min_length == 1 if isinstance(m, annotated_types.MinLen) else False) for m in f.annotation_metadata)

    inst = TestStructure(some_field="A")    # valid char
    assert type(inst.some_field) is str
    assert inst.some_field == "A"
    
    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field="AB")  # too long
    assert_validation_error(exc_info, "string_too_long", "AB")

    with pytest.raises(pydantic.ValidationError) as exc_info:
        TestStructure(some_field="")    # too short
    assert_validation_error(exc_info, "string_too_short", "")


## Bool testing ##

def test_create_struct_bool():
    class TestStructure(BaseStruct):
        some_field: Bool
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BoolField)
    assert_general_field_checks(f, bool, "some_field", True, False, "?", 1, 1)

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

def test_create_struct_bytes_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[Bytes, Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), BytesField)
    assert_general_field_checks(f, bytes, "some_field", True, False, "5s", 1, 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    inst = TestStructure(some_field=b"Hihi")    # valid bytes
    assert type(inst.some_field) is bytes
    assert inst.some_field == b"Hihi"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=b"Hihihi")   # too long
    assert_validation_error(exc_info, "bytes_too_long", b"Hihihi")


def test_create_struct_bytes_no_len():
    # bytes without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: Bytes
    assert_missing_config_error(exc_info, "Len")


def test_create_struct_bytes_exact():
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


def test_create_struct_bytes_explicit_min():
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


def test_create_struct_bytes_ignore_with_min():
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


def test_create_struct_bytes_ignore():
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

def test_create_struct_string_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[String, Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), StringField)
    assert_general_field_checks(f, str, "some_field", True, False, "5s", 1, 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    inst = TestStructure(some_field="Hihi")    # valid string
    assert type(inst.some_field) is str
    assert inst.some_field == "Hihi"

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field="Hihihi")   # too long
    assert_validation_error(exc_info, "string_too_long", "Hihihi")


def test_create_struct_string_no_len():
    # string without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: String
    assert_missing_config_error(exc_info, "Len")


def test_create_struct_string_exact():
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


def test_create_struct_string_explicit_min():
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


def test_create_struct_string_ignore_with_min():
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


def test_create_struct_string_ignore():
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


## Padding tests ##

def test_create_struct_padding_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[Padding, Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), PaddingField)
    assert_general_field_checks(f, type(None), "some_field", True, False, "5x", 0, 5)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)

    inst = TestStructure()    # not required
    assert inst.some_field is None

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field="Hihihi")   # need none to init
    assert_validation_error(exc_info, "none_required", "Hihihi")


def test_create_struct_padding_no_len():
    # padding without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: Padding
    assert_missing_config_error(exc_info, "Len")


## Array testing ##

def test_create_struct_array_default():
    class TestStructure(BaseStruct):
        some_field: Annotated[ArrayList[Uint16], Len(5)]
    
    assert isinstance(f := TestStructure.struct_fields.get("some_field"), ArrayField)
    assert_general_field_checks(f, list, "some_field", True, False, "HHHHH", 5, 10)
    # check that the pydantic length constraint for max is present but not min by default
    assert any((m.max_length == 5 if isinstance(m, annotated_types.MaxLen) else False) for m in f.annotation_metadata)
    assert not any(isinstance(m, annotated_types.MinLen) for m in f.annotation_metadata)
    
    # array element has to be a non-top-level integer field
    assert isinstance(el := f.element_field, IntegerField)
    assert_general_field_checks(el, int, "some_field.__element__", False, False, "H", 1, 2)

    inst = TestStructure(some_field=(1, 2, 3))    # should coerce to list
    assert type(inst.some_field) is list
    assert inst.some_field == [1, 2, 3]
    assert type(inst.some_field[0]) is int

    with pytest.raises(pydantic.ValidationError) as exc_info:
        inst = TestStructure(some_field=[1, 2, 3, 4, 8, 9])   # too long
    assert_validation_error(exc_info, "too_long")


def test_create_struct_array_no_len():
    # string without length must fail
    with pytest.raises(TypeError) as exc_info:
        class TestStructure(BaseStruct):
            some_field: ArrayList[Uint16]
    assert_missing_config_error(exc_info, "Len")


def test_create_struct_array_exact():
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


def test_create_struct_array_explicit_min():
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


def test_create_struct_array_ignore_no_filler():
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


def test_create_struct_array_ignore_with_filler():
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

# TODO: test array of arrays
# TODO: test big struct with all fields packing and unpacking with binary verification

def atest_create_struct_invalid_enum():
    class BaseMsg(BaseStruct):
        #model_config = StructConfigDict(extra="forbid")
        model_config = StructConfigDict(
            byte_order="big-endian", 
            extra="forbid"
        )

        mtype: EnumU8[KnownGoodEnumUnsigned]
        local_timestamp_abs: Uint32
        missed_messages: Uint16
        b: Annotated[String, Len(9)]
        c: Annotated[Bytes, Len(2)]
        pad1: Annotated[Padding, Len(4)]
        compf_outlet: Float32
        msgs: Annotated[ArrayFrozenSet[
                Annotated[ArrayTuple[
                    Uint8
                ], Len(3), Filler(5)]
            ], Len(5), Filler()]

        @pydantic.computed_field
        def compf(self) -> float:
            return 0.6

#class OtherMsg(BaseMsg):
#    data: Annotated[list[int], pydantic.Field(default_factory=lambda: [1, 2])]
#
#    @pydantic.field_serializer("data")
#    def data_ser(self, dt: list[int], _info):
#        return ", ".join([str(d) for d in dt])
#
#if __name__ == "__main__":
#    OtherMsg.__init__.__annotations__ = {"ho": str}
#    my_instance = OtherMsg(
#        mtype=MsgType.STARTUP_INFO,
#        local_timestamp_abs=2,
#        missed_messages=65535,
#        b="heyanot",
#        c="as",
#        msgs=[[90, 18, 5], [1, 2], [1, 4], [9, 8]],#, maxlen=5),
#        data=[7, 8, 519]
#    )
#    #my_instance.msgs.append((5,198,81,8))
#    #my_instance.msgs.append((5,24))
#    #my_instance.msgs.append((9,50))
#    print(my_instance.model_validate)
#    print(my_instance.model_dump_json())
#    print(elem := my_instance.struct_dump_elements())
#    print(bt := my_instance.struct_dump_bytes())
#    print(OtherMsg.struct_validate_elements(elem))
#    print(OtherMsg.struct_validate_bytes(bt))
#    print(OtherMsg.__bindantic_struct_code__)
#    print(OtherMsg.__bindantic_byte_consumption__)
#    print(len(my_instance.struct_dump_bytes()))
#    
#
