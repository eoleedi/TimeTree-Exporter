"""Tests for the utils module."""

import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from timetree_exporter.utils import (
    convert_timestamp_to_datetime,
    get_events_from_file,
    paths_to_filelist,
)


def test_get_events_from_file(temp_event_file):
    """Test getting events from a JSON file."""
    events = get_events_from_file(temp_event_file)

    assert len(events) == 2
    assert events[0]["uuid"] == "test-uuid-1"
    assert events[0]["title"] == "測試活動 1"
    assert events[1]["uuid"] == "test-uuid-2"
    assert events[1]["title"] == "測試活動 2"


def test_get_public_events_from_file(temp_public_event_file):
    """Test getting public events from a JSON file."""
    events = get_events_from_file(temp_public_event_file)

    assert len(events) == 2
    assert events[0]["uuid"] == "test-uuid-1"
    assert events[0]["title"] == "公開測試活動 1"
    assert events[1]["uuid"] == "test-uuid-2"
    assert events[1]["title"] == "公開測試活動 2"


def test_get_events_from_invalid_file(temp_invalid_file):
    """Test getting events from a file with invalid format."""
    events = get_events_from_file(temp_invalid_file)
    assert events is None


def test_get_events_from_nonexistent_file():
    """Test getting events from a nonexistent file."""
    events = get_events_from_file("nonexistent_file.json")
    assert events is None


def test_paths_to_filelist(temp_directory):
    """Test converting paths to a file list."""
    # 創建一個獨立的文件用於測試
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        # 測試混合目錄和文件的路徑
        paths = [temp_directory, temp_file_path]
        file_list = paths_to_filelist(paths)

        # 驗證結果
        assert len(file_list) == 4  # 3 files in directory + 1 temp file
        assert temp_file_path in file_list

        # 檢查目錄中的文件是否包含在列表中
        for i in range(3):
            expected_file = str(Path(temp_directory) / f"file_{i}.txt")
            assert expected_file in file_list

        # 測試無效路徑
        invalid_paths = ["/nonexistent/path"]
        invalid_file_list = paths_to_filelist(invalid_paths)
        assert len(invalid_file_list) == 0
    finally:
        # 清理
        Path(temp_file_path).unlink()


def test_convert_timestamp_to_datetime():
    """Test converting timestamps to datetime objects."""
    # 測試正時間戳（1970年之後）
    positive_timestamp = 1713110000  # 2024年4月14日左右
    positive_dt = convert_timestamp_to_datetime(positive_timestamp, ZoneInfo("UTC"))

    assert isinstance(positive_dt, datetime)
    assert positive_dt.year == 2024
    assert positive_dt.tzinfo == ZoneInfo("UTC")

    # 測試帶有不同時區的時間戳
    taipei_dt = convert_timestamp_to_datetime(positive_timestamp, ZoneInfo("Asia/Taipei"))
    assert taipei_dt.tzinfo == ZoneInfo("Asia/Taipei")

    # 測試時區轉換是否正確（檢查時區差異）
    new_york_dt = convert_timestamp_to_datetime(positive_timestamp, ZoneInfo("America/New_York"))
    assert new_york_dt.tzinfo == ZoneInfo("America/New_York")

    # 檢查不同時區間的時間差異
    # UTC 與台北時區差 8 小時
    utc_taipei_diff = (taipei_dt.utcoffset() - positive_dt.utcoffset()).total_seconds() / 3600
    assert utc_taipei_diff == 8.0

    # 計算 UTC 與紐約的時差（根據季節可能是 -4 或 -5 小時）
    utc_ny_diff = (new_york_dt.utcoffset() - positive_dt.utcoffset()).total_seconds() / 3600
    # 2024年4月是夏令時間，所以時差應該是 -4 小時
    assert utc_ny_diff == -4.0

    # 測試負時間戳（1970年之前）
    negative_timestamp = -10000000  # 約1969年12月
    negative_dt = convert_timestamp_to_datetime(negative_timestamp, ZoneInfo("UTC"))

    assert isinstance(negative_dt, datetime)
    assert negative_dt.year == 1969
    assert negative_dt.tzinfo == ZoneInfo("UTC")

    # 測試在特定時間戳的本地時間是否正確
    # 創建一個已知的時間戳並檢查對應的本地時間
    timestamp_2023_01_01 = 1672531200  # 2023-01-01 00:00:00 UTC
    london_dt = convert_timestamp_to_datetime(timestamp_2023_01_01, ZoneInfo("Europe/London"))
    assert london_dt.year == 2023
    assert london_dt.month == 1
    assert london_dt.day == 1
    assert london_dt.hour == 0  # 冬令時間，倫敦與UTC相同

    tokyo_dt = convert_timestamp_to_datetime(timestamp_2023_01_01, ZoneInfo("Asia/Tokyo"))
    assert tokyo_dt.year == 2023
    assert tokyo_dt.month == 1
    assert tokyo_dt.day == 1
    assert tokyo_dt.hour == 9  # 東京比UTC快9小時
