N = 4  # the tiles are N*N
LVWIN = 5  # level of winning
FPS = 60  # frame per second/ for time presenting


def tr(s: str | float, dtype=None) -> str:
    "translate user name/ used time to representation form"
    if isinstance(s, str):
        if s == "":
            return "(anonymous)"
        else:
            return s
    elif isinstance(s, float):
        if s <= 0 or s > 1e19:
            return "N.A."
        else:
            return f"{s:.3f}s"
    else:
        raise NotImplementedError
