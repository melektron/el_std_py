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

from el.errors import SetupError

import sys
import atexit
if sys.platform != "win32":
    import tty
    import termios
else:
    import ctypes
    import ctypes.wintypes
    import queue
    import threading
    import msvcrt
    import os

    try:
        import colorama
    except ImportError:
        raise SetupError("el.terminal requires colorama on Windows. Please install it before using el.terminal.")
        #raise SetupError("el.widgets requires customtkinter and pillow (PIL). Please install them before using el.widgets.")
import asyncio
import logging
import typing


BLUE    = '\033[94m'
GREEN   = '\033[92m'
YELLOW  = '\033[93m'
RED     = '\033[91m'
MAGENTA = '\033[95m'
GREY    = '\033[90m'
RESET   = '\033[0m'  # Reset color to default

LEVEL_COLORS = {
    'DEBUG': BLUE,
    'INFO': GREEN,
    'WARNING': YELLOW,
    'ERROR': RED,
    'CRITICAL': MAGENTA
}

type LogLevel = int | typing.Literal[
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
]

ENABLE_ECHO_INPUT = 0x0004
ENABLE_LINE_INPUT = 0x0002
ENABLE_PROCESSED_INPUT = 0x0001
ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

def set_cbreak_mode_windows():
    h_stdin = ctypes.windll.kernel32.GetStdHandle(-10)
    mode = ctypes.wintypes.DWORD()
    ctypes.windll.kernel32.GetConsoleMode(h_stdin, ctypes.byref(mode))
    new_mode = mode.value & (~(ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT))
    ctypes.windll.kernel32.SetConsoleMode(h_stdin, new_mode)


class TerminalController(logging.Handler):
    """
    Class to asynchronously control a raw terminal with command prompt
    and above flowing log output
    """

    def __init__(self, interactive: bool = True):
        """
        Creates a terminal controller that will manage terminal in raw mode to provide
        a CLI while allowing output to be printed above.

        Parameters
        ----------
        interactive : bool, optional
            Whether the interactive stdin terminal should be enabled, by default True.
            Disabling this will run the application in "daemon mode" where the prompt
            is disabled (nicer log output) and stdin is not required (necessary when running 
            via .desktop entry). This may be required when stdio is not connected to a tty. 
            When stdin is connected to a non-tty, this is disabled automatically.
        """

        super().__init__()

        self._interactive = interactive

        if self._interactive:
            try:
                # test if we are connected to a tty. If we are not,
                # we disable interactivity regardless of the argument value
                self._interactive = sys.stdin.isatty()
            except Exception:
                # if stdin is not available, we also disable interactivity
                self._interactive = False

        if self._interactive:
            self._fd = sys.stdin.fileno()

            if sys.platform != "win32":
                # put terminal into raw mode
                self._old_settings = termios.tcgetattr(self._fd)
                # enable direct control but still allows Ctrl+C and similar to work as expected
                tty.setcbreak(self._fd)
            else:
                #msvcrt.setmode(self._fd, os.O_BINARY)
                set_cbreak_mode_windows()
                colorama.just_fix_windows_console()     # enables coloring on windows in every situation
                self._win_input_queue = queue.Queue()   # queue to transfer input from thread

            # make sure the terminal is restored, even when crashing
            atexit.register(self._restore_settings)
        
        self._command_buffer = ""
        self._prompt = f"{GREY}>>{RESET} "
        
        # flag that is set when loop should exit
        self._exited = False

    async def setup_async_stream(self):
        """
        sets up the async stdin stream to be able to ready using asyncio
        https://stackoverflow.com/a/64317899

        This has to be called manually after the asyncio loop has been started. 
        This is not in __init__ to allow constructing a terminal object globally before 
        an asyncio event loop has been started.
        """
        # when running in non-interactive mode we likely can't do this
        if not self._interactive:
            return
        
        if sys.platform != "win32":
            loop = asyncio.get_event_loop()
            self._reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(self._reader)
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        else:
            self._win_read_thread = threading.Thread(target=self._windows_read_thread, daemon=True)
            self._win_read_thread.start()
    
    if sys.platform == "win32":
        def _windows_read_thread(self) -> None:
            while not self._exited:
                # getch() does not support input that is redirected. However swithcing to using stdin has weird
                # behaviour with the return key. For this reason, we are using getch() for now
                #char = sys.stdin.read(1).encode()
                char = msvcrt.getch()
                self._win_input_queue.put(char)
        
    async def _portable_read_one(self) -> bytes:
        if sys.platform != "win32":
            return await self._reader.readexactly(1)
        else:
            while True:
                try:
                    return self._win_input_queue.get_nowait()
                except queue.Empty:
                    pass
                await asyncio.sleep(0.03) # check every 30ms for relatively responsive input
    
    def _restore_settings(self):
        """
        restores the terminal configuration from cbreak back to what it was before.
        """
        if sys.platform != "win32":
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old_settings)
        else:
           ...
    
    async def next_command(self) -> str | None:
        """
        waits for a command to be entered and returns it when the user
        presses the enter key. If the application is due to exit before the
        command is submitted, None is returned
        """
        while not self._exited:
            # in interactive mode we just do nothing
            if not self._interactive:
                await asyncio.sleep(.5)
                continue
            
            # otherwise wait for input and process it
            c: bytes = ...
            try:
                async with asyncio.timeout(.5):
                    c = await self._portable_read_one()
            except TimeoutError:
                continue

            if c == b'\x7f' or (sys.platform == "win32" and c == b'\x08'):  # Backspace
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
        # in non interactive mode, there is no prompt and no clearing
        if self._interactive:
            sys.stdout.write("\033[2K")  # Clear the current line
            sys.stdout.write("\033[1G")  # Move the cursor to the beginning of the line

    def _reprint_command_line(self) -> None:
        # in non interactive mode, there is no prompt and no clearing
        if self._interactive:
            sys.stdout.write(self._prompt + self._command_buffer)
    
    def print(self, log: str | typing.Any, color: str | None = None) -> None:
        """
        normal print function that can be used to print lines to the terminal.
        If a color is specified (string with the appropriate ANSI escape sequence)
        the color string is prepended and a color reset sequence is automatically prepended
        to the printed message
        """
        self._clear_line()
        if color is not None:
            sys.stdout.write(color + str(log) + RESET)
        else:
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

    Parameters
    ----------
    level : LogLevel, optional
        Global log level, by default INFO.
    """
    log = logging.getLogger()
    log.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)    # show everything if enabled
    
    formatter = ColoredFormatter()
    ch.setFormatter(formatter)
    
    log.addHandler(ch)


def setup_simple_terminal(
    level: LogLevel = logging.INFO, 
    interactive: bool = True
) -> TerminalController:
    """
    Configures the python logging library with a simple formatter
    and am async terminal controller as the output to allow interactive commands
    while using logging.

    Parameters
    ----------
    level : LogLevel, optional
        Global log level, by default INFO.
    interactive : bool, optional
        Whether the interactive stdin terminal should be enabled, by default True.
        Disabling this will run the application in "daemon mode" where the prompt
        is disabled (nicer log output) and stdin is not required (necessary when running 
        via .desktop entry). This may be required when stdio is not connected to a tty. 
        When stdin is connected to a non-tty, this is disabled automatically.

    Returns: terminal controller
    """
    global _TERMINAL
    log = logging.getLogger()
    log.setLevel(level)

    term = TerminalController(interactive=interactive)
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


def set_root_log_level(level: LogLevel) -> int | None:
    """
    Sets the log level of the root logger and returns its integer
    representation.
    If the level is not valid, None is returned and nothing happens
    """
    try:
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        return root_logger.level
    except (ValueError, TypeError) as e:
        return None