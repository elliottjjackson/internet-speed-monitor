import logging
from pathlib import Path
from typing import Any, Callable, List, MutableMapping

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


def add_log_header(message: str) -> None:
    """Add log header to log."""
    with open(log_filename, "a") as f:
        f.write(f"\n<<< {message} >>>\n")


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
        # Retrieve server stats, download and upload on first call.
        self.speed_test = st.Speedtest()
        self._server_stats = self.update_best_server()
        self._download_speed = self.update_download_speed()
        self._upload_speed = self.update_upload_speed()
        self._results = self.speed_test.results

    @property
    def server_stats(self) -> dict[str, Any]:
        return self._server_stats

    @property
    def download_speed(self) -> float:
        return self._download_speed

    @property
    def upload_speed(self) -> dict[str, Any]:
        return self._upload_speed

    @property
    def results(self) -> dict[str, Any]:
        self._results = self.parse_speedtest_results(self._results.__dict__)
        return self._results

    @speedtest_connection_log
    def update_best_server(self) -> dict[str, Any]:
        """Queries for the best server nearby and returns statistics"""
        self._server_stats = self.speed_test.get_best_server()
        return self._server_stats

    @speedtest_connection_log
    def update_download_speed(self) -> float:
        """Downloads a package and returns the download speed."""
        self._download_speed = self.speed_test.download()
        return self._download_speed

    @speedtest_connection_log
    def update_upload_speed(self) -> float:
        """Uploads a package and returns the download speed."""
        self._upload_speed = self.speed_test.upload()
        return self._upload_speed

    def parse_speedtest_results(
        self, input_dict: MutableMapping[Any, Any], parent_key: str = "", sep: str = "_"
    ) -> dict[str, Any]:
        """Parses result set by flattening nested dictionaries.
        Expected result is a dictionary with primitive values only and
        concatenated keys (underscore deliminiter by default)."""
        output_dict: List[tuple[str, Any]] = []
        for k, v in input_dict.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, MutableMapping):
                output_dict.extend(
                    self.parse_speedtest_results(v, new_key, sep=sep).items()
                )
            else:
                output_dict.append((new_key, v))
        self._result: dict[str, Any] = dict(output_dict)
        return self._result


# TODO database handler class
#   TODO Initialise database in project directory
#   TODO Add new test data method
#   TODO Delete last line method
#   TODO delete all lines method

# TODO Visualiser class
#   TODO Pull data method, construct table
#   TODO Create key data graph
#   TODO Layout Graphs
#   TODO Tabulate data

if __name__ == "__main__":

    add_log_header(f"RUNNING {script_filename}")
    speed_test = SpeedTest()
    server_stats = speed_test.server_stats
    download = speed_test.download_speed
    upload = speed_test.upload_speed
    results = speed_test.results
    add_log_header(f"SCRIPT {script_filename} COMPLETE")

print(results)
