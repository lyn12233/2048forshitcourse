import os,time
from backend_worker import ack_queue,actions_queue,backend_worker
from pynput import keyboard
def on_press(key):

    if key==keyboard.Key.left:
        actions_queue.put(('move','l'))
    elif key==keyboard.Key.right:
        actions_queue.put(('move','r'))
    elif key==keyboard.Key.up:
        actions_queue.put(('move','u'))
    elif key==keyboard.Key.down:
        actions_queue.put(('move','d'))