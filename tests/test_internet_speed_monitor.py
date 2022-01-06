from internet_speed_monitor import __version__
from internet_speed_monitor.main import SpeedTest

speed_test = SpeedTest()


def test_version():
    assert __version__ == "0.1.0"


def test_speedtest_server_stats_is_not_none():
    assert speed_test.server_stats is not None


def test_speedtest_server_stats_is_not_string():
    assert not isinstance(speed_test.server_stats, str)


def test_speedtest_download_speed_is_not_none():
    assert speed_test.download_speed is not None


def test_speedtest_download_speed_is_not_string():
    assert not isinstance(speed_test.download_speed, str)


def test_speedtest_upload_speed_is_not_none():
    assert speed_test.upload_speed is not None


def test_speedtest_upload_speed_is_not_string():
    assert not isinstance(speed_test.upload_speed, str)
