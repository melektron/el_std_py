"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 11:04
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

manual tests for terminal module
"""

import asyncio
import logging
from el import terminal, timers


_term = terminal.setup_simple_terminal()
_log = logging.getLogger(__name__)


async def handle_commands() -> None:
    cmd: str = ""
    while (cmd := await _term.next_command()) is not None:
        _log.info(f"Got command: {cmd}")
        match cmd:
            case "q":
                _term.exit()

async def some_logs() -> None:
    _log.debug("Hello debug")
    _log.info("Hello info")
    _log.warning("Hello warn")
    _log.error("Hello error")
    _log.critical("Hello critical")
    _log.fatal("Hello fatal")

async def run_tests() -> None:
    await _term.setup_async_stream()

    log_timer = timers.IntervalTimer(1.0)
    log_timer.on_interval(some_logs)
    log_timer.start()
    
    await handle_commands()


if __name__ == "__main__":
    asyncio.run(run_tests())
