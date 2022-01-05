import logging
from pathlib import Path
from typing import Any, Iterable

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


def plog(logging_level: int, iterable: Iterable[Any]) -> None:
    """Pretty logging for iterables.
    Log each item or key-value pair on a single line."""
    if isinstance(iterable, dict):
        for (key, value) in iterable.items():
            log.log(logging_level, f"{key}: {value}")
    if isinstance(iterable, (tuple, list)):
        for item in iterable:
            log.log(logging_level, f"{item}")


def get_best_server_stats() -> dict[str, Any]:
    speed_test = st.Speedtest()
    log.info("Searching for best server...")
    try:
        best_server: dict[str, Any] = speed_test.get_best_server()
        log.info("Best server found!")
        plog(10, best_server)
    except Exception as error:
        log.error(f"Something went wrong when finding a server.\nError - {error}")
        raise error
    return best_server


if __name__ == "__main__":

    add_log_header()
    best_server_stats = get_best_server_stats()
