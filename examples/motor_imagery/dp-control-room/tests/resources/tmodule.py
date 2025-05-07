# A dummy module for testing
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from socket import socket
from subprocess import Popen
from typing import Callable

from control_room.utils.logging import logger

# Mockup for ./control_room/processes.py start_container()


def start_container(
    name: str,
    ip: str = "127.0.0.1",
    port: int = 5050,
    loglevel: int = 10,
    **kwargs,
):
    cmd = f"python -m tests.resources.tserver --port={port} --ip={ip}"

    return subprocess.Popen(cmd, shell=True)


@dataclass
class DummySocker:
    ip: str = "127.0.0.1"
    port: int = 0
    is_ready: bool = False

    def sendall(self, msg):
        if self.is_ready and msg == "UP":
            return 1
        # logger.info(f"Sending {msg=} to socket {self.ip}:{self.port}")
        return 0


@dataclass
class DummyModule:
    name: str
    type: str = (
        ""  # a dareplane module type, e.g. control, io_data, io_control, decoding, paradigm    # noqa
    )
    port: int = 0
    near_port: int = 0
    ip: str = "127.0.0.1"
    socket_c: None | socket = None
    host_process: None | Popen = None
    module_root_path: Path = Path(".")
    kwargs: dict = field(default_factory=dict)
    pcomms: list = field(default_factory=list)
    container_starter: Callable = start_container
    is_ready: bool = False

    def start_module_server(self):
        logger.debug("starting module server")

    def start_socket_client(self):
        logger.debug(f"starting socket client at {self.ip}:{self.port}")
        self.socket_c = DummySocker(self.ip, self.port, self.is_ready)

    def stop_process(self):
        logger.debug("stopping process")

    # Just have this method to have a consistent name with stop_process
    def stop_socket_c(self):
        logger.debug("stopping socket")

    def get_pcommands(self):
        self.pcomms = "START|INIT|STOP|RUN_BLOCK".split("|")


def get_dummy_modules():
    return [
        DummyModule(
            name="module1", type="decoding", port=8080, is_ready="True"
        ),
        DummyModule(name="module2", type="control", port=8081, is_ready=True),
        DummyModule(name="module3", type="control", port=8082, is_ready=True),
        DummyModule(name="module4", type="control", port=8083),
        DummyModule(name="module5", type="control", port=8084),
        DummyModule(name="module6", type="control", port=8085),
    ]
