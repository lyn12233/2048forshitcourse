import wx
import time
import os

current_path=os.path.split(__file__)[0]
icon_path = os.path.join(current_path,'img','my2048.ico')
title_prefix='2048'
default_size=(400,300)

#tile_images=[os.path.join(current_path,f'tile_{int(2**i)}.jpg') for i in range(-1,12)]


print(wx.DefaultSize)

class My2048Frame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(parent=None,title=title_prefix,size=default_size)
        self.SetIcon(wx.Icon(icon_path))

        self.load_images()
        self.load_user()

        self.init_menubar()
        self.init_ui()
        self.Show()

    def init_menubar(self):
        menubar=wx.MenuBar()
         # Game menu
        game_menu = wx.Menu()
        game_menu.Append(wx.ID_ANY, 'Restart', 'Restart the game')
        game_menu.Append(wx.ID_ANY, 'Hint', 'Show a hint')
        menubar.Append(game_menu, 'Game')
        # Option menu
        option_menu = wx.Menu()
        option_menu.Append(wx.ID_ANY, 'Mode', 'Change mode')
        option_menu.Append(wx.ID_ANY, 'User', 'Change user')
        menubar.Append(option_menu, 'Option')
        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ANY, 'What is this?', 'Show help information')
        menubar.Append(help_menu, 'Help')
        # Set Menubar
        self.SetMenuBar(menubar)
        # Bind menu actions
        self.Bind(wx.EVT_MENU, self.on_restart,     id=game_menu.FindItem('Restart')      )
        self.Bind(wx.EVT_MENU, self.on_hint,        id=game_menu.FindItem('Hint')         )
        self.Bind(wx.EVT_MENU, self.on_mode,        id=option_menu.FindItem('Mode')       )
        self.Bind(wx.EVT_MENU, self.on_user,        id=option_menu.FindItem('User')       )
        self.Bind(wx.EVT_MENU, self.on_help,        id=help_menu.FindItem('What is this?'))

    def init_ui(self):
        # Create panels
        self.page1 = wx.Panel(self)
        self.page2 = wx.Panel(self)
        # Set background colors for visibility
        self.page1.SetBackgroundColour('lightblue')
        self.page2.SetBackgroundColour('lightgreen')

        # Init page 1
        self.tiles=[wx.StaticBitmap(self.page1) for _ in range(16)]# normal mode is 4x4
        p1box=wx.BoxSizer(wx.HORIZONTAL)


        # Initially show the first panel
        self.page1.Show()
        self.page2.Hide()
    def on_restart(self,event):
        pass
    def on_hint(self,event):
        pass
    def on_mode(self,event):
        pass
    def on_user(self,event):
        pass
    def on_help(self,event):
        pass

    def load_images(self):
        tile_images=[os.path.join(current_path,f'tile_0.jpg') for i in range(-1,12)]
        self.tile_images=[wx.Bitmap(i) for i in tile_images]
    def load_user(self):
        pass

if __name__=='__main__':
    app = wx.App()
    frame = My2048Frame()
    app.MainLoop()