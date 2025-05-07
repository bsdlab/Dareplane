from fire import Fire
import time
import random
import pylsl
from psychopy.visual import TextStim, Window

from mi_paradigm.utils.logging import logger

logger.setLevel(10)

BG_COLOR = (0, 0, 0)
TEXT_COLOR = (1, 0, 0)

# timing parameters
t_pre = 1
t_show = 1
t_post = 1


# LSL outlet - for convenience we also display to the logger
class Outlet:
    def __init__(self):
        self.logger = logger
        info = pylsl.StreamInfo(name="markers", channel_format="string")
        self.outlet = pylsl.StreamOutlet(info)

    def push_sample(self, sample: str):
        self.logger.debug(f"Pushing sample {sample}")
        self.outlet.push_sample([sample])

# Sometimes is is more convenient to have a paradigm instance which can be
# kept alive globally. This especially holds if the server we will wrap around
# this module will not call psychopy in a subprocess
# --> So for the example, add a class
class Paradigm:
    def __init__(self):
        self.open_window()

    def open_window(self):
        self.win = Window((800, 600), screen=1, color=BG_COLOR)
        self.rstim = TextStim(win=self.win, text="R", color=TEXT_COLOR)
        self.lstim = TextStim(win=self.win, text="L", color=TEXT_COLOR)
        self.fix_cross = TextStim(win=self.win, text="+", color=TEXT_COLOR)

    def close_window(self):
        self.win.close()


def run_mi_task(paradigm: Paradigm, nrepetitions: int = 4) -> int:
    outlet = Outlet()
    win = paradigm.win
    fix_cross = paradigm.fix_cross
    rstim = paradigm.rstim
    lstim = paradigm.lstim

    fix_cross.draw()
    win.flip()

    # create a balanced set
    directions = ["R"] * (nrepetitions // 2) + ["L"] * (nrepetitions // 2)
    random.shuffle(directions)

    for i, dir in enumerate(directions):
        fix_cross.draw()
        win.flip()
        outlet.push_sample("new_trial")

        time.sleep(t_pre)

        if dir == "R":
            rstim.draw()
        else:
            lstim.draw()

        win.flip()
        outlet.push_sample(dir)

        # clear screen and sleep for post
        time.sleep(t_show)
        win.flip()
        outlet.push_sample("cleared")

        win.flip()
        time.sleep(t_post)

    return 0


if __name__ == "__main__":

    from functools import partial
    pdm = Paradigm()
    Fire(partial(run_mi_task, pdm))