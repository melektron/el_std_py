"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 10:43
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

manual tests for timers module
"""

import aioconsole
from el.timers import *


async def timeout():
    print("timeout")

async def restart():
    print("restart")

async def run_tests():
    timer = WDTimer(5)
    timer.on_restart(restart)
    timer.on_timeout(timeout)

    while await aioconsole.ainput() != "q":
        print("refresh")
        timer.refresh()

# Tests
if __name__ == "__main__":
    asyncio.run(run_tests())
