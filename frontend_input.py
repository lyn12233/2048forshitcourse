from config import *
from backend_worker import actions_queue

from pynput import keyboard
import webbrowser


def on_press(key):
    "keyboard.Listener routine, message keyboard event to backend"
    if key == keyboard.Key.left:
        actions_queue.put((MOVE, "l"))
    elif key == keyboard.Key.right:
        actions_queue.put((MOVE, "r"))
    elif key == keyboard.Key.up:
        actions_queue.put((MOVE, "u"))
    elif key == keyboard.Key.down:
        actions_queue.put((MOVE, "d"))
    elif isinstance(key, keyboard.KeyCode):
        if eval(str(key)) == "\x08":  # Ctrl+H
            actions_queue.put((HINT,))
        elif eval(str(key)) == "\x03":  # Ctrl+C
            return False
        elif eval(str(key)) == "\x11":  # Ctrl+Q
            b = webbrowser.get()
            b.open_new("https://www.github.com/lyn12233")
        elif eval(str(key)) == "\x0c":  # Ctrl+L
            actions_queue.put((LOG,))
