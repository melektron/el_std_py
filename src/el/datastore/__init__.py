"""
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
10.08.23, 23:28
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Non-volatile data storage systems with human readable
and editable JSON storage format.

This module contains multiple data storage systems.

## Datastore

The datastore is sort of an ORM for a pseudo-database,
but with file paths and json objects instead of tables. 

Data is stored relative to a datastore root file path 
(configured with `set_datastore_root()`) on disk.
In other parts of the datastore, locations are referenced
using datastore paths, which are just lists of strings and
loosely map to folder/file names (but not directly due
to sanitization).

Each Entity (defined using `@specialized_file()` on a 
default-constructable pydantic model) can
be assigned a base path, which can be thought of as
it's "table name". You can organize the paths so the 
hierarchy on disk makes sense for your data structure.

Whenever an entity (specialized file) is instantiated,
a further datastore path can be passed to the initializer. 
This can be thought of as the primary key, and is the only
way to identify and query for a specific datastore "file".
The instance is called a single datastore "file", which more 
or less maps to an actual file on disk. If the identified 
file exists, it is opened and parsed, otherwise a new
one is created. Either way, the developer will not have to
think about it, they can just start using and setting the data.
The datastore will automatically save changes to disk periodically.
When multiple instances with the same path are created, they act as 
singletons, with only a single instance representing them both.

## SavableModel and VersionedModel

In addition to the database-like datastore files, this python
module also provides the "SavableModel" and "VersionedModel" 
classes. In contrast to the datastore, these are useful
when you need to interact with regular, possibly user-facing
files on the disk directly without the "database" abstraction.

`SavableModel` can be used as a baseclass replacing
`pydantic.BaseModel`. It adds factory methods to the type
to easily load the model from or save a model to a file 
on disk and methods to easily save it.
It handles opening, reading parsing and validating
automatically, but gives you control about exactly what 
file you want to open and when to read/write it.
It can also remember the path of a file that was opened, 
so you can simply save it without needing to keep track of 
the location.

`VersionedModel` is especially useful in combination
with `SavableModel` to manage multiple versions of
file formats and automatically migrate from older
formats to newer formats when opening a file,
without you even noticing.
"""

from ._file import File, set_datastore_root
from ._specialized import specialized_file
from ._versioning import VersionedModel
from ._savable import SavableModel