N=4 # the tiles are N*N
LVWIN=3 # level of winning
FPS=10
def tr(s:str|float,dtype=None)->str:
    'translate user name/ used time to representation form'
    if isinstance(s,str):
        if s=='':
            return '(anonymous)'
        else:
            return s
    elif isinstance(s,float):
        if s<=0:
            return 'N.A.'
        else:
            return f'{s:.3f}'
    else:
        raise NotImplementedError
    