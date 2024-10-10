from config import *
from frontend_input import on_press
from backend_worker import ack_queue, actions_queue, backend_worker

import numpy as np
from queue import Empty
from pynput import keyboard

import os, sys


def clear():
    "clear console when starting/ size changed. cause sparkling"
    if sys.platform.startswith("win32"):
        os.system("cls")
    else:
        os.system("clear")


# defining colors and representations(ANSI escape sequence).
# each tile is 4*2 spaces
BKGD = "\033[48;2;255;255;255m"  # white background
FRGD = "\033[38;2;0;0;0m"  # black border
present_color = (
    "\033[48;2;211;211;211m",
    "\033[48;2;248;228;218m\033[38;2;0;0;0m",
    "\033[48;2;254;216;177m\033[38;2;0;0;78m",  # 4 light orange
    "\033[48;2;240;128;128m\033[38;2;0;64;63m",  # 8 light coral
    "\033[48;2;255;160;122m\033[38;2;0;0;133m",  # 16 light salmon
    "\033[48;2;171;39;79m\033[38;2;0;216;0m",  # 32 purple
    "\033[48;2;173;216;210m\033[38;2;82;0;0m",  # 64 light blue
    "\033[48;2;132;176;178m\033[38;2;0;0;0m",  # 128 medium orange
    "\033[48;2;144;238;144m\033[38;2;56;0;0m",  # 256 light green
    "\033[48;2;0;128;128m\033[38;2;255;0;0m",  # 512 light teal
    "\033[48;2;177;90;217m\033[38;2;10;40;0m",  # 1024 soft pruple
    "\033[48;2;255;215;0m\033[38;2;255;0;0m",  # 2048 gold
)
present_text_up = (  # upper half text
    "    ",
    " 2  ",
    " 4  ",
    " 8  ",
    " 16 ",
    " 32 ",
    " 64 ",
    "12  ",
    "25  ",
    "51  ",
    "10  ",
    "20  ",
)
present_text_dn = (  # lower half text
    "    ",
    "    ",  # 2
    "    ",  # 4
    "    ",  # 8
    "    ",  # 16
    "    ",  # 32
    "    ",  # 64
    "  8 ",  # 128
    "  6 ",
    "  2 ",
    "  24",
    "  48",
)
# make sure LVWIN is less than 12. see ./config
assert (
    LVWIN < len(present_text_up)
    and LVWIN < len(present_text_dn)
    and LVWIN < len(present_color)
)
# unicode borders
(LU, LD, RU, RD, TL, TR, TU, TD, H, V, X) = (
    " ┌─",
    " └─",
    "─┐ ",
    "─┘ ",
    " ├─",
    "─┤ ",
    "─┬─",
    "─┴─",
    "─",
    " │ ",
    "─┼─",
)
HCELL = len(present_text_up[0])  # length of tile, 4
LEADIN = "### Ctrl+H for Hint, Ctrl+C for exit, Ctrl+Q to explain what this is ###"


class frontend_worker:
    "frontend drawing on the console. console size aware"

    def __init__(self) -> None:
        # be aware of size change
        self.last_size = os.get_terminal_size()

    def update_frame(self, m: np.ndarray, *supplements: str):
        """refresh the console and update values"""
        assert m.shape == (N, N)

        # always add lead-in
        supplements += ("_" * len(LEADIN), LEADIN)

        # estimate spaces on 4 sides
        est_col = len(LU) + len(TU) * (N - 1) + HCELL * N + len(RU)
        est_row = 3 * N + 1 + len(supplements)
        max_col, max_row = os.get_terminal_size()
        nbcspace = max((max_col - est_col) // 2, 0)
        nbcspace2 = max((max_col - est_col - nbcspace), 0)
        nbrspace = max((max_row - est_row - 2) // 2, 0)
        nbrspace2 = max((max_row - est_row - nbrspace), 0)

        CSPACE, RSPACE = " " * nbcspace, (" " * max_col + "\n") * nbrspace
        CSPACE2, RSPACE2 = " " * nbcspace2, (" " * max_col + "\n") * (nbrspace2 - 2)

        # generate outs
        outs = BKGD + FRGD + RSPACE
        outs += (
            CSPACE + LU + (H * HCELL + TU) * (N - 1) + H * HCELL + RU + CSPACE2 + "\n"
        )

        # enum each row
        for i in range(N):
            # upper tile
            outs += CSPACE + V
            for j in range(N):
                outs += (
                    present_color[m[i][j]] + present_text_up[m[i][j]] + BKGD + FRGD + V
                )
            # lower tile
            outs += CSPACE2 + "\n" + CSPACE + V
            for j in range(N):
                outs += (
                    present_color[m[i][j]] + present_text_dn[m[i][j]] + BKGD + FRGD + V
                )
            outs += CSPACE2 + "\n" + CSPACE

            # lower border
            if i != N - 1:
                outs += TL + (H * HCELL + X) * (N - 1) + H * HCELL + TR + CSPACE2 + "\n"
            else:
                outs += (
                    LD + (H * HCELL + TD) * (N - 1) + H * HCELL + RD + CSPACE2 + "\n"
                )

        # add supplement texts
        for s in supplements:
            outs += ("{:^%d}" % (max_col,)).format(s)[:max_col] + "\n"
        outs += RSPACE2

        # clear when resized
        if self.last_size != (max_col, max_row):
            self.last_size = (max_col, max_row)
            clear()

        # flush out string
        print("\033[0;0H\033[?25l")  # seek to begining and hide cursor
        print(outs, end="", flush=True)

    def mainloop(
        self, listener: keyboard.Listener, backend: backend_worker, user="", passwd=""
    ):
        "program mainloop"

        # activate components
        listener.start()
        backend.start()

        # determine initial user
        if user != "":
            actions_queue.put(("set_user", user, passwd))
        else:
            actions_queue.put(("get_current_user",))

        # used time, also span
        span = -1.0
        # showcasing the colors
        m = np.array(((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11), (0, 0, 0, 0)))
        # initial state
        state = "pending"
        # initial frame when started
        self.update_frame(m, f"user: {tr(user)}", f"used time: {tr(span)}")

        # mainloop
        while listener.is_alive():

            # listen the backend
            try:
                code, *args = ack_queue.get(timeout=1 / FPS)
            except Empty:
                # default routine: update time and user
                actions_queue.put(("get_time",))
                actions_queue.put(("get_current_user",))
            except KeyboardInterrupt:
                # shutoff
                break

            # process the received command
            if code == "update_state":
                # align state with backend
                state = args[0]

            elif code == "move":
                if state == "pending":
                    # first step need clearance
                    clear()
                dir, m = args
                self.update_frame(
                    m,
                    f"user: {tr(user)}",
                    f"used time: {tr(span)}" + " (CHEATED)" * (state == "cheating"),
                )

            elif code == "win":
                dir, m, new_rec, last_rec = args
                span, d = new_rec["value"], new_rec["date"]
                span2, d2 = last_rec["value"], last_rec["date"]
                if state == "cheating":
                    self.update_frame(m, "Finished! (CHEATED)")
                elif span < span2:
                    self.update_frame(
                        m,
                        f"Congratulations {tr(user)}!",
                        f"Finished game within {tr(span)} (new record!)",
                        f"your record: {tr(span)} at {d}",
                    )
                else:
                    self.update_frame(
                        m,
                        f"Congratulations {tr(user)}!",
                        f"Finished game within {tr(span)}",
                        f"your record: {tr(span2)} at {d2}",
                    )

            elif code == "fail":
                dir, m = args
                self.update_frame(m, "You failed.")

            elif code == "get_current_user":
                (user,) = args

            elif code == "get_time":
                (span,) = args
                # when pending maintain win/fail result page
                if state != "pending":
                    self.update_frame(
                        m,
                        f"user: {tr(user)}",
                        f"used time: {tr(span)}" + " (CHEATED)" * (state == "cheating"),
                    )
        # mainloop is over
        clear()
        print("shutting down...")
        # stop components
        listener.stop()
        backend.stop()


# test
if __name__ == "__main__":
    clear()
    assert (
        hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    ), "current console doesn't support ANSI escape sequence"
    arg = sys.argv
    user = arg[1] if len(arg) >= 2 else ""
    passwd = arg[2] if len(arg) == 3 else ""
    frontend = frontend_worker()
    # mainloop
    frontend.mainloop(
        keyboard.Listener(on_press=on_press), backend_worker(), user=user, passwd=passwd
    )
