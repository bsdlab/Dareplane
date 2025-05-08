import threading
import time

import mne
import numpy as np
import pylsl
import pytest

from mockup_streamer.main import MockupStream, glob_path_to_path_list


@pytest.fixture(scope="session")
def mne_file(
    tmp_path_factory,
):  # tmp_path_factory is a fixture provided by pytest
    """Create files to test the file load"""

    info = mne.create_info(["A", "B", "C"], 100, ["eeg"] * 3)
    data = np.random.randn(3, 1000)
    raw = mne.io.RawArray(data, info)

    raw.set_annotations(
        mne.Annotations([0, 0.1, 6, 10], [0, 0, 0, 0], ["start", "m1", "m2", "end"])
    )

    fn = tmp_path_factory.mktemp("data") / "raw.fif"
    raw.save(fn)
    return fn


def test_random_data_setup():

    cfg = dict(sampling_freq=100, n_channels=2, pre_buffer_s=300, stream_name="testA")

    cfg_with_marker = dict(
        sampling_freq=100,
        n_channels=3,
        pre_buffer_s=300,
        stream_name="testA",
        markers=dict(
            marker_stream_name="mock_random1",
            t_interval_s=1,
            values=["a", "b", "c"],
        ),
    )

    # assert that the data generation is as expected
    streamer = MockupStream(name="test", cfg=cfg)
    assert streamer.buffer.shape == (30_000, 2)
    assert streamer.outlet_mrk is None

    streamer_mrk = MockupStream(name="test2", cfg=cfg_with_marker)
    assert streamer_mrk.markers.shape == (300, 2)
    assert (np.unique(streamer_mrk.markers[:, 1]) == ["a", "b", "c"]).all()
    assert streamer_mrk.markers[2, 1] == "c"
    assert streamer_mrk.markers[3, 1] == "a"
    assert streamer_mrk.markers[4, 1] == "b"
    assert isinstance(streamer_mrk.outlet_mrk, pylsl.StreamOutlet)


def test_pushing_multiple_streams():
    cfg_a = dict(sampling_freq=100, n_channels=2, pre_buffer_s=1, stream_name="testA")

    cfg_b = dict(
        sampling_freq=200,
        n_channels=3,
        pre_buffer_s=30,
        stream_name="testB",
        markers=dict(
            marker_stream_name="mock_random1",
            t_interval_s=1,
            values=["a", "b", "c"],
        ),
    )

    streams = [
        MockupStream(name="testA", cfg=cfg_a),
        MockupStream(name="testB", cfg=cfg_b),
    ]

    # reset clocks
    for sm in streams:
        sm.t_start_s = pylsl.local_clock()

    time.sleep(1.2)

    for sm in streams:
        sm.push()

    assert streams[0].buffer_i == 0  # will have a new set loaded
    assert streams[0].n_pushed == 0
    assert streams[1].buffer_i > 200
    assert streams[1].buffer_i == streams[1].n_pushed
    assert streams[1].t_start_s + 1 < streams[0].t_start_s


def test_sender_receiver():

    cfg = dict(
        sampling_freq=200,
        n_channels=3,
        pre_buffer_s=30,
        stream_name="test_sr",
        markers=dict(
            marker_stream_name="test_marker_sr",
            t_interval_s=1,
            values=["a", "b", "c", "d", "e"],
        ),
    )
    sm = MockupStream(name="test", cfg=cfg)

    buffer_data = []
    buffer_mrk = []

    streams = pylsl.resolve_streams()
    idx_test = [i for i, s in enumerate(streams) if s.name() == "test_sr"][0]
    idx_marker = [i for i, s in enumerate(streams) if s.name() == "test_marker_sr"][0]

    th, ev = start_listener_thread(streams[idx_test], buffer_data)
    thm, evm = start_listener_thread(streams[idx_marker], buffer_mrk)

    # reset then send two chunks
    sm.t_start_s = pylsl.local_clock()
    for _ in range(20):  # window needs to be long enough to include at least
        # one marker
        time.sleep(0.1)
        sm.push()

    ev.set()
    evm.set()

    time.sleep(0.3)

    th.join()
    thm.join()

    # assert that last data in buffer agrees with idx of streamer
    last_data = sm.buffer[sm.buffer_i - 1, :]
    assert np.allclose(last_data, buffer_data[-1][0][-1])

    last_marker = sm.markers[sm.markers[:, 0] < sm.buffer_i][-1, 1]
    assert last_marker == buffer_mrk[-1][0][0][0]


def start_listener_thread(
    info: pylsl.StreamInfo, buffer: list
) -> tuple[threading.Thread, threading.Event]:
    stop_event = threading.Event()
    stop_event.clear()

    def listener_thread(info, buffer):
        inlet = pylsl.StreamInlet(info)
        while not stop_event.is_set():
            time.sleep(0.1)
            res = inlet.pull_chunk()
            if res[0] != []:
                buffer.append(res)

    thread = threading.Thread(target=listener_thread, args=(info, buffer))
    thread.start()
    return thread, stop_event


def test_mne_file_read(mne_file):

    cfg = dict(
        file_path=mne_file,
        stream_name="mock_EEG_stream_1",
        mode="repeat",
        type="regular",
        sampling_freq="derive",
        stream_type="EEG",
        select_channels=["A", "C"],
    )

    sm = MockupStream(name="test", cfg=cfg, files=glob_path_to_path_list(cfg))

    assert (sm.markers[:, 1] == ["start", "m1", "m2", "end"]).all()
    assert sm.buffer.shape == (1000, 2)
    assert sm.sfreq == 100
    assert isinstance(sm.outlet, pylsl.StreamOutlet)
    assert isinstance(sm.outlet_mrk, pylsl.StreamOutlet)

    # Without limitation on the channels
    cfg = dict(
        file_path=mne_file,
        stream_name="mock_EEG_stream_1",
        mode="repeat",
        type="regular",
        sampling_freq="derive",
        stream_type="EEG",
    )

    sm = MockupStream(name="test", cfg=cfg, files=glob_path_to_path_list(cfg))
    assert sm.buffer.shape == (1000, 3)


# def test_xdf_file_read():
#     # What would be a good way of creating an xdf fixture? > provide a sample
#     # xdf as asset?
#     print("XDF test not implemented yet")


# --> think about how to best include example with the proprietary file formats
# def test_brainvision_file_read():
#     pass
