# Bindantic notes

- Fields are arranged in the struct according to the order of fields in the class. Fields of base classes are arranged before the fields in the class and in the order of the base classes.
- Just like with regular pydantic, attributes with leading underscores are considered private and are excluded from the structure. They do not use up any bits.
- Padding variables are excluded from pydantic serialization by setting them to excluded. They still have an effect as padding bytes
- computed fields are not directly supported because it is not possible to get both normal fields and properties (functions/descriptors) in one list in correct order. Instead, an additional field of type "ComputedOutlet" has to be defined, which is named "[computed]_outlet" where [computed] is to be replaced with the name of the computed field. These fields are excluded from pydantic dump and have a default value of None so they don't need to be initialized when validating using pydantic. They MUST NOT have a leading underscore, as those items are not counted as fields by pydantic and we need pydantic to detect them so the order is known. When unpacking from a binary structure, the bytes occupied by the computed field are simply ignored, as the value is defined by the computed field property.


# ToDo

- Add support for bitfields (fields aligned at bit level)
- Add support for nested structures
- Add support for byte order config
- Add support for arbitrary iterable types in arrays