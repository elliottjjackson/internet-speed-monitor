import logging
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from sqlite3 import Error
from typing import Any, Callable, List, MutableMapping, Optional, Union

import speedtest as st

# Set up log file configuration for global use in the script.
log_filename = f"{Path(__file__).stem}.log"
script_filename = Path(__file__).name
project_directory = str(Path(__file__).parent)
project_directory = project_directory.replace("\\\\", "\\")

logging.basicConfig(
    filename=log_filename,
    filemode="a",
    format=f"[%(asctime)s] {{{script_filename}:%(lineno)d}} "
    f"%(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)
# setLevel required outside of basicConfig to prevent matplotlib from writing to log.
log.setLevel(logging.DEBUG)


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


def datetime_from_utcstring(utc_string: str) -> datetime:
    return datetime.strptime(utc_string, "%Y-%m-%d %H:%M:%S.%f")


Mbps = float


class SpeedTest:
    def __init__(self) -> None:
        self._results = None

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
    def results(self) -> Optional[dict[str, Any]]:
        if self._results:
            self._results = self.parse_speedtest_results(self._results.__dict__)
        return self._results

    def run(self) -> None:
        """Retrieve server stats, download and upload on first call."""
        self.speed_test = st.Speedtest()
        self._server_stats = self.update_best_server()
        self._download_speed = self.update_download_speed()
        self._upload_speed = self.update_upload_speed()
        self._results = self.speed_test.results

    @speedtest_connection_log
    def update_best_server(self) -> dict[str, Any]:
        """Queries for the best server nearby and returns statistics"""
        self._server_stats = self.speed_test.get_best_server()
        return self._server_stats

    @speedtest_connection_log
    def update_download_speed(self) -> Mbps:
        """Downloads a package and returns the download speed."""
        self._download_speed = self.speed_test.download() / 1e6
        return self._download_speed

    @speedtest_connection_log
    def update_upload_speed(self) -> Mbps:
        """Uploads a package and returns the download speed."""
        self._upload_speed = self.speed_test.upload() / 1e6
        return self._upload_speed

    def parse_speedtest_results(
        self, input_dict: MutableMapping[Any, Any], parent_key: str = "", sep: str = "_"
    ) -> Optional[dict[str, Any]]:
        """Parses result set by flattening nested dictionaries.
        Expected result is a dictionary with primitive values only and
        concatenated keys (underscore deliminiter by default)."""
        if self._results:
            output_dict: List[tuple[str, Any]] = []
            # for loop flattens nested dictionaries.
            for k, v in input_dict.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, MutableMapping):
                    output_dict.extend(
                        self.parse_speedtest_results(v, new_key, sep=sep).items()
                    )
                else:
                    output_dict.append((new_key, v))
            self._results = dict(output_dict)
            try:
                self._results["download"] = round(self._results["download"] / 1e6, 3)
                self._results["upload"] = round(self._results["upload"] / 1e6, 3)
            except KeyError:
                pass
        else:
            log.debug("Result set is empty. No results to parse.")

        return self._results


class DataBase:
    def __init__(self, results: dict[str, Any] = None) -> None:
        """Establish database (db) connection.
        Create new db in directory if not there.
        Initialises headers and adds speedtest result data if available."""
        self.db_name = "speedtest"
        self.db_directory = project_directory + "\\" + self.db_name + ".db"
        self.conn = self.connect_to_db(self.db_directory)
        self.lastrowid = self.create_table()
        if results:
            self.update_results(results)
        pass

    def connect_to_db(self, db_dir: str) -> object:
        """Establish sqlite3 database connection and curser."""
        conn = None
        try:
            conn = sqlite3.connect(db_dir)
            return conn
        except Error as e:
            log.error(f"Error encountered when connecting to database: {e}")
            raise e

    def create_table(self) -> object:
        """Create new db file if not pre-existing."""
        sql_create_table = f"""CREATE TABLE IF NOT EXISTS {self.db_name}
        (id INTEGER, datetime TEXT, PRIMARY KEY(id));"""
        try:
            cursor = self.conn.cursor()  # type: ignore
            cursor.execute(sql_create_table)
        except Error as e:
            log.error(f"Error occurred when creating new database table: {e}")
            raise e
        return cursor.lastrowid

    def update_headers(self, results: dict[str, Any]) -> List[str]:
        """Adds dictionary keys as headers to database.
        Returns list of headers added to the database."""
        with self.conn:  # type: ignore
            if self.conn is not None:
                # Header list of all keys generated by speedtest
                _header_list = [key for key in results]
                _header_list.insert(0, "datetime")
                # Loop through header list to add them to the database
                for header in _header_list:
                    try:
                        cursor = self.conn.cursor()  # type: ignore
                        _sql_alter = f"ALTER TABLE {self.db_name} ADD {header} TEXT;"
                        cursor.execute(_sql_alter)
                        self.conn.commit()  # type: ignore
                    except Error as e:
                        if re.search("duplicate column name", str(e)):
                            pass
                        else:
                            log.error(
                                f"Error occurred while adding headers to db. Error: {e}"
                            )
                            raise e
        return _header_list

    def update_results(self, results: dict[str, Any]) -> None:
        """Adds result set to database."""
        _header_list = self.update_headers(results)
        _header_string = ", ".join(_header_list)
        # Results added as strings, except timestamp (datetime).
        _value_list = [str(value) for value in results.values()]
        _value_list.insert(0, str(datetime.utcnow()))
        _value_string = ", ".join("?" * len(_value_list))
        _sql_insert = (
            f"INSERT INTO {self.db_name} ({_header_string}) VALUES ({_value_string});"
        )
        with self.conn:  # type: ignore
            if self.conn is not None:
                try:
                    cursor = self.conn.cursor()  # type: ignore
                    cursor.execute(_sql_insert, _value_list)
                except Error as e:
                    log.error(
                        f"Error occurred while running db result update. Error: {e}"
                    )
                    raise e
        log.info("Results added to database.")
        # TODO Add result sets to db rows.

    def sql_to_dict(self) -> List[dict[str, str]]:
        _sql_select = f"SELECT * FROM {self.db_name}"
        with self.conn:  # type: ignore
            if self.conn is not None:
                try:
                    # Creates a list of dictionaries representing each row.
                    self.conn.row_factory = lambda c, r: dict(  # type: ignore
                        zip([col[0] for col in c.description], r)
                    )
                    cursor = self.conn.cursor()  # type: ignore
                    _sql_dict = cursor.execute(_sql_select).fetchall()
                except Error as e:
                    log.error(
                        f"Error occurred while getting timeseries data. Error: {e}"
                    )
                    raise e
        log.info("Retrieved timeseries data from database.")
        return _sql_dict

    def search_for_id_keys(self, header: str, value: str) -> Optional[List[int]]:
        """Returns database id key when provided a header and value."""
        _primary_id_key = None
        _sql_select = f"SELECT id FROM {self.db_name} WHERE {header} = '{value}';"
        with self.conn:  # type: ignore
            if self.conn is not None:
                try:
                    cursor = self.conn.cursor()  # type: ignore
                    cursor.execute(_sql_select)
                    _primary_id_key = cursor.fetchall()
                except Error as e:
                    log.error(f"Error occurred while running db search. Error: {e}")
                    raise e
        # Converts tuple list into normal list of primary ID keys.
        _primary_id_key = [x[0] for x in _primary_id_key]  # type: ignore
        return _primary_id_key

    def delete_entries_with_id(self, ids: Union[List[int], int]) -> None:
        """Deletes a database entry using primary id key."""
        with self.conn:  # type: ignore
            if self.conn is not None:
                if isinstance(ids, int):
                    ids = [ids]
                for id in ids:
                    _sql_delete = f"DELETE FROM {self.db_name} WHERE id = {id}"
                    try:
                        cursor = self.conn.cursor()  # type: ignore
                        cursor.execute(_sql_delete)
                    except Error as e:
                        log.error(f"Error occurred while deleting db line. Error: {e}")
                        raise e


if __name__ == "__main__":

    add_log_header(f"RUNNING {script_filename}")
    speed_test = SpeedTest()
    speed_test.run()
    results = speed_test.results
    db = DataBase(results)
    add_log_header(f"SCRIPT {script_filename} COMPLETE")
