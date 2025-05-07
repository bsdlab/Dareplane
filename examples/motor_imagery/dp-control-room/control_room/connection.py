import time
from dataclasses import dataclass, field
from pathlib import Path
from socket import SHUT_RDWR, socket
from subprocess import Popen
from typing import Callable

from control_room.processes import close_child_processes, start_container
from control_room.socket import create_socket_client
from control_room.utils.logging import logger


# This is designed for python, so maybe refactor later
@dataclass
class ModuleConnection:
    name: str
    type: str = (
        ""  # a dareplane module type, e.g. control, io_data, io_control, decoding, paradigm    # noqa
    )
    port: int = 0  # the port at the server
    near_port: int = 0  # the port of the client
    ip: str = "127.0.0.1"
    socket_c: socket = None
    host_process: Popen = None
    module_root_path: Path = Path(".")
    kwargs: dict = field(default_factory=dict)
    pcomms: list = field(default_factory=list)
    container_starter: Callable = start_container
    loglevel: int = 10
    retry_connection_after_s: float = 1

    def start_module_server(self):
        self.host_process = self.container_starter(
            self.name,
            self.ip,
            self.port,
            self.loglevel,
            modules_root_path=self.module_root_path,
            start_kwargs=self.kwargs,
        )

    def start_socket_client(self):
        logger.debug(f"{self.name=} - connecting socket to " f"{self.ip}:{self.port}")
        self.socket_c = create_socket_client(
            host_ip=self.ip,
            port=self.port,
            retry_connection_after_s=self.retry_connection_after_s,
        )

        # Time-out as non of the sockets should block indefinitely
        self.socket_c.setblocking(0)

        # read out the actual socket -> if port == 0, a random free port
        # was assigned
        self.near_port = self.socket_c.getsockname()[1]

        # There might be a response / confirmation of the connetion
        try:
            self.socket_c.settimeout(1)
            # msg = self.socket_c.recv(2048 * 8)
            fragments = []
            while True:
                chunk = self.socket_c.recv(1024)
                if not chunk:
                    break
                fragments.append(chunk)
            msg = b"".join(fragments)

            logger.debug(f"connection returned: {msg.decode()}")
            self.socket_c.settimeout(None)
        except ConnectionResetError as err:
            logger.debug(
                f"Connection refused for - {self.name=}, {self.ip=}, {self.port=}"
            )
            raise err
        except TimeoutError as err:
            logger.debug(f"No response upon connection for {self.name=} - {err=}")
        except Exception as err:
            logger.debug(f"Other error upon connection for {self.name=}, {err=}")
            raise err

    def stop_process(self):
        if self.host_process:
            closed = close_child_processes(self.host_process)
            if closed == 0:
                self.host_process = None

    # Just have this method to have a consistent name with stop_process
    def stop_socket_c(self):
        try:
            logger.debug(
                f"{self.name} trying to gracefully shurtdown " f"{self.socket_c}"
            )
            self.socket_c.shutdown(SHUT_RDWR)
        except OSError:
            logger.debug(
                f"{self.name} caught OSError on connection.shutdown"
                " - connection already closed?"
            )

        self.socket_c.close()

    def __del__(self):
        if self.host_process:
            self.stop_process()
        if self.socket_c:
            self.stop_socket_c()

    def get_pcommands(self):
        """Populate self.pcommands as a list of possible commands"""

        logger.debug(f"Getting PCOMMS from {self.name}")
        self.socket_c.sendall(b"GET_PCOMMS")
        time.sleep(0.1)  # allow for processing on the server
        # logger.debug(f"Reading for receive")

        msg = self.socket_c.recv(2048 * 8)
        logger.debug(f"Received msg for pcommands: {msg.decode()}")
        self.pcomms = msg.decode().split("|")


def noop(*args, **kwargs):
    pass


@dataclass
class ModuleConnectionExe(ModuleConnection):
    exe_path: str = ""
    pcomms_defaults: dict = field(default_factory=dict)
    container_starter: Callable = noop

    def get_pcommands(self):
        logger.debug(
            "Pcomms for exe modules currently need to be provided by the configs"
            "This will change to an analogeous behaviour to the python modules"
            " once the AO communication is reworked. Currently this means that "
            "*.exe modules have to be started manually."
        )

    def start_module_server(self):
        # Noop at the moment, implement this after AO communication rework
        pass

    def stop_process(self):
        # Noop at the moment, implement this after AO communication rework
        pass
