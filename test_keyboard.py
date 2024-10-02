import os,time
from backend_worker import ack_queue,actions_queue,backend_worker
from pynput import keyboard
def on_press(key):
    print(key,type(key),eval(str(key))=="\x08" if isinstance(key,keyboard.KeyCode)else 0)

with keyboard.Listener(on_press=on_press)as l:
    l.join()