from datetime import datetime
from pathlib import Path
from typing import Any, List

import matplotlib.pyplot as plt

from internet_speed_monitor.main import DataBase, add_log_header

script_filename = Path(__file__).name

if __name__ == "__main__":
    add_log_header(f"RUNNING {script_filename}")
    db = DataBase()

    def two_variable_scatter_plot(
        xaxis_list: List[Any], xaxis_label: str, yaxis_list: List[Any], yaxis_label: str
    ) -> None:
        """Creates scatter plot with anchored x-axis add origin."""
        plt.scatter(xaxis_list, yaxis_list, edgecolors="black")
        plt.ylabel(yaxis_label)
        plt.xlabel(xaxis_label)
        plt.gca().set_ylim(bottom=0)
        plt.xticks(rotation=90)

    # Extract result sets from database.
    date: List[datetime] = [
        datetime.fromisoformat(x["datetime"]) for x in db.sql_to_dict()
    ]
    download: List[float] = [float(x["download"]) for x in db.sql_to_dict()]
    upload: List[float] = [float(x["upload"]) for x in db.sql_to_dict()]
    ping: List[float] = [float(x["ping"]) for x in db.sql_to_dict()]

    # Tri-plot set-up.
    plt.figure(figsize=(18, 9))
    plt.subplot(131)
    two_variable_scatter_plot(date, "Datetime", download, "Download Speed, Mbps")
    plt.subplot(132)
    two_variable_scatter_plot(date, "Datetime", upload, "Upload Speed, Mbps")
    plt.subplot(133)
    two_variable_scatter_plot(date, "Datetime", ping, "Ping, ms")
    plt.suptitle("Internet Speed Test")
    plt.show()
    add_log_header(f"SCRIPT {script_filename} COMPLETE")
