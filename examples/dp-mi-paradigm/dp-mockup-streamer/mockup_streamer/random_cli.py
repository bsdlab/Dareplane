# Expose a few parameters usually accessible via config as a CLI
import threading

from fire import Fire

from mockup_streamer.main import run_random


def cli(
    n_channels: int = 10,
    sfreq: int = 100,
    pre_buffer_s: int = 300,
    stream_name: str = "mockup_random",
    markers_t_s: int = 1,
    marker_values: list = ["a", "b", "c"],
):
    """A simple CLI to spawn an LSL mockup stream with random data

    Parameters
    ----------
    n_channels : int
        number of channels

    sfreq : int
        sampling frequency

    pre_buffer_s : int
        number of samples to be pre-generated, after streaming, another
        set will be generated

    stream_name : str
        name of the stream

    markers_t_s : int
        time interval of markers

    marker_values : list
        values of markers

    """
    cfg = dict(
        sfreq=sfreq,
        n_channels=n_channels,
        pre_buffer_s=pre_buffer_s,
        stream_name=stream_name,
        markers_t_s=markers_t_s,
        marker_values=marker_values,
    )
    stop_event = threading.Event()
    stop_event.clear()
    _ = run_random(stop_event, **cfg)


if __name__ == "__main__":
    Fire(cli)
