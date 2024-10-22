import wx
import numpy as np
from config import *
from frontend_input import on_press
from queue import Empty
from backend_worker import ack_queue, actions_queue, backend_worker
from pynput import keyboard

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
        self.user_undet=True
        self.tmspan=0.
        self.desc_lines=[]
        self.m=np.zeros((4,4),dtype=int)
        self.state=PENDING
        self.te_inf=[]

        self.init_ui()

        #bind event
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.on_routine,self.timer)
        self.timer.Start(round(1000/FPS))

        self.Bind(wx.EVT_KEY_DOWN,self.on_key)

    def init_ui(self):
        self.p1=wx.Panel(
            self
        ) # p1 for game page
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
        if not self.lstn.is_alive() :
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
        if code==UPDATE_STATE:
            self.state=args[0]
            self.tmspan=0.
            if self.state!=PENDING:
                self.te_inf.clear()
        elif code==ACK_MOVE:
            _,self.m=args
            self.update_tile()
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
            else:raise NotImplementedError
            self.update_frame()

        elif code==FAIL:
            dir,self.m=args

            self.te_inf.clear()
            self.te_inf.append('You failed!')

            self.update_frame()

        elif code==ACK_CURRENT_USER:
            self.user,*_=args
            self.update_te()
            self.user_undet=False
        elif code==ACK_TIME:
            if self.state==PENDING:return
            self.tmspan,*_=args
            self.update_te()
        else:raise NotImplementedError

    def update_tile(self):
        assert len(self.tiles)==16
        assert len(self.bmps)==12
        assert self.m.shape==(4,4)
        for i in range(16):
            self.tiles[i].SetBitmap(self.bmps[self.m[i//4,i%4]])
        self.Show()
    def update_te(self):
        inf=[]
        if self.state==PENDING:
            if not self.te_inf:
                if self.user_undet:
                    inf.append('user: '+'\\|/'[np.random.randint(0,3)])
                else:
                    inf.append(f'user: {self.user}')
                inf.append('press direction keys to start')
            else:
                inf=self.te_inf
        elif self.state in (CHEATING,PLAYING):
            inf.append(f'user: {self.user}')
            inf.append(f'used time: {tr(self.tmspan)}'+'(CHEATED)'*(self.state==CHEATING))
        else:
            raise NotImplementedError(f'unkown state {self.state}')
        
        self.te.SetLabel('\n'.join(inf))

    def update_frame(self):
        self.update_te()
        self.update_tile()
    def __del__(self):
        self.backend.stop()
        self.lstn.stop()

if __name__=='__main__':
    app=wx.App()
    fr=myframe(backend_worker(),keyboard.Listener(on_press=on_press))
    app.MainLoop()
        