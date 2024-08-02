"""
ELEKTRON © 2024 - now
Written by melektron
www.elektron.work
02.08.24, 09:34
All rights reserved.

This source code is licensed under the Apache-2.0 license found in the
LICENSE file in the root directory of this source tree. 

Simple logging setups and async terminal controller to allow
interactive CLI while using logging.
"""

import sys
import tty
import atexit
import termios
import asyncio
import logging
import typing
from el.errors import SetupError


LEVEL_COLORS = {
    'DEBUG': '\033[94m',    # Blue
    'INFO': '\033[92m',     # Green
    'WARNING': '\033[93m',  # Yellow
    'ERROR': '\033[91m',    # Red
    'CRITICAL': '\033[95m'  # Magenta
}
RESET = '\033[0m'  # Reset color
GREY = '\033[90m'  # Grey for logger name and line number

type LogLevel = int | str


class TerminalController(logging.Handler):
    """
    Class to asynchronously control a raw terminal with command prompt
    and above flowing log output
    """

    def __init__(self):
        """
        Creates a terminal controller that will manage terminal in raw mode to provide
        a CLI while allowing output to be printed above.
        """

        super().__init__()
        # put terminal into raw mode
        self._fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(self._fd)
        # enable direct control but still allows Ctrl+C and similar to work as expected
        tty.setcbreak(self._fd)
        # make sure the terminal is restored, even when crashing
        atexit.register(self._restore_settings)
        
        # flag that is set when loop should exit
        self._exited = False

        self._command_buffer = ""
        self._prompt = f"{GREY}>>{RESET} "
    
    async def setup_async_stream(self):
        """
        sets up the async stdin stream to be able to ready using asyncio
        https://stackoverflow.com/a/64317899

        This has to be called manually after the asyncio loop has been started. 
        This is not in __init__ to allow constructing a terminal object globally before 
        an asyncio event loop has been started.
        """
        loop = asyncio.get_event_loop()
        self._reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(self._reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    def _restore_settings(self):
        """
        restores the terminal configuration from cbreak back to what it was before.
        """
        termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
    
    async def next_command(self) -> str | None:
        """
        waits for a command to be entered and returns it when the user
        presses the enter key. If the application is due to exit before the
        command is submitted, None is returned
        """
        while not self._exited:
            c: bytes = ...
            try:
                async with asyncio.timeout(.5):
                    c = await self._reader.readexactly(1)
            except TimeoutError:
                continue

            if c == b'\x7f':  # Backspace
                if len(self._command_buffer) > 0:
                    self._command_buffer = self._command_buffer[:-1]
                    self._clear_line()
                    self._reprint_command_line()
                    sys.stdout.flush()
            #elif c in [b'\033[C', b'\033[B', b'\033[C', b'\033[D']:   # don't allow cursor movements
            #    continue   # TODO: fix this
            
            elif c == b'\n' or c == b'\r':  # Enter key
                cmd = self._command_buffer
                self._command_buffer = ""
                self.print(f"{self._prompt}{cmd}")
                return cmd

            else:   # normal character
                text = c.decode()
                self._command_buffer += text
                sys.stdout.write(text)
                sys.stdout.flush()
        
        return None

    def _clear_line(self):
        sys.stdout.write("\033[2K")  # Clear the current line
        sys.stdout.write("\033[1G")  # Move the cursor to the beginning of the line

    def _reprint_command_line(self) -> None:
        sys.stdout.write(self._prompt + self._command_buffer)
    
    def print(self, log: str | typing.Any) -> None:
        """
        normal print function that can be used to print lines to the terminal
        """
        self._clear_line()
        sys.stdout.write(str(log))
        sys.stdout.write("\n\r")
        self._reprint_command_line()
        sys.stdout.flush()
    
    def exit(self) -> None:
        """
        Stops the terminal controller which causes any active "await next_command()" calls to 
        exit returning None.
        """
        self._exited = True
    
    def emit(self, record: logging.LogRecord):
        """
        Emit override for logging handler support
        """
        try:
            msg = self.format(record)
            self.print(msg)
        except Exception:
            self.handleError(record)


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        level_color = LEVEL_COLORS.get(record.levelname, RESET)
        log_fmt = f"{level_color}%(levelname)s{RESET}: {GREY}%(name)s:%(lineno)d{RESET}: %(message)s"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


_TERMINAL: TerminalController | None = None


def setup_simple_logging(level: LogLevel = logging.INFO) -> None:
    """
    Configures the python logging library with a simple formatter
    and stream output handler that is a good baseline for most 
    non-interactive applications.

    Params:
        _level: The default logging level for the root logger
    """
    log = logging.getLogger()
    log.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)    # show everything if enabled
    
    formatter = ColoredFormatter()
    ch.setFormatter(formatter)
    
    log.addHandler(ch)


def setup_simple_terminal(level: LogLevel = logging.INFO) -> TerminalController:
    """
    Configures the python logging library with a simple formatter
    and am async terminal controller as the output to allow interactive commands
    while using logging.

    Params:
        _level: The default logging level for the root logger

    Returns: terminal controller
    """
    log = logging.getLogger()
    log.setLevel(level)

    term = TerminalController()
    term.setLevel(logging.DEBUG)    # show everything if enabled
    
    formatter = ColoredFormatter()
    term.setFormatter(formatter)
    
    log.addHandler(term)
    _TERMINAL = term
    return term


def get_term() -> TerminalController:
    if _TERMINAL is not None:
        return _TERMINAL
    
    raise SetupError("el.terminal.setup_simple_terminal() needs to be called before this.")