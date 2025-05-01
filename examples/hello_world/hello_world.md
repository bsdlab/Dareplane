# Hello World for Dareplane with python modules

This example will guide you through the process of creating a simple motor imagery task as a Dareplane module and then hook it up with a mock-up data streamer as well as [LSL](https://labstreaminglayer.org/#/) recording.
Completing this example you will have a data source (mockup only), a paradigm providing visual queues and markers and finally recording of markers and streaming data with [LSL](https://labstreaminglayer.org/#/) into an `*.xdf` file.

## Get the Dareplane pyutils

Install the `dareplane-utils` to make use of the default TCP server. E.g. via `pip install dareplane-utils`.

## Building the paradigm module

First, lets decide to call the module `dp-mi-paradigm`. The prefix of `dp-` for Dareplane is arbitrary and you can of course choose not to use it.

### Initialize the project

To start, get the [`dp-strawman-module`](https://github.com/bsdlab/dp-strawman-module) and read the `README.md` therein carefully. After that you should know how to build upon the strawman. So lets rename the relevant folders. The content of our new module folder `./dp-mi-paradigm` should then look like this:

```bash
├── LICENSE
├── README.md
├── api
│   └── server.py
├── configs
├── mi_paradigm
│   ├── main.py
│   └── utils
│       └── logging.py
└── tests
```

### Develop the paradigm

For our paradigm we decide to show simple instructions for motor imagination of left (L) and right ( R) hand movement by displaying letters 'L' and 'R' as well as a fixation cross '+' using [`psychopy`](https://www.psychopy.org/). In addition, we want to send markers to an [LSL](https://labstreaminglayer.org/#/) stream capturing when a direction is shown.

So our `./mi_paradigm/main.py` could look like this.

```python ./mi_paradigm/main.py

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

```

This should be all we need for being able to test the paradigm via `python -m mi_paradigm.main`. Test it like this and make sure it works (especially installing requirements!).

### Wrapping the server around

Next we need to add the server which will allow communication within a Dareplane setup. This requires just a few lines and since we started from the strawman, it actually just requires us to properly import the `run_mi_task` and `Paradigm`, intializing a `Paradigm` instance and adding it to the primary commands dictionary in `./api/server.py`, partially defining the correct `Paradigm` instance.

```python ./api/server
from fire import Fire

from functools import partial
from mi_paradigm.main import run_mi_task, Paradigm
from mi_paradigm.utils.logging import logger

from dareplane_utils.default_server.server import DefaultServer


def main(port: int = 8080, ip: str = "127.0.0.1", loglevel: int = 30):
    pdm = Paradigm()

    logger.setLevel(loglevel)
    logger.debug("Paradigm created")

    # partial is used so taht the function call will use the pdm instance
    pcommand_map = {"RUN": partial(run_mi_task, pdm)}

   # ... rest is left unchanged
```

Now you are ready for the next level of testing, which is to make sure, we can run the task via the server. Just spawn up the server with `python -m api.server` and connect via e.g. `telnet 127.0.0.1 8080`. Then send the `RUN` command in telnet and verify that the paradigm is played correctly.

Once this is successful, you have completed your first Dareplane module. Congratulations !

## Running your module from the control room

It is now time to integrate the `dp-mi-paradigm` with other modules. This is done using the [`dp-control-room`](https://github.com/bsdlab/dp-control-room). If you do not yet have it, clone it from git and place it e.g. in the parent directory of `pd-mi-paradigm`. So that you have the `pd-mi-paradigm` and `pd-control-room` paradigm in the same folder. Make sure to have all dependencies of the control room installed. Try `pip install -r requirements.txt` from within the `pd-control-room` folder.

Then move into the `dp-control-room` directory and create a config at `./configs/mi_experiment.toml` with the following content:

```toml ./configs/mi_experiment.toml
[python]
modules_root = '../'

# -------------------- used modules ---------------------------------------

[python.modules.dp-mi-paradigm]
type = 'paradigm'
port = 8081
ip = '127.0.0.1'
loglevel = 10
```

Then change the config which is loaded by the control room for convenience. So within `./control_room/main.py` we place:

```python ./control_room/main.py

setup_cfg_path: Path = Path("./configs/mi_experiment.toml").resolve()

```

Now spawn up the control_room by calling `python rcr.py` or `python -m control_room.main`. You should now be able to see the control_room at `127.0.0.1:8050` within your browser. Make sure you see the `mi_experiment` section and a `RUN` button. If you click the button, you should see the paradigm being played.

### Composing the module with others

As a final step, we add other modules and create a macro to control all with a single button push. So get the [`dp-mockup-streamer`](https://github.com/bsdlab/dp-mockup-streamer) and the [`dp-lsl-recording`](https://github.com/bsdlab/dp-lsl-recording) module and place them in the same parent directory as the other modules.

```bash
.
├── dp-control-room
├── dp-lsl-recording
├── dp-mockup-streamer
└── dp-mi-paradigm
```

Also install the requirements for the other two modules via `pip install -r requirements.txt` within each of the folders.

Then add the following to the `./configs/mi_experiment.toml` config:

```toml ./configs/mi_experiment.toml
[python]
modules_root = '../'

# -------------------- used modules ---------------------------------------

[python.modules.dp-mi-paradigm]
type = 'paradigm'
port = 8081
ip = '127.0.0.1'
loglevel = 10

[python.modules.dp-mockup-streamer]
type = 'source'
port = 8082
ip = '127.0.0.1'
loglevel = 10

[python.modules.dp-lsl-recording]
type = 'paradigm'
port = 8083
ip = '127.0.0.1'
loglevel = 10


[macros.start_test]
name = 'START_TEST'
description = 'start all modules for simulation'
delay_s = 1
[macros.start_test.default_json]
nrep = 6
[macros.start_test.cmds]
# variable names are arbitrary, the commands will be executes in the same order as they are read by tomllib
com1 = ['dp-mockup-streamer', 'START_RANDOM']
com2 = ['dp-lsl-recording', 'SELECT_ALL']
com4 = ['dp-lsl-recording', 'RECORD']
com5 = ['dp-mi-paradigm', 'RUN', 'nrepetitions=nrep']

[macros.stop]
name = 'STOP_TEST'
description = 'Send a stop command to all involved modules'
[macros.stop.cmds]
com1 = ['dp-lsl-recording', 'STOPRECORD']

```

For more details about how create a config for `dp-control-room`, please be referred to the [README](https://github.com/bsdlab/dp-control-room).

Before we restart the control room to check our new configuration including the macro, we need to start the [LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder). Otherwise the we will not be able to start the control room GUI. (_Note_ - this is a temporary necessity. In later versions of the `dp-lsl-recording` module, this will be done automatically).

Now restart the control room from within `dp-control-room` by using `python rcr.py` and you should see a `Macro` section on the GUI at `127.0.0.1:8050`.
