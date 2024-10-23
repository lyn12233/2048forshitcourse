from config import *
from frontend_input import on_press
from backend_worker import backend_worker

# delayed import for frontend_output/gui

from pynput import keyboard
import argparse

import sys


if __name__ == "__main__":

    # user logging-in and select UI by parameter
    parser = argparse.ArgumentParser(prog="2048", description="simple 2048 game")
    parser.add_argument("-c", "--user")
    parser.add_argument("-p", "--passwd")
    parser.add_argument("-g", "--gui", action="store_true")

    ns = parser.parse_args(sys.argv[1:])
    user = ns.user if ns.user != None else ""
    passwd = ns.passwd if ns.passwd != None else ""

    if ns.gui:  # GUI

        # try to import wx
        try:
            import wx
            from frontend_gui import myframe
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                "wxpython isn't installed or it is not supported on your platform"
            )

        # gui mainloop
        app = wx.App()
        fr = myframe(
            backend_worker(),
            keyboard.Listener(on_press=on_press),
            user=user,
            passwd=passwd,
        )
        app.MainLoop()

    else:  # CUI

        # check tty supporting
        assert (
            hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
        ), "current console doesn't support ANSI escape sequence"
        from frontend_output import clear, frontend_worker

        # clear console
        clear()
        # cui mainloop
        frontend = frontend_worker()
        frontend.mainloop(
            keyboard.Listener(on_press=on_press),
            backend_worker(),
            user=user,
            passwd=passwd,
        )
