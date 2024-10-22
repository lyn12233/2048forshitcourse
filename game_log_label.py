import concurrent.futures
import concurrent
from config import *
import numpy as np
from game_search import evaluate_m,node
import concurrent
dat=np.load('./log.npz')['arr_0']
print(dat.shape)

#labeling

NSMP=dat.shape[0]
def get_val(m):
    #m=dat[i]
    n0=node(m,N,)
    n0.evaluate()
    print(n0.v-evaluate_m(m))
    return n0.v-evaluate_m(m)

arglist=[(dat[i].copy(),)for i in range(NSMP)]

if __name__=='__main__':
    with concurrent.futures.ProcessPoolExecutor()as ex:
        results=ex.map(get_val,*zip(*arglist))

    print(results)
    np.savez('./label.npz',dat=dat,label=[i for i in results])