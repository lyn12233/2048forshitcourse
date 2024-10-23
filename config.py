N = 4  # the tiles are N*N
LVWIN = 11  # level of winning
FPS = 60  # frame per second/ for time presenting

ACTIONS=L,R,U,D,NOP=range(5)
# queue codes
(
    MOVE,
    SET_USER,
    GET_TIME,
    HINT,
    GET_CURRENT_USER,
    # acks
    ACK_MOVE,
    UPDATE_STATE,
    WIN,
    FAIL,
    ACK_CURRENT_USER,
    ACK_TIME,
    # states
    PENDING,
    PLAYING,
    CHEATING,
    #logging
    LOG,
    *_
)=range(100)

# TRACK=True # track tiles matrix for training
TRACK=False

# GUI config
GUI_SIZE=(900,500)
GUI_GRID_SIZE=(500,500)
GUI_TILE_SIZE=(100,100)

#translation util
def tr(s: str | float, dtype=None) -> str:
    "translate user name/ used time to representation form"
    if isinstance(s, str):
        if s == "":
            return "(anonymous)"
        else:
            return s
    elif isinstance(s, float):
        if s < 0 or s > 1e19:
            return "N.A."
        else:
            return f"{s:.3f}s"
    else:
        raise NotImplementedError
