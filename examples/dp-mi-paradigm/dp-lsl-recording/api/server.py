from dareplane_utils.default_server.server import DefaultServer
from fire import Fire

from lsl_recorder.main import init_lsl_recorder_com
from lsl_recorder.utils.logging import logger


def main(port: int = 8080, ip: str = "127.0.0.1", loglevel: int = 10):
    logger.setLevel(loglevel)

    # Get the communication manager
    lslm = init_lsl_recorder_com()

    pcommand_map = {
        "SELECT_ALL": lslm.select_all,
        "SET_SAVE_PATH": lslm.set_recording_file,
        "UPDATE": lslm.update,
        "RECORD": lslm.record,
        "STOPRECORD": lslm.stop,
    }

    server = DefaultServer(
        port, ip=ip, pcommand_map=pcommand_map, name="lsl_control_server"
    )

    # initialize to start the socket
    server.init_server()
    # start processing of the server
    server.start_listening()

    return 0


if __name__ == "__main__":
    Fire(main)
