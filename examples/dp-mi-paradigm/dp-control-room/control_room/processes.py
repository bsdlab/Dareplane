import subprocess
import time
from pathlib import Path
from sys import platform

import psutil

from control_room.utils.logging import logger

# Used to separate multiple shell commands in one string
COMMAND_SEP_MAP = {
    "darwin": ";",
    "win32": "&",
    "linux": ";",
    "linux2": ";",
}


def close_child_processes(process: subprocess.Popen) -> int:
    """Close all child processes of a Popen instance"""
    parent_ps = psutil.Process(process.pid)
    max_iter = 5
    i = 0

    while parent_ps and parent_ps.children != [] and i <= max_iter:
        if i > 0:
            time.sleep(0.2)
        try:
            for ch in parent_ps.children():
                logger.debug(f"Sending kill to child process={ch}")
                ch.kill()
        except psutil.NoSuchProcess:
            logger.debug(f"Process {process.pid} no longer existing")
            # break as no need to continue
            break

        i += 1

    logger.debug(f"Sending kill to parent process={parent_ps}")
    parent_ps.kill()

    return 0


def start_container(
    module_name: str,
    ip: str,
    port: int,
    loglevel: int = 10,
    modules_root_path: Path = Path("."),
    start_kwargs: dict = {},
) -> subprocess.Popen:
    """
    Given the configs for python, create subprocesses running the given modules

    Returns
    -------
    subprocess.Popen
    """

    modpath = modules_root_path.joinpath(module_name)
    assert modpath.exists(), f"not a valid path {modpath}"

    logger.info(f"Spawning {module_name=} @ {ip}:{port} with {start_kwargs=}")

    cmd = (
        f"cd {modpath.resolve()}{COMMAND_SEP_MAP[platform]} "
        "python -m api.server "
        f"--port={port} --ip={ip} --loglevel={loglevel}"
        + " "
        + " ".join([f"--{k}={v}" for k, v in start_kwargs.items()])
    )

    # For now, this just starts python containers
    # [ ] TODO implement this for general containers, including Docker

    logger.debug(f"Running Popen with {cmd=}")
    return subprocess.Popen(cmd, shell=True)
