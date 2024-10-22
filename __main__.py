from frontend_input import on_press
from frontend_output import clear, frontend_worker
from frontend_gui import myframe
from backend_worker import backend_worker
import wx

from pynput import keyboard
import argparse

import sys

if __name__ == "__main__":
    # clear console
    clear()
    # make sure tty supported
    assert (
        hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    ), "current console doesn't support ANSI escape sequence"

    # user logging-in by parameter
    parser=argparse.ArgumentParser(prog='2048',description='simple 2048 game')
    parser.add_argument('-c','--user')
    parser.add_argument('-p','--passwd')
    parser.add_argument('-g','--gui',action='store_true')
    #ns=parser.parse_args(' --passwd p --gui'.split())
    #print(ns)
    ns=parser.parse_args(sys.argv[1:])
    user = ns.user if ns.user!=None else ""
    passwd = ns.passwd if ns.passwd!=None else ""
    #print(ns);input()
    if ns.gui:
        app=wx.App()
        fr=myframe(backend_worker(),keyboard.Listener(on_press=on_press))
        app.MainLoop()

    else:
        # cui mainloop
        frontend = frontend_worker()
        frontend.mainloop(
            keyboard.Listener(on_press=on_press), backend_worker(), user=user, passwd=passwd
        )
