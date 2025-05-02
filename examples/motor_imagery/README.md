# Strawman Module

This is a strawman module which can simply be copied to create a new [`Dareplane`](https://github.com/bsdlab/Dareplane) module quickly.

# How to create a module

This is a quick introduction of how you can approach module development in `python` using this strawman.

#### Step 1 - copy the strawman

Start of by copying the parent folder of this content to a new folder, e.g. `test_module`.

This will provide you with the following content:

```bash
.
├── README.md             # this file
├── api                   │
└── server.py         # the server used to control the module
├── configs               # folder for potential configurations of the module
├── mymodule              # the modules source folder
│   ├── main.py           # a script / main entry point for your moduel
│   └── utils             # folder for utilities of the module
│       └── logging.py    # logging utility, getting a logger from the dareplane_utils module and making it available on a module level
└── tests                 # folder for potential unit tests, e.g. using pytest
```

#### Step 2 - start a new git for versioning

Delete the `.git` folder and change the `README.md` content. Rename the `mymodule` folder to the name of your module, e.g. `test_module`.
Then initialize a new git repository and start with your development process.

#### Step 3 - develop the python side of your code

Create your code like you would for any python standalone module your are working on. The endpoint of this development step should be functionality which can be invoked as you would for a regular python script. E.g. `python -m .test_module.main --some-argument some_value`.

At this stage you can make certain your module works purely in terms of python coding. Of course you can also create unit tests at this stage to ensure easy retesting of core functionality.

#### Step 4 - add the functionality to the server

In this step we make the functionality we implemented in step 3 available through a TCP server.
The strawman you copied already provides the following template:

```python
from fire import Fire

from mymodule.main import run_hello_world
from mymodule.utils.logging import logger

from dareplane_utils.default_server.server import DefaultServer


def main(port: int = 8080, ip: str = "127.0.0.1", loglevel: int = 10):
    logger.setLevel(loglevel)

    pcommand_map = {
        "START": lambda x: 0,  # here you would hook up the functionality of your module to the server
    }

    server = DefaultServer(
        port, ip=ip, pcommand_map=pcommand_map, name="mymodule_control_server"
    )

    # initialize to start the socket
    server.init_server()
    # start processing of the server
    server.start_listening()

    return 0
```

###### Adjusting the input

All functionality will be managed within the server for which the `DefaultServer` should be well equipped as a starting point. Your functionality usually will be available as a function or a class with associated methods. Just import them into the `./api/server.py`. E.g. changing to this

```python ./api/server.py
from test_module.main import run_hello_world
```

Also rename `mymodule` to `test_module` for the importing of the logger and the name passed to the creation of the `DefaultServer` instance.

###### Adding the functionality to the primary commands

The basic concept of Dareplane is to use what we call primary commands to invoke and control the functionality of a module.

This means the interpretation of a single string with a function or method call. E.g. if we want to connect the primary command `START` with calling `run_hello_world`, we would add it as:

```python ./api/server.py

    pcommand_map = {
        "START": run_hello_world,
    }

```

Note: You want to link the function and not a function call (no `run_hello_world()`).

**Important**: Currently any function or method hooked up needs to return either an `int`, a `threading.Thread` or a `subprocess.Popen` subprocess. The server will then manage the life time of spawned threads or subprocesses.

Now the server is ready for testing. Spawn the server manually using:

```bash
python -m api.server
```

Then from another terminal you can connect to the server using `telnet` and try the primary commands:

```bash
telnet 127.0.0.1 8080
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Connected to mymodule_control_server
START
```

The default server also implements a `STOP` command to stop any thread or subprocess which the server has in its book keeping. Additionally, a `CLOSE` command is implemented by default and will close the server. For integrating the module, the default server provides a `GET_PCOMMS` implementation, which will send the list of commands you specified + `STOP` and `CLOSE`. This is used within the control_room module (used to compose various Dareplane modules) and allows for arbitrary command name choices. You just need to reflect them properly later, when setting up the module as part of a whole system. So better choose simple and indicative names. There is not restrictions to using all capital letters either. But given the global nature of these commands, it feels natural.

Note that the communication via primary commands allows to send arbitrary json payloads. So sending `START|{"some": "json"}` would result in a function call of the form `run_hello_world(**{"some": "json"})`.

**Congratulations** you have now a working module which can be controlled from within the control_room module and can be composed within a system of modules.
