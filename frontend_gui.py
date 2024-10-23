from config import *
from frontend_input import on_press
from backend_worker import ack_queue, actions_queue, backend_worker

from queue import Empty
from pynput import keyboard

import numpy as np
import wx

#main game window implemented in the program
class myframe(wx.Frame):
    def __init__(
            self,
            backend:backend_worker,
            lstn:keyboard.Listener,
            user='',
            passwd=''
    ):
        super().__init__(
            parent=None,
            size=GUI_SIZE
        )
        self.backend=backend
        self.lstn=lstn
        self.backend.start()
        self.lstn.start()

        # determine initial user
        if user != "":
            actions_queue.put((SET_USER, user, passwd))
        else:
            actions_queue.put((GET_CURRENT_USER,))

        # init config
        self.user=''
        self.user_undet=True # if user is undetermined, display circling(\|/-)
        self.tmspan=0. #time span ,also used time
        self.m=np.zeros((4,4),dtype=int) #tiles
        self.state=PENDING #synchronized state
        self.te_inf=[]# informing text

        self.init_ui()

        #bind event
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.on_routine,self.timer)
        self.timer.Start(round(1000/FPS))

        #problematic, use separate keyboard listener instead
        #self.Bind(wx.EVT_KEY_DOWN,self.on_key)

    def init_ui(self):
        self.p1=wx.Panel(
            self
        ) # p1 for game page. now multipage isn't implemented
        self.p1.SetBackgroundColour('lightblue')

        # init tiles
        self.tiles=[
            wx.StaticBitmap(
                self.p1,
            )for _ in range(16)
        ]
        self.bmps=[
            wx.Bitmap(
                wx.Image(
                    f'./img/bmp/tile_{i}.bmp',wx.BITMAP_TYPE_BMP
                ).Scale(*GUI_TILE_SIZE)
            )
            for i in range(12)
        ]

        #init tile_sizer
        self.tile_sizer=wx.GridSizer(4)# row col gap gap
        for i in range(16):
            self.tile_sizer.Add(self.tiles[i],wx.ALL|wx.CENTER|wx.EXPAND)
        self.tile_sizer.SetMinSize(*GUI_TILE_SIZE)

        #init supplement
        self.te=wx.StaticText(
            self.p1,
            label='',
            style=wx.ALIGN_CENTER_HORIZONTAL
        )

        #init main sizer
        self.main_sizer=wx.BoxSizer()
        self.main_sizer.Add(self.tile_sizer,proportion=0,flag=wx.CENTRE)
        self.main_sizer.Add(self.te,proportion=1,flag=wx.CENTRE)
        
        self.SetMinSize(GUI_GRID_SIZE)
        #add sizer to panel
        self.p1.SetSizer(self.main_sizer)

    #alternative implementation of on_press
    def on_key(self,e:wx.KeyEvent):
        return
        keycode=e.GetKeyCode()
        if keycode==ord('H')and e.ControlDown():
            actions_queue.put((HINT,))
        elif keycode==ord('C')and e.ControlDown():
            self.shutdown=True
        elif keycode==ord('Q')and e.ControlDown():
            try:
                import webbrowser
                b = webbrowser.get()
                b.open_new("https://www.github.com/lyn12233")
            except:pass
        elif keycode==wx.WXK_LEFT:
            actions_queue.put((MOVE,'l'))
        elif keycode==wx.WXK_RIGHT:
            actions_queue.put((MOVE,'r'))
        elif keycode==wx.WXK_UP:
            actions_queue.put((MOVE,'u'))
        elif keycode==wx.WXK_DOWN:
            actions_queue.put((MOVE,'d'))
        
    def on_routine(self,e):
        #shutdown check
        if not self.lstn.is_alive() or not self.backend.is_alive():
            self.Close()

        try:
            code,*args=ack_queue.get(block=False)
        except Empty:

            # scheduled routine
            actions_queue.put((GET_TIME,))
            actions_queue.put((GET_CURRENT_USER,))
            # varying at pending
            if self.state==PENDING and not self.te_inf:
                self.m=np.random.choice(np.arange(12),size=(4,4))
                self.update_tile()
            return
        
        # burst routine

        #update state
        if code==UPDATE_STATE:
            self.state=args[0]
            self.tmspan=0.
            if self.state!=PENDING:# when playing, the inf should be varying
                self.te_inf.clear()
        #move
        elif code==ACK_MOVE:
            _,self.m=args
            self.update_tile()
        #win
        elif code==WIN:
            #collect necessary data
            dir, self.m, new_rec, last_rec = args
            span, d = new_rec["value"], new_rec["date"]
            span2, d2 = last_rec["value"], last_rec["date"]
            IsBest=span<span2

            self.te_inf.clear()
            if self.state==PLAYING:
                self.te_inf.append(f'Congratulations {tr(self.user)}!')
                self.te_inf.append(f'finished game in {tr(span)}'+' (new record!)'*IsBest)
                self.te_inf.append(f'your record: {tr(span2)} achieved at {d2}GMT')
            elif self.state==CHEATING:
                self.te_inf.append('Finished! (you have cheated)')
            else:
                raise NotImplementedError(f"win at invalid state {self.state}")
            #both tiles and inf changed
            self.update_frame()
        #fail
        elif code==FAIL: #same like win,less inf
            dir,self.m=args

            self.te_inf.clear()
            self.te_inf.append('You failed!')

            self.update_frame()
        # set user displayed
        elif code==ACK_CURRENT_USER:
            self.user,*_=args
            #inf changed
            self.update_te()
            #user determined
            self.user_undet=False
        #set time
        elif code==ACK_TIME:
            if self.state==PENDING:#reassure inf maintains, when not playing
                ack_queue.task_done()
                return
            self.tmspan,*_=args
            #inf changed
            self.update_te()
        else:
            raise NotImplementedError

        #unecessary because we only use stop()
        ack_queue.task_done()

    #update tile
    def update_tile(self):
        assert len(self.tiles)==16
        assert len(self.bmps)==12
        assert self.m.shape==(4,4)

        for i in range(16):
            self.tiles[i].SetBitmap(self.bmps[self.m[i//4,i%4]])
        self.Show()
    #update inf text
    def update_te(self):
        inf=[]
        if self.state==PENDING:
            if not self.te_inf:
                if self.user_undet:
                    inf.append('user: '+'\\|/-'[np.random.randint(0,4)])
                else:
                    inf.append(f'user: {tr(self.user)}')
                inf.append('press direction keys to start')
            else:
                inf=self.te_inf
        elif self.state in (CHEATING,PLAYING):
            inf.append(f'user: {tr(self.user)}')
            inf.append(f'used time: {tr(self.tmspan)}'+'(CHEATED)'*(self.state==CHEATING))
        else:
            raise NotImplementedError(f'unkown state {self.state}')
        
        self.te.SetLabel('\n\n'.join(inf))

    def update_frame(self):
        self.update_te()
        self.update_tile()
    def __del__(self):
        self.backend.stop()
        self.lstn.stop()

if __name__=='__main__':
    #test
    app=wx.App()
    fr=myframe(
        backend_worker(),
        keyboard.Listener(on_press=on_press),
    )
    app.MainLoop()
        