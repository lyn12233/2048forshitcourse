from config import *

import numpy as np

np.random.seed(1145)

def update_array(arr: tuple[int]) -> tuple[int]:
    """
    update_array(arr:Tuple_Like)->Tuple_Like\n
    merge a row/col to the little endian\n
    tile value convention:\n
    \t -1 \tinvalid\n
    \t 0  \tblank tile\n
    \t i  \toccupied tile with presented value 2**i
    """
    res = [
        -1,
    ]
    bar = False  # only merge 2 tiles at once, thus need separation
    for i in arr:
        assert i >= 0, f"invalid tile value({i})"
        if i != 0:
            if i == res[-1] and not bar:
                res[-1] += 1
                bar = True
            else:
                res.append(i)
                bar = False
    res = res[1:]
    l = len(res)
    return tuple(res) + (0,) * (N - l)


def update_matrix(m: np.ndarray, dir: str|int) -> tuple[np.ndarray, bool]:
    """
    update_matrix(m:array(4,4))->m:array(4,4),flag:int\n
    update the full matrix of tiles in given direction(left,right,upper,downer)\n
    ordering of tiles: order='C'\n
    Returns:\n\tm\tthe new matrix\n\tflag\tdecide the game result, false for possibly trrapped
    """
    #copy m first
    m=m.copy()

    if isinstance(dir,int):
        dir='lrudn'[dir]
    assert m.shape == (N, N)
    assert dir in ("l", "r", "u", "d","n")

    if dir=='n':
        return m,True

    # transfer by direction
    if dir in ("u", "d"):
        m = np.swapaxes(m, 0, 1)
    if dir in ("r", "d"):
        m = np.fliplr(m)

    # try merge
    for i in range(N):
        m[i] = update_array(m[i])

    # reverse by direction
    if dir in ("r", "d"):
        m = np.fliplr(m)
    if dir in ("u", "d"):
        m = np.swapaxes(m, 0, 1)

    # add 2 new tiles
    idx_blank = np.argwhere(m == 0)
    if idx_blank.shape[0] == 0:
        return m, False
    elif idx_blank.shape[0] == 1:
        idx_new = idx_blank
    else:
        chc = np.random.choice(idx_blank.shape[0], 2, replace=False)
        idx_new = idx_blank[chc]
    # randomly
    for i in idx_new:
        m[tuple(i)] = np.random.choice([1, 2])
    return m, True


# test
if __name__ == "__main__":
    print(update_array((1,) * N))
    print(update_matrix(np.cumsum(np.ones((N, N), dtype=int), axis=1), dir="d"))
    m=np.array(eval('''[[2 2 2 0]
 [3 3 1 0]
 [2 2 0 0]
 [3 2 0 0]]'''.replace(' ',',')))
    print(update_matrix(m,0))