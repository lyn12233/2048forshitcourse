from frontend_input import on_press
from frontend_output import clear, frontend_worker
from backend_worker import backend_worker

from pynput import keyboard

import sys

if __name__ == "__main__":
    # clear console
    clear()
    # make sure tty supported
    assert (
        hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    ), "current console doesn't support ANSI escape sequence"

    # user logging-in by parameter
    arg = sys.argv
    user = arg[1] if len(arg) >= 2 else ""
    passwd = arg[2] if len(arg) == 3 else ""
    
    # mainloop
    frontend = frontend_worker()
    frontend.mainloop(
        keyboard.Listener(on_press=on_press), backend_worker(), user=user, passwd=passwd
    )
