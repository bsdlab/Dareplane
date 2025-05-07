from pathlib import Path
from dareplane_utils.logging.server import LogRecordSocketReceiver

logfile = Path("dareplane_cr_all.log")
if __name__ == "__main__":
    rcv = LogRecordSocketReceiver(logfile=logfile)
    rcv.serve_until_stopped()
