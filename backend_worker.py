from config import *
from game_logic import update_matrix
from game_search import simple_search

from threading import Thread
from queue import Queue, Empty
import numpy as np

import os
import json
import time

actions_queue = Queue()
ack_queue = Queue()
"""full actions:
1. l/r/u/d: moving
2. get time
3. hint
4. get/set user"""


class backend_worker(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.daemon = True # close with mainn thread
        self.keep_running = True # postponed shutdown

        # load user data
        user_data_path = os.path.join(os.path.split(__file__)[0], "userdata.json")
        if not os.path.isfile(user_data_path):
            self.user_data = {
                "users": {
                    "": {"password": "", "record": {"value": 1e99, "date": "N.A."}}
                },
                "current_user": "",
            }
        else:
            with open(user_data_path, "r", encoding="utf8") as f:
                self.user_data = json.load(f)
        self.FW = open(user_data_path, "w", encoding="utf8")
        # reset current user if it has password
        if self.user_data["users"][self.user_data["current_user"]]["password"] != "":
            self.user_data["current_user"] = ""

        self.flush_userdata()

        # game state
        self.game_state = PENDING
        self.start_time = 1e99
        self.end_time = 0

        #log storage
        self.logs=[]

    def run(self):
        'called by Thread.start(), baeckend mainloop'
        while self.keep_running:
            # no scheduled routines, thus unecessary for try..except Empty block
            try:
                code, *args = actions_queue.get(timeout=1)

                # match..case block. for compatibility

                # one move on tiles
                if code == MOVE:
                    # start the game
                    if self.game_state == PENDING:
                        self.game_state = PLAYING
                        ack_queue.put((UPDATE_STATE, PLAYING))
                        self.tiles = np.zeros((N, N), dtype=int)
                        self.start_time = time.time()

                    #log
                    if TRACK:
                        self.logs.append(self.tiles.copy())
                    # conduct move
                    dir, *_ = args
                    self.tiles, available = update_matrix(self.tiles, dir)
                    # precheck for fail
                    if not available:
                        available_dirs=[
                            update_matrix(self.tiles,'lrud'[dir])[1] for dir in range(4)
                        ]
                    else:
                        available_dirs=[True,]

                    # check for return
                    # win
                    if np.any(self.tiles >= LVWIN):
                        # calc used time
                        self.end_time = time.time()
                        used_time = self.end_time - self.start_time
                        self.game_state = PENDING
                        # generate record
                        user = self.user_data["current_user"]
                        new_record = {
                            "value": used_time,
                            "date": time.strftime("%Y.%m.%d %H:%M", time.gmtime()),
                        }
                        last_record = (
                            self.user_data["users"][user]["record"]
                            if "record" in self.user_data["users"][user]
                            else {"value": 1e99, "date": 0}
                        )
                        # update record
                        if new_record["value"] < last_record["value"]:
                            self.user_data["users"][user]["record"] = new_record
                            self.flush_userdata()
                        #ackownledge
                        ack_queue.put(
                            (WIN, dir, np.copy(self.tiles), new_record, last_record)
                        )
                        ack_queue.put((UPDATE_STATE, PENDING))
                    # fail
                    elif not np.any(available_dirs):
                        self.end_time = time.time()
                        self.game_state = PENDING
                        #ackownledge
                        ack_queue.put((FAIL, dir, np.copy(self.tiles)))
                        ack_queue.put((UPDATE_STATE, PENDING))
                    # normal move done
                    else:
                        ack_queue.put((ACK_MOVE, dir, np.copy(self.tiles)))

                #set user
                elif code == SET_USER:
                    #only permitted when pending
                    if self.game_state == PENDING:
                        user2, passwd = args

                        # sign in
                        if user2 in self.user_data["users"]:  
                            # assert passwd==self.user_data['users'][user]['password'],'wrong password'
                            if (
                                passwd == self.user_data["users"][user2]["password"]
                            ):  # password correct
                                self.user_data["current_user"] = user2
                            else:  # log in failed
                                pass

                        # sign up
                        elif str.isidentifier(user2):  # qualified user name
                            self.user_data["users"][user2] = {
                                "password": passwd,
                                "record": {"value": 1e99, "date": "N.A."},
                            }
                            self.user_data["current_user"] = user2
                        else:  # unqualified user name
                            pass

                        #store and ack
                        self.flush_userdata()
                        ack_queue.put(
                            (ACK_CURRENT_USER, self.user_data["current_user"])
                        )

                elif code == GET_TIME:
                    if self.game_state != PENDING:
                        span = time.time() - self.start_time
                    else:#when pending, tmspan default static
                        span = self.end_time - self.start_time
                    ack_queue.put((ACK_TIME, span))

                elif code == GET_CURRENT_USER:
                    ack_queue.put((ACK_CURRENT_USER, self.user_data["current_user"]))

                #hint,Ctrl+H
                elif code == HINT:
                    if self.game_state != PENDING:
                        self.game_state = CHEATING
                        ack_queue.put((UPDATE_STATE, CHEATING))

                        #select the best move
                        # sel = []
                        # for dir in range(4):
                        #     tails, available = update_matrix(self.tiles, dir)
                        #     sel.append((np.sum(tails == 0), dir))
                        # best_dir = max(sel)[1]
                        # new implementation
                        best_dir=simple_search(self.tiles)
                        while not actions_queue.empty():
                            actions_queue.task_done()
                            actions_queue.get_nowait()
                        actions_queue.put((MOVE, best_dir))
                #log, Ctrl+L
                elif code==LOG:
                    if TRACK:
                        last=np.load('./log.npz')['arr_0']
                        np.savez('./log.npz',np.concatenate((self.logs,last)))
                        self.logs=[]
                #unkown opcode
                else:
                    raise NotImplementedError(f"backend: code {code} uncaught")
                actions_queue.task_done()

            #scheduled routine
            except Empty:
                pass
        #handle shutdown
        self.FW.close()

    # stopped running
    def stop(self):
        self.keep_running = False

    def flush_userdata(self):
        self.FW.seek(0)
        self.FW.truncate()
        json.dump(self.user_data, self.FW)
        self.FW.flush()
        # print(f'{self.user_data} dumped')
