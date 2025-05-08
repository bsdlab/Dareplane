# import toml as tomllib
from pathlib import Path

from lsl_recorder.controller import LSLRecorderCom

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

cfg = toml_load("./configs/lsl_conf.toml")


def init_lsl_recorder_com(
    lsl_recording_path: Path = Path(cfg["lsl_recording_path"]),
) -> LSLRecorderCom:
    return LSLRecorderCom(data_root=lsl_recording_path)
