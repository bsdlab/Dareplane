import threading
import time

import psutil
import pytest

from control_room.connection import ModuleConnection
from control_room.utils.logging import logger
from tests.resources.tmodule import start_container
from tests.resources.tserver import run_server, run_slow_startup_server

logger.setLevel(10)


@pytest.fixture
def module_with_thread_for_tserver():
    # setup
    sev = threading.Event()
    thread = threading.Thread(
        target=run_server,
        kwargs=dict(ip="127.0.0.1", port=5050, stop_event=sev),
    )
    thread.start()

    con = ModuleConnection(name="test", ip="127.0.0.1", port=5050)

    con.start_socket_client()

    # The test
    yield con

    # Teardown of threads
    logger.debug("Starting thread teardown")
    con.socket_c.sendall(b"CLOSE\r\n")
    con.stop_socket_c()

    logger.debug("Starting thread teardown")
    thread.join()


def test_socket_connection(module_with_thread_for_tserver):
    con = module_with_thread_for_tserver
    con.get_pcommands()
    assert tuple(con.pcomms) == ("START", "GET_PCOMMS", "STOP", "CLOSE")


@pytest.fixture
def slow_server_thread() -> tuple[threading.Thread, threading.Event]:

    sev = threading.Event()
    thread = threading.Thread(
        target=run_slow_startup_server,
        kwargs=dict(ip="127.0.0.1", port=5051, stop_event=sev),
    )

    yield thread, sev

    sev.set()
    thread.join()


def test_retry_connection_after_s_for_slow_startup(slow_server_thread):
    thread, sev = slow_server_thread
    thread.start()

    # Quick connection should fail
    with pytest.raises(OSError):
        conq = ModuleConnection(
            name="test_slow", ip="127.0.0.1", port=5051, retry_connection_after_s=0.3
        )
        conq.start_socket_client()

    # slow start-up takes 5 seconds -> 3 seconds for retry with 3 retries should be enough
    con = ModuleConnection(
        name="test_slow", ip="127.0.0.1", port=5051, retry_connection_after_s=3
    )

    con.start_socket_client()

    con.get_pcommands()

    time.sleep(0.5)  # wait a bit to ensure response arrived

    # Close before assert could break the test
    con.socket_c.sendall(b"CLOSE\r\n")
    con.stop_socket_c()

    assert (
        "SLOWSERVERTEST" in con.pcomms
    ), f"Did not get the expected pcomms from the server - {con.pcomms=}"


@pytest.fixture
def module_connection_with_running_process():
    # setup
    con = ModuleConnection(
        name="test",
        ip="127.0.0.1",
        port=5051,
        container_starter=start_container,
    )

    con.start_module_server()

    # testing
    yield con

    # teardown
    con.stop_process()
    try:
        host_pid = con.host_process.pid
        hostp = psutil.Process(host_pid)
        hostp.kill()

    except (psutil.NoSuchProcess, AttributeError):
        logger.debug(f"Process {con.host_process=} already killed?")


def test_subprocess(module_connection_with_running_process):
    con = module_connection_with_running_process

    assert con.host_process is not None
    host_pid = con.host_process.pid
    hostp = psutil.Process(host_pid)

    con.stop_process()
    time.sleep(0.5)

    # Second condition added for testing on windows
    try:
        assert con.host_process is None and hostp.status() == "zombie"
    finally:
        hostp.kill()

    logger.info(f"{hostp=}")


# def test_just_run():
#     run_server(port=8080, ip="127.0.0.1")
