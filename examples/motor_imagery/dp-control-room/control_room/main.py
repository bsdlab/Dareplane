import subprocess
import threading
import time
from pathlib import Path

import psutil
from fire import Fire
from waitress import serve

from control_room.callbacks import CallbackBroker
from control_room.connection import ModuleConnection, ModuleConnectionExe
from control_room.gui.app import build_app
from control_room.utils.logging import logger
from tests.resources.tmodule import get_dummy_modules

# --- For backwards compatibility with python < 3.11
try:
    import tomllib

    def toml_load(file: Path):
        return tomllib.load(open(file, "rb"))

except ImportError:
    try:
        import toml

        def toml_load(file: Path):
            return toml.load(open(file, "r"))

    except ImportError:
        raise ImportError(
            "Please install either use python > 3.11 or install `toml` library"
            "to able to parse the config files."
        )


logger.setLevel(10)

setup_cfg_path: Path = Path("./configs/mi_experimental.toml").resolve()

def test_dummy(debug: bool = True):
    cfg = toml_load(setup_cfg_path)
    modules = get_dummy_modules()
    for m in modules:
        m.get_pcommands()
        m.start_socket_client()
        print(m)

    app = build_app(modules, macros=cfg.get("macros", None))
    app.run_server(debug=debug)


def initialize_python_modules(mod_cfgs: dict) -> list[ModuleConnection]:
    connections = []

    # Python modules
    for module_name, module_cfg in mod_cfgs["modules"].items():
        connections.append(
            ModuleConnection(
                name=module_name,
                module_root_path=Path(mod_cfgs["modules_root"]),
                **module_cfg,
            )
        )

    return connections


def initialize_exe_modules(mod_cfgs: dict) -> list[ModuleConnection]:
    connections = []

    # Python modules
    for module_name, module_cfg in mod_cfgs["modules"].items():
        connections.append(
            ModuleConnectionExe(
                name=module_name,
                exe_path=Path(module_cfg["path"]),
                ip=module_cfg["ip"],
                port=module_cfg["port"],
                pcomms=list(module_cfg["pcomms"].keys()),
                pcomms_defaults=module_cfg["pcomms"],
            )
        )

    return connections


def close_down_connections(mod_connections: list[ModuleConnection]):
    # Close down
    for conn in mod_connections:
        if conn.socket_c:
            # API connection
            conn.stop_socket_c()

        # the server process
        if conn.host_process:
            conn.stop_process()


def run_control_room(setup_cfg_path: Path = setup_cfg_path, debug: bool = True):
    cfg = toml_load(setup_cfg_path)

    connections = []
    log_server = psutil.Process(
        subprocess.Popen("python -m control_room.utils.logserver", shell=True).pid
    )
    cbb_th = None

    try:
        # Other modules
        if "exe" in cfg.keys():
            connections += initialize_exe_modules(cfg["exe"])

        if "python" in cfg.keys():
            connections += initialize_python_modules(cfg["python"])

        # start the module servers - spawning the processes
        for conn in connections:
            logger.debug(f"Starting module server for {conn.name=}")
            conn.start_module_server()

        time.sleep(0.5)

        # connect clients to the servers
        for conn in connections:
            logger.debug(f"Starting socket client for {conn.name=}")
            conn.start_socket_client()

            logger.debug(f"Getting PCOMMS for {conn.name=}")
            # request primary commands
            conn.get_pcommands()

        # hook up the callback broker
        logger.debug("Starting CallbackBroker thread")
        cbb_stop = threading.Event()
        cbb_stop.clear()

        # prepare the connection socket timeouts to be quicker
        for c in connections:
            c.socket_c.settimeout(0.001)

        cbb = CallbackBroker(
            mod_connections={c.name: c for c in connections},
            stop_event=cbb_stop,
        )
        logger.info(
            f"CallbackBroker has following modules connected: {list[cbb.mod_connections.keys()]}"
        )
        cbb_th = threading.Thread(target=cbb.listen_for_callbacks)
        cbb_th.start()

        # Create the dash app
        app = build_app(connections, macros=cfg.get("macros", None))

        # Note: debug True will lead to conflicts with sockets already being used
        # since dash will run the script to this point another time
        # Use the test_dummy for GUI development instead

        # for the debugging Flask server
        # app.run_server(debug=True)

        # for a lightweight production server
        serve(app.server, port=8050)

    finally:
        if cbb_th:
            logger.debug("Stopping callback broker")
            cbb_stop.set()
            cbb_th.join()

        logger.debug("Closing down connections")
        close_down_connections(connections)

        logger.debug("Terminating log server")
        log_server.terminate()
        time.sleep(0.1)

        # check if the log server is still running
        if psutil.pid_exists(log_server.pid):
            log_server.kill()


if __name__ == "__main__":
    Fire(run_control_room)
