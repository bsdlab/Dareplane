# Mockup_streamer

<!--toc:start-->
- [Mockup_streamer](#mockupstreamer)
  - [Running the module](#running-the-module)
  - [Config](#config)
    - [Config options](#config-options)
    - [Running in a shell](#running-in-a-shell)
      - [As standalone python](#as-standalone-python)
      - [As TCP server](#as-tcp-server)
      - [Connecting](#connecting)
  - [Configure](#configure)
<!--toc:end-->

__NOTE__: This module requires python `3.11` as it loads the config using `tomlib`. If you want to use an older python version, you can simply adjust the import to use `toml` instead.

This is a module for the [Dareplane](https://github.com/bsdlab/Dareplane) project which provides mockup streaming from recorded data (currently only EEG from BrainVision files) or randomly generated data.

## Running the module

As for all Dareplane modules, you can have this run standalone, via a TCP server or here also as a Docker container. The core interaction is meant to take place via the TCP server.

## Config

The configuration options can be found under `./config` in the `streams.toml` or `streaming_docker.toml` depending whether you plan to run as a docker container or not. For most use cases, running in a `shell` is sufficient and should be the prefered way.

### Config options

```toml

```

### Running in a shell

#### As standalone python

A simple CLI is implemented in `./mockup_streamer/main.py` for the following function

```python
def run_stream(stop_event: threading.Event = threading.Event(),
               stream_name: str = "",
               log_push: bool = False,
               random_data: bool = True,
               **kwargs) -> int:
```

This will run the standard configuration located in `./config/streams.toml`.

To simply spawn a quick stream of random data with CLI control over the parameters, use this:

```bash
python -m mockup_streamer.random_cli
# or this for help about parameters
python -m mockup_streamer.random_cli --help
```

#### As TCP server

To spawn it, simply run from this directory

```bash
python -m api.server
```

Note: By default, this will bind to port `8080` on the local host. You might want to change this within `./api/server.py`.


#### Connecting

Once the server is running (either in a shell or in a docker container), you can send the primary commands `START` and `STOP` to the server, which will start or stop streaming data via LSL.
To do so connect a socket, e.g. via `telnet` from your terminal as

```bash
telnet 127.0.0.1 8080
```

## Configure

All configuration can be found under `./config/`. Check e.g. `./config/streaming.toml` for setting of the mockup stream, and where the source files are globbed from.

## TODO
- [ ] Improve documentation
