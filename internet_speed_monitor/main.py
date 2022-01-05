import logging
from pathlib import Path
from pprint import pprint
from typing import Any

import speedtest as st

# Set up log file configuration for global use in the script.
log_filename = f"{Path(__file__).stem}.log"
script_filename = Path(__file__).name
logging.basicConfig(
    filename=log_filename,
    filemode="a",
    level=logging.DEBUG,
    format=f"[%(asctime)s] {{{script_filename}:%(lineno)d}} "
    f"%(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def add_log_header() -> None:
    """Add log header to log."""
    with open(log_filename, "a") as f:
        f.write(f"\n\n<<< RUNNING {script_filename} >>>\n")


def add_log_footer() -> None:
    """Add log footer to log."""
    with open(log_filename, "a") as f:
        f.write(f"<<< SCRIPT COMPLETE {script_filename} >>>\n")


def plog(logging_level: int, object_to_log: Any) -> None:
    """Pretty logging for iterables.
    Log each item or key-value pair on a single line."""
    if isinstance(object_to_log, dict):
        for (key, value) in object_to_log.items():
            log.log(logging_level, f"{key}: {value}")
    if isinstance(object_to_log, (tuple, list)):
        for item in object_to_log:
            log.log(logging_level, f"{item}")
    else:
        log.log(logging_level, f"{object_to_log}")


class SpeedTest:
    def __init__(
        self,
    ) -> None:
        speed_test = st.Speedtest()

        log.info("Searching for best server...")
        try:
            server_stat_dict = speed_test.get_best_server()
            log.info("Best server found!")
            plog(10, server_stat_dict)
        except Exception as error:
            log.error(f"Something went wrong when finding a server.\nError - {error}")
            raise error
        self._server_stats = server_stat_dict

        log.info("Retrieving download speed...")
        try:
            download_value = speed_test.download()
            log.info("Download speed received!")
            plog(10, download_value)
        except Exception as error:
            log.error(f"Unable to determine download speed.\nError - {error}")
            raise error
        self._downloads = download_value

        log.info("Retrieving upload speed...")
        try:
            upload_value = speed_test.upload()
            log.info("Upload speed received!")
            plog(10, upload_value)
        except Exception as error:
            log.error(f"Unable to determine upload speed.\nError - {error}")
            raise error
        self._uploads = upload_value

    @property
    def server_stats(self) -> dict[str, Any]:
        return self._server_stats

    @property
    def download_speed(self) -> float:
        return self._downloads

    @property
    def upload_speed(self) -> dict[str, Any]:
        return self._uploads


if __name__ == "__main__":

    add_log_header()
    speed_test = SpeedTest()
    server_stats = speed_test.server_stats
    downloads = speed_test.download_speed
    uploads = speed_test.upload_speed
    add_log_footer()

    pprint(server_stats)
    pprint(downloads)
    pprint(uploads)
