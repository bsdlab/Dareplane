#  Note this still follows the old setup structure before dareplane_utils was created
from functools import partial

from dareplane_utils.default_server.server import DefaultServer
from fire import Fire

from mockup_streamer.main import run_mockup_streamer_thread
from mockup_streamer.utils.logging import logger


def run_server(port: int = 8080, ip: str = "127.0.0.1", loglevel: int = 10, **kwargs):
    logger.setLevel(loglevel)

    pcommand_map = {
        "START": partial(run_mockup_streamer_thread, **kwargs),
        "START_RANDOM": partial(run_mockup_streamer_thread, random_data=True, **kwargs),
    }

    logger.debug("Initializing server")
    server = DefaultServer(port, ip=ip, pcommand_map=pcommand_map, name="mockup_server")

    # initialize to start the socket
    server.init_server()

    # start processing of the server
    logger.debug("starting to listen on server")
    server.start_listening()
    logger.debug("stopped to listen on server")

    return 0


if __name__ == "__main__":
    Fire(run_server)
