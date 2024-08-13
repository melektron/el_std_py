"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
07.08.24, 08:44
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Configuration objects for fields. These work similar
to the standard library annotation types, just specialized for
bindantic.
"""

import typing
from ._deps import pydantic_core, pydantic, annotated_types
if typing.TYPE_CHECKING:
    from ._fields import BaseField


BindanticUndefinedType = pydantic_core.PydanticUndefinedType
BindanticUndefined = pydantic_core.PydanticUndefined

type ByteOrder = typing.Literal[
    "native-aligned",
    "native",
    "little-endian", 
    "big-endian", 
    "network"
]

class StructConfigDict(pydantic.ConfigDict, total=False):
    """
    Extension of pydantics ConfigDict adding struct specific 
    options.
    """

    byte_order: ByteOrder
    """
    What byte order and alignment should be used when packing and unpacking structs.
    If native alignment is required, use "native-aligned" which will use both native
    byte order and alignment the the current systems CPU.
    All other options have no alignment and pack the structure as closely as possible.
    It is recommended to add padding manually if required.
    The default option is "native" which means the system native byte order but no alignment.
    "network" byte order is the same as "big-endian".
    
    See Python doc's for details: https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment
    """


"""
== Bindantic struct field configuration ==

Bindantic needs to have the ability to configure options for fields.
Some of the options have to work together with existing Pydantic features
while some are exclusive to Bindantic structs.

For this reason, there Bindantic defines config functions that return a 
config info object that can then be parsed during model creation (similar
to the pydantic.Field()).

Unlike Pydantic, Bindantic only supports configuration via annotation, not via
attribute assignment, although some options might still work with assignment
because they use Pydantic FieldInfo in the background which is parsed by Pydantic.

The Bindantic config functions only serve one purpose each, so you may have to combine
multiple functions to reach the desired configuration.
Some of these function which also have an effect on existing pydantic features return
pydantic.FieldInfo. Those are simply a shortcut for a common config required for binary
structs. 
Others return an instance of a subclass of bindantic.FieldConfigItem. These options
are specific to Bindantic and are parsed by Bindantic itself (Pydantic is still responsible
for metadata collection)

Internally during struct construction, all metadata is read through and all FieldConfigItems
and other elements that are pydantic compatible are read out and converted into FieldConfigItems
that are stored in the FieldConfigOptions instance of each field.
"""


class FieldConfigItem[VT]:
    def __init__(self, value: VT) -> None:
        super().__init__()
        self.value = value
    pass


class LenInfo(FieldConfigItem[int]):
    pass

class EncodingInfo(FieldConfigItem[str]):
    pass

class DiscriminatorInfo(FieldConfigItem[str]):
    pass

@typing.final
class FillDefaultConstructor:
    pass

FillerParseMode = typing.Literal["auto", "strip-leading", "strip-trailing", "strip-both", "remove", "keep"]

class FillerInfo(FieldConfigItem[tuple[typing.Any | type[FillDefaultConstructor], FillerParseMode]]):
    def __init__(self, value: typing.Any | type[FillDefaultConstructor], parse_mode: FillerParseMode) -> None:
        super().__init__((value, parse_mode))


def Len(val: int, *, min: int | typing.Literal["same"] = 0, ignore: bool = False) -> pydantic.fields.FieldInfo | LenInfo:
    """
    Length for Array, String, Bytes, Padding.
    This specifies how many elements the array must be able to hold. The structure
    will always contain enough space to hold this maximum amount of elements.

    By default, this also specifies the maximum size for pydantic, meaning that arrays
    greater than this size will cause a validation error. 
    
    If 'min' is set to a value other than 0, a minimum size for pydantic is defined causing pydantic to 
    raise a validation error for any sequences shorter than the full array/string size. If set to
    "same", 'val' will be used as the minimum, effectively enforcing the sequence to have the exact specified
    size.

    If the 'ignore' option is set to True,
    this behavior is disabled and pydantic will not enforce any length requirements when validating.
    In this case, the 'min' option has no effect.
    When packing, too long sequences will be truncated to fit in the structure.

    Params:
        val: length of the binary sequence in number of elements
        min: optional minimum sequence length
        ignore: whether to ignore length requirements during validation
    """
    if ignore:
        return LenInfo(val)
    elif min == 0:
        return pydantic.Field(max_length=val)
    else:
        return pydantic.Field(max_length=val, min_length=(val if min == "same" else min))

def Encoding(val: str) -> EncodingInfo:
    """
    String encoding
    """
    return EncodingInfo(val)

def Filler(
    val: typing.Any | type[FillDefaultConstructor] = FillDefaultConstructor,
    parse_mode: FillerParseMode = "auto",
) -> FillerInfo:
    """
    Filler value for shorter arrays. FillDefaultConstructor
    will use the the default constructor with no parameters for filling.

    The "parse_mode" option configures how fillers are handed
    when postprocessing the array after unpacking. There are three options:
     - "strip-leading": removes leading filler values from the output type. Not recommended for lists, but may be useful for queues
     - "strip-trailing" (default for sequence types including queues): removes trailing filler values from the output type
     - "strip-both": removes leading and trailing filler values form the output type. Not recommended for arrays, but may be useful for queues
     - "remove" (default for set types): removes all fillers from the output type (even amidst valid values). Be careful when 
         using this with list or tuple arrays because indexes may be shifted. This is mostly intended for sets.
     - "keep" (default without filler specified): keeps all values when parsing, even fillers.
    
    When selecting "auto" (default) the setting is chosen according to type as described above
    """
    return FillerInfo(val, parse_mode)


class FieldConfigOptions:
    """
    Internal class used by bindantic fields to access config options
    """
    def __init__(self) -> None:
        self.items: dict[type[FieldConfigItem], FieldConfigItem] = {}
    
    def set_from_item(self, config_item: FieldConfigItem) -> None:
        self.items[type(config_item)] = config_item
    
    def set_from_metadata(self, metadata: typing.Iterable[typing.Any]) -> None:
        """
        extracts all available configuration items from annotation metadata.
        The annotation metadata should already be collected by pydantic so that
        it contains pre-processed values used by pydantic.
        """
        for meta_element in metadata:
            match meta_element:

                # config items passed directly as annotation
                case FieldConfigItem():
                    self.set_from_item(meta_element)

                # maximum length (from pydantic) defines the binary length.
                case annotated_types.MaxLen():
                    self.set_from_item(LenInfo(meta_element.max_length))
                
                # union discriminator (from pydantic)
                case pydantic.Discriminator():
                    self.set_from_item(DiscriminatorInfo(meta_element.discriminator))
    
    def get_with_error[VT](self, field: "BaseField", opt: type[FieldConfigItem[VT]], default: VT | BindanticUndefinedType = BindanticUndefined) -> VT:
        """
        Gets the value of a specific config options if it was passed, a default if not
        and throws an error if no default available.
        """
        if opt in self.items:
            return self.items[opt].value
        elif default is not BindanticUndefined:
            return default
        else:
            raise TypeError(f"'{field.__class__.__name__}' '{field.field_name}' is missing required config option: '{opt.__name__.removesuffix("Info")}'")


class StructPackingError(Exception):
    """
    Error when packing or unpacking structure data and
    preprocessing/postprocessing it into python objects.
    """
    pass