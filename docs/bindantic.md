# bindantic

Bindantic is an unofficial "extension" (one could call it a "mod") for the popular [pydantic](https://docs.pydantic.dev/latest/) data validation library.
It that adds support for defining, dumping and validating binary data structures (like in C/C++) while maintaining all pydantic features, meaning that data can be easily converted between JSON, Python and binary.

This is extremely useful for efficient communication with systems programmed in C or C++ such as microcontrollers, over protocols like serial, where JSON might not be a viable solution both in terms of information density, transfer speed, processing power and memory limitation.


## The principles

Bindantic introduces the concept of *"Structs"* (data structures). A bindantic *Struct* is the equivalent of a pydantic *Model*. A *Struct* defines the layout of data in binary form, the same way that structs work in C.

In Bindantic, a *Struct* is defined by creating a class with ```bindantic.BaseStruct``` as its superclass, the same way you would create a pydantic *Model* by inheriting from ```pydantic.BaseModel```. 

> [!NOTE] 
> ```bindantic.BaseStruct``` is an EXTENSION of the ```pydantic.BaseModel``` and actually inherits from it. Therefor, bindantic *Structs* can do everything a pydantic *Model* can do as well as a few extra features.
> 
> See [src/el/bindantic/_base_struct.py](../src/el/bindantic/_base_struct.py):
> ```python
> #...
> class BaseStruct(pydantic.BaseModel, metaclass=StructMetaclass):
>     """
>     Pydantic BaseModel that also adds support for binary packing and unpacking
>     """
> #...
> ```

After defining a *Struct*, you can use the provided helper types to lay out the structure just like in C/C++:

```c
struct my_structure_t
{
    uint32_t field1;
    int8_t field2;
    char field3[8];
};

// assert(sizeof(my_structure_t) == 13)
```

Bindantic equivalent:

```python
import el.bindantic as bin
from typing import Annotated

class MyStructure(bin.BaseStruct):
    field1: bin.Uint32 = 0x56
    field2: bin.Int8
    field3: Annotated[bin.String, bin.Len(8)]

assert MyStructure.__bindantic_byte_consumption__ == 13 # This attribute defines how many bytes the structure needs
```

Although these fields look like they have weird datatypes any you may fear that they behave weirdly, but fear not, because all these shortcut types provided by pydantic are actually just type aliases to the standard python type with some metadata added using ```typing.Annotated```. For example, this is what a Uint32 looks like under the hood:

```python
Uint32 = Annotated[int, IntegerField(4, "I", False), IntegerField.range_limit(False, 32)]
```

As per [definition in the standard](https://docs.python.org/3/library/typing.html#typing.Annotated), type checkers treat annotated types the same way as their underlying type, in this case ```int```. The extra metadata is then used at runtime to deduce how fields are arranged in binary form (or in JSON when using pydantic functions).

As demonstrated by teh string field, sometimes it is necessary to provide extra metadata such as the length of a string (represented as char[] in the structure). To do so, bindantic provides handy helper functions such as ```bindantic.Len``` that can be used together with ```typing.Annotated``` to configure the field further.

Once a structure is defined, you can instantiate it with full IntelliSense support and data validation, just like pydantic. Bindantic already applies basic constraints to fields where it makes sense, such as limiting numbers to the allowed range for the specified binary integer type (as evident in the code excerpt above).

```python
inst = MyStructure(
    # field1 is omitted and filled with default value
    field2=5,
    field3="Hello"
)
assert isinstance(inst.field1, int)
assert isinstance(inst.field2, int)
assert isinstance(inst.field3, str)
assert inst.field1 == 0x56
assert inst.field2 == 5
assert inst.field3 == "Hello"


inst = MyStructure(
    # field1 is omitted and filled with default value
    field2=278,     # ValidationError: field2 must be less than or equal to 255
    field3="Hello"
)
```

All of this can also be done with pydantic on its own, but now we can also convert this field to binary:

```python 
as_json = inst.model_dump_json()    # converting to JSON is pydantic feature
as_bytes = inst.struct_dump_bytes() # bindantic exclusive

assert as_bytes == b"\0\0\0\x56\x05Hello\0\0\0" # assuming big-endian byte order
```

And then unpack and validate it back into a python object:

```python 
as_python_from_json = MyStructure.model_validate_json(as_json)      # pydantic feature
as_python_from_bytes = MyStructure.struct_validate_bytes(as_bytes)  # bindantic exclusive

assert as_python_from_json == as_python_from_bytes

assert isinstance(as_python_from_bytes.field1, int)
assert isinstance(as_python_from_bytes.field2, int)
assert isinstance(as_python_from_bytes.field3, str)
assert as_python_from_bytes.field1 == 0x56
assert as_python_from_bytes.field2 == 5
assert as_python_from_bytes.field3 == "Hello"

```

If any value is not allowed or couldn't be parsed for any other reason, either a ```pydantic.ValidationError``` or a ```bindantic.StructPackingError``` will be raised.


## ConfigDict and byte order

Integers spanning over multiple bytes can be arranged differently in memory. This is called byte-order or "endianness". How they are arranged depends on the underlying CPU architecture. By default, bindantic uses the byte order native to your CPU. 

You can however change that by specifying the byte order in the pydantic ```model_config``` field, which has been extended in bindantic to be of type ```bindantic.StructConfigDict```. This is again just an EXTENSION of ```pydantic.ConfigDict``` which adds the ```byte_order``` attribute.

```python
class TestStructure(BaseStruct):
    model_config = StructConfigDict(byte_order="big-endian")
    ...
```

All other config options relevant for pydantic are still available and working in the ```bindantic.StructConfigDict```.

The byte order attribute is typed as a literal and provides the following options:
- "native-aligned"
- "native"
- "little-endian"
- "big-endian"
- "network"

> [!WARNING]
> The "native-aligned" option additionally adds some byte alignment rules that are required for some fields and some architectures. These rules are again platform dependant and not handled by bindantic. Using this option is generally discouraged as it can lead to unexpected byte consumption changes and weird errors. When required, explicitly add alignment padding bytes using the ```bindantic.Padding``` type.


## Other supported field types

While there is not a full write up about every supported field type, here is a list of all the types that can be used and some examples. If you are looking for a specific use case, you can look in the [tests/test_bindantic.py](../tests/test_bindantic.py) file which shows many different use cases and error cases.


### Integer types

Underlying python type: ```int```

```python
class MyStructure(bin.BaseStructure):
    field1: bin.Uint8
    field2: bin.Uint16
    field3: bin.Uint32
    field4: bin.Uint64
    field5: bin.Int8
    field6: bin.Int16
    field7: bin.Int32
    field8: bin.Int64
```


### Enumerations

Supported underlying python types:
- ```enum.Enum```
- ```enum.IntEnum```
- ```enum.Flag```
- ```enum.IntFlag```

Not supported:
- ```enum.StrEnum```

```python
import enum

class MyE(enum.Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

class MyStructure(bin.BaseStructure):
    field1: bin.EnumU8[MyE]
    field2: bin.EnumU16[MyE]
    field3: bin.EnumU32[MyE]
    field4: bin.EnumU64[MyE]
    field5: bin.Enum8[MyE]
    field6: bin.Enum16[MyE]
    field7: bin.Enum32[MyE]
    field8: bin.Enum64[MyE]
```

Enums are properly validated and will be converted to and from integers both in JSON and binary.


### Floating point numbers

Underlying python type: ```int```

```python
class MyStructure(bin.BaseStructure):
    field1: bin.Float32     # float
    field2: bin.Float64     # double
```


### Characters

Underlying python type: ```str```

```python
class MyStructure(bin.BaseStructure):
    field1: bin.Char
```


### Boolean

Underlying python type: ```bool```

```python
class MyStructure(bin.BaseStructure):
    field1: bin.Bool
```

> [!NOTE]
> Booleans are 1 byte in size as is standard. When wanting to use bits directly, use enums with ```enum.Flag``` or ```enum.IntFlag``` types or resort to manual integer bit manipulation


### Strings

Underlying python type: ```str```

```python
from typing import Annotated

class MyStructure(bin.BaseStructure):
    field1: Annotated[bin.String, bin.Len(10)]
```

Strings represent char arrays in C. The length of the array in bytes is specified using the ```bindantic.Len()``` annotation. 

By default, their length is limited by pydantic to the length specified in the Len() annotation. To define a minimum size or disable the constraints, see the doc-comments of ```bindantic.Len()```.


#### Termination

Strings don't have to be null terminated when they are limited to the size of the string field. When a string field is 15 bytes in size and a 15 character string is passed to it, all 15 bytes will be filled (assuming a 1Char=1Byte encoding). There is therefore no guaranteed null termination. If however the string is smaller than the size of the field, the rest of the bytes are filled with zeros.

When unpacking a string from bytes, all characters up to but not including the first null character are read into the string. The rest is discarded. If there is no null character, all bytes until the end of the field according to the specified size are read.

#### Encoding

One can use the ```bin.Encoding()``` annotation to specify the encoding to be used. The default is "utf-8".

> [!IMPORTANT]
> When using Multi-byte per character encodings, the string length in bytes is not properly validated by pydantic because it is not possible to know in advance how many bytes such a string might consume. Pydantic will limit the amount of characters to the specified length, while the bindantic interprets the length as the number of BYTES to reserve in the structure. When the string ends up too long, it is truncated to fit. It might even be truncated in the middle of a multi-byte character.


### Bytes

Underlying python type: ```bytes```

```python
from typing import Annotated

class MyStructure(bin.BaseStructure):
    field1: Annotated[bin.Bytes, bin.Len(10)]
```

Bytes are similar to Strings, but you could say that they represent uint8_t arrays in C. The length of the array in bytes is specified using the ```bindantic.Len()``` annotation. 

By default, their length is limited by pydantic to the length specified in the Len() annotation. To define a minimum size or disable the constraints, see the doc-comments of ```bindantic.Len()```.


#### Difference to Strings

Unlike strings, bytes represent the raw array of bytes in the structure. When the ```bytes``` object specified is shorter than the amount of bytes that fit in the structure, the remaining bytes are filled with zeros. When unpacking from binary, all bytes representing the reserved space are returned in the ```bytes``` object, including the Zeros. Zeros don't have any special meaning for ```bindantic.Bytes```.

Bytes have no encoding, as they return and are fed with raw data.


### Padding

Underlying python type: ```None```

```python
from typing import Annotated

class MyStructure(bin.BaseStructure):
    field1: bin.Uint8
    pad_xyz: Annotated[bin.Padding, bin.Len(10)]
    field2: bin.Uint8
```

Padding represents a fixed number of free bytes in the structure that are left empty. The following fields are therefore shifted down by the length of the padding. These padding bytes are not converted to or from any python object and thus the ```pad_xyz``` field is always ```None```. 

Although IntelliSense shows the field when constructing an instance, it does not need to and should not be specified and is also not required or exported when validating or dumping JSON.

While the field is practically invisible, it does need a unique name that DOES NOT start with an underscore because pydantic needs to recognize it as a field.


### Arrays

Underlying python types: 
- ```bindantic.ArrayList```: ```list```
- ```bindantic.ArrayTuple```: ```tuple```
- ```bindantic.ArraySet```: ```set```
- ```bindantic.ArrayFrozenSet```: ```frozenset```
- ```bindantic.ArrayDeque```: ```collections.deque```

```python
from typing import Annotated

class MyStructure(bin.BaseStructure):
    field1: Annotated[bin.ArrayList[Uint8], bin.Len(5), bin.Filler()]
    field2: Annotated[bin.ArrayTuple[Uint8], bin.Len(5), bin.Filler()]
    field3: Annotated[bin.ArraySet[Uint8], bin.Len(5), bin.Filler()]
    field4: Annotated[bin.ArrayFrozenSet[Uint8], bin.Len(5), bin.Filler()]
    field5: Annotated[bin.ArrayDeque[Uint8], bin.Len(5), bin.Filler()]
```

Arrays directly represent C arrays and are simply a fixed-length sequence of an arbitrary binary capable datatype. They are in principle similar to a list.

Bindantic provides shortcuts for converting these arrays into some common python representations depending on the use case.

#### Filler

The ```bindantic.Filler()``` annotation allows you to specify the value to fill empty array elements with if the python object contains less elements than fit in the array. When specifying ```bindantic.Filler``` with no arguments, array elements are created using their default constructor.

If no filler is specified, the python list MUST be exactly the length that fits in the array, otherwise a StructPackingError is raised.

Example of filling empty elements with "5": ```bindantic.Filler(5)```

When unpacking from binary, there are multiple options to handle the filler values. When no filler is specified, all array values are taken as is (empty values might for example have a binary value of zero) and fed to the initializer of the corresponding python type, such as list or set. This has the expected effect depending on the type, for example when using an ```ArraySet```, duplicate elements are automatically removed and the order might not be guaranteed.

If a filler is specified, filler elements by default are handled differently depending on the underlying datatype. If the behavior is not desired, it can be changed with additional arguments to ```bindantic.Filler```. See it's doc-string for details.


### Nested structures

It is possible to use one structure as a field of another structure or anywhere else a field can be specified, such as an array element, just like in pydantic. It is possible to nest structures indefinitely.


```python
class InnerStructure(bin.BaseStructure):
    field1: bin.Uint32
    field2: bin.Uint64
    field3: bin.Int8

class MyStructure(bin.BaseStructure):
    field1: bin.Uint32
    field2: InnerStructure
    field3: bin.Int8
```

The structure will take up exactly the amount of bytes that it would if the elements where inlined into the outer structure. Internally, the structure is represented as a field that takes up that specific number of bytes. After unpacking, these bytes are fed to the nested structure to unpack again and so on.

The resulting behavior works the same as expected and as it does with pydantic.
These nested structures can also still be used for JSON validation and serialization just like with pydantic.


### Literals

Some types can be used as Literals which will be enforced, and can be used for discrimination, just as with pydantic.

```python
from typing import Annotated, Literal
import enum

class MyE(enum.Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

class MyStructure(bin.BaseStructure):
    field1: bin.EnumU8[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field2: bin.EnumU16[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field3: bin.EnumU32[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field4: bin.EnumU64[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field5: bin.Enum8[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field6: bin.Enum16[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field7: bin.Enum32[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field8: bin.Enum64[Literal[MyE.SECOND, MyE.THIRD]] = MyE.SECOND
    field1: bin.LitU8[Literal[4, 5]] = 5
    field2: bin.LitU16[Literal[4, 5]] = 5
    field3: bin.LitU32[Literal[4, 5]] = 5
    field4: bin.LitU64[Literal[4, 5]] = 5
    field5: bin.Lit8[Literal[4, 5]] = 5
    field6: bin.Lit16[Literal[4, 5]] = 5
    field7: bin.Lit32[Literal[4, 5]] = 5
    field8: bin.Lit64[Literal[4, 5]] = 5
    field1: bin.LitChar[Literal["2"]] = "2"
    field1: Annotated[bin.LitString[Literal["HiHi"]], Len(5)] = "HiHi"
```

Literals can have multiple options but they have to be of the same type. Literals can have a default value, which is often used for discriminators that you don't want to assign manually.

String literal values must take up no more than the length of the string field.

Enum literals can use any of the supported enum base types. When invalid enum values are unpacked, that error is caught and raised as a StructPackingError. If the found value is a valid enumeration but not the correct literal value, a ValidationError is raised just like with pydantic.

> [!NOTE]
> While bindantic properly supports all enums as literals, unfortunately pydantic does not properly support ```enum.Enum``` or ```enum.Flag``` when validating from JSON or when validating from python when inputting the enumeration value as numbers. This is because pydantic does not convert the incoming integer value to the enumeration type before checking if it matches the Literal values. To circumvent this issue, you can use the ```enum.IntEnum``` and ```enum.IntFlag``` variants which are subclasses of int and are therefore directly equal to the value integer.


### Unions

It is possible to define a union of multiple data-types that are overlaid and take up the same bytes, just like in C/C++.
Unlike pydantic, unions in bindantic can only contain substructures, not arbitrary field.

```python
from typing import Union

class InnerStructureA(bin.BaseStructure):
    field1: bin.LitU8[Literal[4]] = 4
    field2: bin.Uint64
    field3: bin.Int8

class InnerStructureB(bin.BaseStructure):
    field4: bin.LitU8[Literal[3, 5]] = 5
    field5: bin.Int8
    field6: bin.Uint64

class MyStructure(bin.BaseStructure):
    union_field: Union[InnerStructureA, InnerStructureB]
```

The union field takes up as many bytes as required by the larges union member. When packing an inner structure type which takes up less than that maximum number of bytes, the reset are filled with zeros.

When unpacking a union field from binary, bindantic attempts to find the correct matching inner structure for the binary data using one of two discrimination methods, similar to pydantic:

- Left to right mode: Bindantic attempts to validate the binary data reserved for the union with each of the union types from left to right order, returning the first one that doesn't result in an unpacking or validation error. This works the same as the equally named pydantic discrimination mode and is the bindantic default. Be aware though that as of writing, the default mode for pydantic has been changed to smart, which doesn't exist for bindantic though the behavior in most sensible scenarios should not differ.
- discriminated mode: The pydantic.Discriminator() annotation is used to specify a field in the substructures that is exclusively used to differentiate between the members. This also works the same for pydantic. 
  - Note that internally, this only unpacks the bytes to dict according to the correct type (all are attempted from left to right until the matching one is found) and still lets pydantic discriminate to the correct python type. 
  - Unlike for JSON data, this doesn't help that much with performance for binary unpacking because it might still be necessary to unpack up to all of the structure types before finding the matching one, because data isn't already provided as a dict-like object. 
  - Note that the discriminator has to be a hard-coded field, Bindantic does not support the use of tagging and callable discriminators.
  - Unlike pydantic, bindantic does fully and properly support the use of enum literals as discriminators. When creating the structure, the enum type of the literal value is determined and stored as the type of the variable. When unpacking from binary, the field is post-processed in to that enum type so that pydantic can then properly constrain it to the enum values. Unfortunately, when validating JSON, pydantic doesn't convert enum values to enums when used in literals and enum literal fields can therefore not be properly parsed from json without a custom validator. (though they can be dumped to JSON just fine). Validating python is possible but it is required to use the literal enum directly, not just the value of the enumeration.


#### Uniqueness of substructures

Unlike in C, in python it is not possible to access the bytes of the union interpreted as two different structures. When unpacking from bytes, python has to detect the correct datatype (substructure) to use to represent the bytes and then instantiate that type, using the algorithms described above.

When doing this from JSON, it is easily possible to look up a special discriminator field to identify the correct type. In binary however, non of the bytes mean anything before they have been unpacked and certain bytes parsed into certain fields. This can cause problems with uniqueness. When no discriminator is used what so ever, it is quite likely that every single struct type can validate the bytes, even though the resulting data might not make any sense. 

Therefore it is recommended to have at least one field in each structure that is constrained to a unique value using a literal type, so that validation fails if the field doesn't have that exact specified value. This can then also be used explicitly as the discriminator, which allows the library to explicitly look at this value and use the matching union member even if another field fails validation, which would the be reported as an error instead of trying the next member.

One problem is left though, and that is that if in the binary position where one union member contains the discriminator, another contains some other arbitrary data which just by chance might match another structures discriminator value. To avoid this issue, it is strongly recommended that every union member has an equally named discrimination member with unique value that is in THE SAME BINARY LOCATION on every member, ideally the first field in the structure. This way, discrimination mistakes are not possible.


### Outlets and computed fields

Computed fields are not directly supported in bindantic because it is not possible to determine the location of the decorated function in the class. Instead, an additional outlet field named ```[computed]_outlet``` (where [computed] is to be replaced with the name of the computed field) has to be defined in the place where the computed value should end up at. These fields must also be of type ```bindantic.Outlet[bin.Uint16]``` where ```bin.Uint16``` is an example for the real field datatype. This is required so that these outlet fields are excluded from the pydantic dump and have a default value of None so they don't need to be initialized when validating from JSON or Python. They MUST NOT have a leading underscore, as those items are not counted as fields by pydantic and we need pydantic to detect them so the order is known. When unpacking from a binary structure, the bytes occupied by the computed field are simply ignored, as the value is defined by the computed field property.

```python
class MyStructure(bin.BaseStructure):
        some_field: bin.Uint16
        double_outlet: bin.Outlet[bin.Uint16]

        @pydantic.computed_field
        def double(self) -> bin.Uint16:
            return self.some_field * 2
```

> [!IMPORTANT]
> The actual name of the field is determined by the function name of the computed property. The name of the outlet MUST have the above described structure, otherwise it is not detected as an outlet. Each defined outlet MUST also have an accompanying computed field that returns the same type as the outlet, otherwise an error will be raised during definition. 