"""
ELEKTRON © 2023 - now
Written by melektron
www.elektron.work
02.09.23, 17:40
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

manual tests for datastore module
"""

import pydantic
import asyncio

from el.timers import IntervalTimer
from el.datastore import File, specialized_file


class _MySpecialFile(pydantic.BaseModel):
    hello: int = 0
    goodby: str = "abc"


async def _count_fn():
    print(len(File.__all_files__))


@specialized_file(base_path=["base", "path"])
#@specialized_file
class _MyFileDataModel(pydantic.BaseModel):
    var1: int = 1
    var3: int = 4
    name_var: str = "mel"


#myfile = File(["test"], _MyFileDataModel)
#myfile.content.var1

class MyClass:
    def __init__(self) -> None:
        self._testfile1 = File(["annoyi42 aon*gpa//th"], _MySpecialFile)
        print(self._testfile1.content.goodby)


@specialized_file
class MyDataStructure(pydantic.BaseModel):
    value1: int = 13
    name: str = "hello"
    list_of_wishes: list[str] = [
        "powerbank",
        "airpodspro",
        "macarena"
    ]


async def run_tests():

    inst = MyDataStructure(["hi"])

    print(inst.value1)

    inst.value1 = 26

    await asyncio.sleep(10)

    inst.list_of_wishes.append("blablabl mak machen")

    return
    #IntervalTimer(0.5).on_interval(_count_fn).start()

    # ints = MyClass()
    #_MyFileDataModel()

    data = _MyFileDataModel(["test", "another", "specialized"])
    print(data.var1)#
    data.var1 = 2
    print(f"JSON: {data.model_dump_json()}")


    await asyncio.sleep(1)

    """
    testfile1 = File(["annoyi42 aon*gpa//th"], _MySpecialFile)
    testfile2 = File(["annoyi42 aon*gpa//th"], _MySpecialFile)

    print(f"file1: {testfile1.content}\nfile2: {testfile2.content}")
    testfile2.content.hello = 28
    # testfile1.save_to_disk()
    # testfile1.save_to_disk()
    await asyncio.sleep(4)
    print(f"file1: {testfile1.content}\nfile2: {testfile2.content}")
    # testfile1.save_to_disk()
    # testfile1.save_to_disk()

    await asyncio.sleep(10)
    """


if __name__ == "__main__":
    asyncio.run(run_tests())