from config import *
from game_logic import update_matrix

from threading import Thread
from queue import Queue,Empty
import numpy as np

import os
import json
import time

actions_queue=Queue()
ack_queue=Queue()
'''full actions:
2. l/r/u/d: moving
3. query_all'''

class backend_worker(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.daemon=True
        self.keep_running=True

        # load user data
        user_data_path=os.path.join(os.path.split(__file__)[0],'userdata.json')
        if not os.path.isfile(user_data_path):
            self.user_data={'users':{'':{'password':'',}},'current_user':''}
        else:
            with open(user_data_path,'r',encoding='utf8')as f:
                self.user_data=json.load(f)
        self.FW=open(user_data_path,'w',encoding='utf8')
        self.flush_userdata()

        # game state
        self.game_state='pending'
        self.start_time=1e99
        self.end_time=0

    def run(self):
        while self.keep_running:
            try:
                code,*args=actions_queue.get(timeout=1)
                if code == 'move':
                    if self.game_state=='pending':
                        # start the game
                        self.game_state='playing'
                        ack_queue.put(('update_state','playing'))
                        self.tiles=np.zeros((N,N),dtype=int)
                        self.available_dirs={'l':True,'r':True,'u':True,'d':True}
                        self.start_time=time.time()
                    dir,*_=args
                    self.tiles,available=update_matrix(self.tiles,dir)
                    if not available:
                        self.available_dirs[dir]=False
                    else:
                        self.available_dirs={'l':True,'r':True,'u':True,'d':True}

                    # check and return
                    # win
                    if np.any(self.tiles>=LVWIN):
                        self.end_time=time.time()
                        used_time=self.end_time-self.start_time
                        self.game_state='pending'
                        # update record
                        user=self.user_data['current_user']
                        new_record={'value':used_time,'date':time.strftime('%Y.%m.%d %H:%M',time.gmtime())}
                        last_record=self.user_data['users'][user]['record'] if 'record' in self.user_data['users'][user] else {'value':1e99,'date':0}
                        #update record
                        if new_record['value']<last_record['value']:
                            self.user_data['users'][user]['record']=new_record
                            self.flush_userdata()
                        ack_queue.put(('win',dir,np.copy(self.tiles),new_record,last_record))
                        ack_queue.put(('update_state','pending'))
                    # fail
                    elif tuple(self.available_dirs.values())==(False,)*4:
                        self.end_time=time.time()
                        self.game_state='pending'
                        ack_queue.put(('update_state','pending'))
                        ack_queue.put(('fail',dir,np.copy(self.tiles)))
                    # move done
                    else:
                        ack_queue.put((code,dir,np.copy(self.tiles)))
             
                elif code=='set_current_user':
                    if self.game_state!='playing':
                        self.user_data['current_user']=args[0]
                 
                elif code == 'get_time':
                    if self.game_state!='pending':
                        span=time.time()-self.start_time
                    else:
                        span=self.end_time-self.start_time
                    ack_queue.put((code,span))
                    
                elif code=='get_current_user':
                    ack_queue.put((code,self.user_data['current_user']))

                elif code=='hint':
                    if self.game_state=='pending':
                        pass
                    else:
                        self.game_state='cheating'
                        ack_queue.put(('update_state','cheating'))
                        sel=[]
                        for dir in 'lrud':
                            tails,available=update_matrix(self.tiles,dir)
                            sel.append((np.sum(tails==0),dir))
                        best_dir=max(sel)[1]
                        #raise
                        if actions_queue.empty():
                            actions_queue.put(('move',best_dir))
                actions_queue.task_done()
            except Empty:
                pass
        #stopped running
        self.FW.close()
    def stop(self):
        self.keep_running=False
    def _write(self):
        self.FW.truncate(0)
        self.FW.write(
            json.dumps(self.user_data,indent=4)
        )
    def flush_userdata(self):
        self.FW.seek(0)
        self.FW.truncate()
        json.dump(self.user_data,self.FW)
        self.FW.flush()
        #print(f'{self.user_data} dumped')