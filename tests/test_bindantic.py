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
from collections import deque
from typing import Annotated
from el.bindantic import *
import typing


@pytest.fixture
def enums():
    class MsgType(enum.Enum):
        STARTUP_INFO = 0
        TIMEBASE_ADJUST = 1
        ROLE_CONFIGURED = 2
        TRANSMISSION_ERROR = 3
        SYNC_LISTEN_START = 4
        SYNC_LISTEN_TIMEOUT = 5
        SYNC_LISTEN_PACKET_DISCARD = 6
        SYNC_RECEIVED = 7
        SYNC_SEND = 8
        SYNC_RESP_LISTEN_START = 9
        SYNC_RESP_LISTEN_TIMEOUT = 10
        SYNC_RESP_LISTEN_PACKET_DISCARD = 11
        SYNC_RESP_RECEIVED = 12
        SYNC_RESP_SEND = 13
        EVAL_DATA_LISTEN_START = 14
        EVAL_DATA_LISTEN_TIMEOUT = 15
        EVAL_DATA_LISTEN_PACKET_DISCARD = 16
        EVAL_DATA_RECEIVED = 17
        EVAL_DATA_SEND = 18


    class DiscardReason(enum.Enum):
        DISCARD_UNKNOWN = 0
        DISCARD_AWAIT_NAK = 1
        DISCARD_AWAIT_E_SIZE = 2
        DISCARD_AWAIT_ERR = 3
        DISCARD_WRONG_TYPE = 4
        DISCARD_WRONG_SIZE = 5


    class TxError(enum.Enum):
        TX_ERR_UNKNOWN = 0
        TX_ERR_START_BUSY = 1
        TX_ERR_AWAIT_NAK = 2
        TX_ERR_AWAIT_TIMEOUT = 3
        TX_ERR_AWAIT_ERR = 4


#class PersonInfo(binobj.Struct):
#    first_name = binobj.fields.StringZ(encoding="utf-8")
#    first_name = binobj.fields.StringZ(encoding="utf-8")
#    phone_numbers = binobj.fields.Array(binobj.fields.StringZ(encoding="utf-8"), count=2)
#
#a = PersonInfo()
#a.phone_numbers

# Base class that will process annotations
class TestStruct:
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._field_metadata = {}
        
        # Iterate through the annotations and process them
        for name, annotation in cls.__annotations__.items():
            print(f"hint: {name=}, {annotation=}")
            if typing.get_origin(annotation) is Annotated:
                print(f"{annotation.__metadata__}=")
                actual_type, metadata = typing.get_args(annotation)
                print(f"{actual_type=}, {metadata=}")
                if isinstance(annotation, tuple) and len(annotation) == 2:
                    actual_type, metadata = annotation
                    if isinstance(metadata, dict) and "length" in metadata:
                        cls._field_metadata[name] = metadata
                    # Set the actual type to the field's type (e.g., str for ZString)
                    setattr(cls, name, actual_type)
    
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            if name in self._field_metadata:
                length = self._field_metadata[name]["length"]
                if len(value) != length:
                    raise ValueError(f"{name} must be {length} characters long")
            setattr(self, name, value)


class BaseMsg(BaseStruct):
    #model_config = StructConfigDict(extra="forbid")
    model_config = StructConfigDict(
        byte_order="big-endian", 
        extra="forbid"
    )

    mtype: EnumU8[MsgType]
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

class OtherMsg(BaseMsg):
    data: Annotated[list[int], pydantic.Field(default_factory=lambda: [1, 2])]

    @pydantic.field_serializer("data")
    def data_ser(self, dt: list[int], _info):
        return ", ".join([str(d) for d in dt])

if __name__ == "__main__":
    OtherMsg.__init__.__annotations__ = {"ho": str}
    my_instance = OtherMsg(
        mtype=MsgType.STARTUP_INFO,
        local_timestamp_abs=2,
        missed_messages=65535,
        b="heyanot",
        c="as",
        msgs=[[90, 18, 5], [1, 2], [1, 4], [9, 8]],#, maxlen=5),
        data=[7, 8, 519]
    )
    #my_instance.msgs.append((5,198,81,8))
    #my_instance.msgs.append((5,24))
    #my_instance.msgs.append((9,50))
    print(my_instance.model_validate)
    print(my_instance.model_dump_json())
    print(elem := my_instance.struct_dump_elements())
    print(bt := my_instance.struct_dump_bytes())
    print(OtherMsg.struct_validate_elements(elem))
    print(OtherMsg.struct_validate_bytes(bt))
    print(OtherMsg.__bindantic_struct_code__)
    print(OtherMsg.__bindantic_byte_consumption__)
    print(len(my_instance.struct_dump_bytes()))
    

