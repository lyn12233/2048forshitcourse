from config import *
from game_logic import update_matrix
import numpy as np

MONTE=4

def evaluate_m(m:np.ndarray):
    return np.sum(m**2)+2*(np.sum(m==0)+0)

class node():
    def __init__(self,m,action,depth=0,parent=None,max_depth=4,) -> None:
        "init is expanding"
        assert isinstance(m,np.ndarray)
        self.action=action
        self.m,self.avail=update_matrix(m,action)
        self.depth=depth
        self.parent=parent

        self.next=0 # default next step

        if depth<max_depth and self.avail:
            self.child:list[list[node]]=[]
            for next_step in range(4):
                sub=[node(m.copy(),next_step,depth=depth+1,parent=self) for _ in range(MONTE)]
                self.child.append(sub)
        else:
            self.child=[None,]*4
        
    def evaluate(self):
        if np.all([self.child[i]==None for i in range(4)]):
            # terminal node
            self.v=evaluate_m(self.m)
            self.c=0
        else:
            self.values=np.zeros((4,),dtype=float)
            for next_step in range(4):
                if self.child[next_step]==None:
                    pass
                else:
                    for i in self.child[next_step]:
                        i.evaluate()
                        self.values[next_step]+=i.v/len(self.child[next_step])
            # choose the best next_step
            self.v=np.max(self.values)
            self.c=np.argmax(self.values)
    def show(self):
        print(' '*self.depth+f'{self.v}')
        if self.child[self.c] is None:
            return
        for i in self.child[self.c]:
                i.show()
    def show_chain(self):
        print(f'act {self.action}->{self.m}')
        try:
            self.child[self.c][0].show_chain()
        except :pass
    def __repr__(self) -> str:
        return f'value {self.v}, ({self.c}->{self.values})\
              for tiles {self.m[0]},{self.m[1]},{self.m[2]},{self.m[3]}'
    def __getitem__(self,i):
        return self.child[i]

if __name__=='__main__':
    # component test
    m=np.array(
        (
            (1,1,1,1),
            (2,2,2,2),
            (1,1,1,1),
            (2,2,1,1),
        ),dtype=int
    )
    n0=node(m,N,)
    n0.evaluate()
    n0.show_chain()