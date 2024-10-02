import os,sys
import numpy as np
from backend_worker import ack_queue,actions_queue,backend_worker
from frontend_input import on_press
from pynput import keyboard
from queue import Empty

from config import *

def clear():
    if sys.platform.startswith('win32'):
        os.system('cls')
    else:
        os.system('clear')


BKGD='\033[48;2;255;255;255m'   # white background
FRGD='\033[38;2;0;0;0m'         # black borrder
present_color=(
    '\033[48;2;211;211;211m',
    '\033[48;2;238;228;218m\033[38;2;0;0;0m',
    '\033[48;2;237;224;200m\033[38;2;0;0;0m',
    '\033[48;2;242;177;121m\033[38;2;0;0;0m',
    '\033[48;2;245;149;99m\033[38;2;0;0;0m',
    '\033[48;2;246;124;95m\033[38;2;0;0;0m',
    '\033[48;2;132;176;178m\033[38;2;0;0;0m',#64 medium orange
    '\033[48;2;237;207;114m\033[38;2;0;0;0m',# 128 light green
    '\033[48;2;237;207;97m\033[38;2;0;0;0m',# 256 light teal
    '\033[48;2;237;200;80m\033[38;2;0;0;0m',# 512 light blue
    '\033[48;2;177;156;217;80m\033[38;2;0;0;0m',# 1024 soft pruple
    '\033[48;2;255;215;0m\033[38;2;0;0;0m', # 2048 gold
)
present_text_up=(
    '    ',
    ' 2  ',
    ' 4  ',
    ' 8  ',
    ' 16 ',
    ' 32 ',
    ' 64 ',
    ' 12 ',
    ' 25 ',
    ' 51 ',
    ' 10 ',
    ' 20 ',
)
present_text_dn=(
    '    ',
    '    ',#2
    '    ',#4
    '    ',#8
    '    ',#16
    '    ',#32
    '    ',#64
    ' 8  ',#128
    ' 6  ',
    ' 2  ',
    ' 24 ',
    ' 48 ',
)

assert LVWIN<len(present_text_up)and LVWIN<len(present_text_dn)and LVWIN<len(present_color)

(
    LU,LD,RU,RD,
    TL,TR,TU,TD,
    H,V,
    X
)=(
    ' ┌─',' └─','─┐ ','─┘ ',
    ' ├─','─┤ ','─┬─','─┴─',
    '─',' │ ',
    '─┼─'
)
HCELL=len(present_text_up[0])
LEADIN='### Ctrl+H for Hint, Ctrl+C for exit, Ctrl+Q to explain what this is ###'

def update_frame(m:np.ndarray,*supplements:str):
    '''refresh the console and update values'''
    #supplements+=('_'*len(LEADIN),LEADIN)
    # generate out string
    assert m.shape==(N,N)
    est_col=len(LU)+len(TU)*(N-1)+HCELL*N+len(RU)
    est_row=3*N+1+len(supplements)
    max_col,max_row=os.get_terminal_size().columns,os.get_terminal_size().lines
    nbcspace=max((max_col-est_col)//2,0)
    nbcspace2=max((max_col-est_col-nbcspace),0)
    nbrspace=max((max_row-est_row-2)//2,0)
    nbrspace2=max((max_row-est_row-nbrspace),0)

    CSPACE,RSPACE=' '*nbcspace,(' '*max_col+'\n')*nbrspace
    CSPACE2,RSPACE2=' '*nbcspace2,(' '*max_col+'\n')*(nbrspace2-2)

    # generate outs
    outs=BKGD+FRGD+RSPACE
    outs+=CSPACE+LU+(H*HCELL+TU)*(N-1)+H*HCELL+RU+CSPACE2+'\n'
    for i in range(N):

        outs+=CSPACE+V
        for j in range(N):
            outs+=present_color[m[i][j]]+present_text_up[m[i][j]] +BKGD+FRGD+V
        outs+=CSPACE2+'\n'+CSPACE+V
        for j in range(N):
            outs+=present_color[m[i][j]]+present_text_dn[m[i][j]] +BKGD+FRGD+V
        outs+=CSPACE2+'\n'+CSPACE
        if i!=N-1:
            outs+=TL+(H*HCELL+X)*(N-1)+H*HCELL+TR+CSPACE2+'\n'
        else:
            outs+=LD+(H*HCELL+TD)*(N-1)+H*HCELL+RD+CSPACE2+'\n'

    #outs+=CSPACE+' '*est_col+CSPACE+'\n'
    for s in supplements:
        outs+=('{:^%d}'%(max_col,)).format(s)[:max_col]+'\n'
    outs+=RSPACE2

    # flush out string
    print('\033[0;0H\033[?25l')
    print(outs,end='',flush=True)
        
def mainloop(listener:keyboard.Listener,backend:backend_worker):
    listener.start()
    backend.start()

    actions_queue.put(('get_current_user',))
    user,span,m='',-1.,np.zeros((N,N),dtype=int)
    state='pending'

    update_frame(m,f'user: {tr(user)}',f'used time: {tr(span)}','_'*len(LEADIN),LEADIN)

    while listener.is_alive():
        try:
            code,*args=ack_queue.get(timeout=1/FPS)
        except Empty:
            actions_queue.put(('get_time',))
        except KeyboardInterrupt:
            break
        if code=='update_state':
            state=args[0]
        elif code == 'move':
            if state=='pending':
                clear()
            dir,m=args
            update_frame(m,f'user: {tr(user)}',f'used time: {tr(span)}'+' (CHEATED)'*(state=='cheating'))
        elif code == 'win':
            dir,m,new_rec,last_rec=args
            span,d=new_rec['value'],new_rec['date']
            span2,d2=last_rec['value'],last_rec['date']
            if state=='cheating':
                update_frame(m,'Finished! (CHEATED)')
            elif span<span2:
                update_frame(m,f'Congratulations {tr(user)}!',f'Finished game within {tr(span)} (new record!)',f'your record: {tr(span)}s at {d}')
            else:
                update_frame(m,f'Congratulations {tr(user)}!',f'Finished game within {tr(span)}',f'your record: {tr(span2)}s at {d2}')
        elif code == 'fail':
            dir,m=args
            update_frame(m,'You failed.')
        elif code == 'get_current_user':
            user,=args
        elif code == 'get_time':
            span,=args
            if state!='pending':
                update_frame(m,f'user: {tr(user)}',f'used time: {tr(span)}'+' (CHEATED)'*(state=='cheating'))
    clear()
    print('shutting down...')
    listener.stop()
    backend.stop()

if __name__=='__main__':
    clear()
    # mainloop
    mainloop(
        keyboard.Listener(on_press=on_press),
        backend_worker()
    )
