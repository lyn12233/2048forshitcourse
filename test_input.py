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

backend=backend_worker()
backend.start()
listener=keyboard.Listener(on_press=on_press)
listener.start()
while listener.is_alive():
    code,*args=ack_queue.get()
    if code=='move':
        print(args[1])
    elif code=='win':
        print(args[1])
        print('win')
        break
    elif code=='fail':
        print(args[1])
        print('fail')
        break
backend.stop()
listener.stop()
time.sleep(0.3)
os.system('cls')