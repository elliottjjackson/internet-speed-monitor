import logging
from pathlib import Path
from typing import Any, Callable

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


def speedtest_connection_log(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for logging of test data queries, retrieval or error occurrance"""

    def wrapper(*args: Any) -> Any:
        """Wrapper for test retrieval log."""
        log.info(f"Retrieving data with {func.__name__}")
        try:
            result = func(*args)
            log.info(f"Data retrieved with {func.__name__}")
            plog(10, result)
        except Exception as error:
            log.error(f"Error occurred while running {func.__name__}\nError - {error}")
            raise error
        return result

    return wrapper


class SpeedTest:
    def __init__(self) -> None:
        self.speed_test = st.Speedtest()
        self._server_stats = self.update_best_server()
        self._download_speed = self.update_download_speed()
        self._upload_speed = self.update_upload_speed()

    @property
    def server_stats(self) -> dict[str, Any]:
        return self._server_stats

    @property
    def download_speed(self) -> float:
        return self._download_speed

    @property
    def upload_speed(self) -> dict[str, Any]:
        return self._upload_speed

    @speedtest_connection_log
    def update_best_server(self) -> None:
        """Queries for the best server nearby and returns statistics"""
        self._server_stats = self.speed_test.get_best_server()

    @speedtest_connection_log
    def update_download_speed(self) -> None:
        """Downloads a package and returns the download speed."""
        self._download_speed = self.speed_test.download()

    @speedtest_connection_log
    def update_upload_speed(self) -> None:
        """Uploads a package and returns the download speed."""
        self._upload_speed = self.speed_test.upload()


if __name__ == "__main__":

    add_log_header()
    speed_test = SpeedTest()
    server_stats = speed_test.server_stats
    download = speed_test.download_speed
    upload = speed_test.upload_speed
    add_log_footer()
