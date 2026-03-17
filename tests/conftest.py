"""Test configuration for pytest."""

import json
import os
import tempfile
import pytest
from timetree_exporter.event import TimeTreeEventType, TimeTreeEventCategory


@pytest.fixture
def normal_event_data():
    """Fixture for normal event data."""
    return {
        "uuid": "test-uuid-normal",
        "title": "測試一般活動",
        "created_at": 1713110000000,  # Unix timestamp in milliseconds
        "updated_at": 1713110100000,  # Unix timestamp in milliseconds
        "note": "測試備註",
        "location": "測試地點",
        "location_lat": "25.0335",
        "location_lon": "121.5645",
        "url": "https://example.com",
        "start_at": 1713120000000,  # Unix timestamp in milliseconds
        "start_timezone": "Asia/Taipei",
        "end_at": 1713123600000,  # Unix timestamp in milliseconds
        "end_timezone": "Asia/Taipei",
        "all_day": False,
        "alerts": [15, 60],  # 15 mins and 60 mins before event
        "recurrences": ["RRULE:FREQ=WEEKLY;COUNT=5"],
        "parent_id": "parent-uuid",
        "type": TimeTreeEventType.NORMAL,
        "category": TimeTreeEventCategory.NORMAL,
    }


@pytest.fixture
def birthday_event_data():
    """Fixture for birthday event data."""
    return {
        "uuid": "test-uuid-birthday",
        "title": "測試生日活動",
        "created_at": 1713110000000,
        "updated_at": 1713110100000,
        "note": "",
        "location": "",
        "location_lat": None,
        "location_lon": None,
        "url": "",
        "start_at": 1713120000000,
        "start_timezone": "Asia/Taipei",
        "end_at": 1713206400000,  # Next day for all-day event
        "end_timezone": "Asia/Taipei",
        "all_day": True,
        "alerts": [15 * 60],  # 15 hours before event
        "recurrences": ["RRULE:FREQ=YEARLY"],
        "parent_id": "",
        "type": TimeTreeEventType.BIRTHDAY,
        "category": TimeTreeEventCategory.NORMAL,
    }


@pytest.fixture
def memo_event_data():
    """Fixture for memo event data."""
    return {
        "uuid": "test-uuid-memo",
        "title": "測試備忘錄",
        "created_at": 1713110000000,
        "updated_at": 1713110100000,
        "note": "備忘內容",
        "location": "",
        "location_lat": None,
        "location_lon": None,
        "url": "",
        "start_at": 1713120000000,
        "start_timezone": "Asia/Taipei",
        "end_at": 1713123600000,
        "end_timezone": "Asia/Taipei",
        "all_day": False,
        "alerts": None,
        "recurrences": None,
        "parent_id": "",
        "type": TimeTreeEventType.NORMAL,
        "category": TimeTreeEventCategory.MEMO,
    }


@pytest.fixture
def labeled_event_data():
    """Fixture for event data with a label_id."""
    return {
        "uuid": "test-uuid-labeled",
        "title": "測試有標籤活動",
        "created_at": 1713110000000,
        "updated_at": 1713110100000,
        "note": "",
        "location": "",
        "location_lat": None,
        "location_lon": None,
        "url": "",
        "start_at": 1713120000000,
        "start_timezone": "Asia/Taipei",
        "end_at": 1713123600000,
        "end_timezone": "Asia/Taipei",
        "all_day": False,
        "alerts": None,
        "recurrences": None,
        "parent_id": "",
        "type": TimeTreeEventType.NORMAL,
        "category": TimeTreeEventCategory.NORMAL,
        "label_id": 3,
    }


@pytest.fixture
def relationship_label_event_data():
    """Fixture for event data with label in relationships format."""
    return {
        "uuid": "test-uuid-rel-label",
        "title": "測試關係標籤活動",
        "created_at": 1713110000000,
        "updated_at": 1713110100000,
        "note": "",
        "location": "",
        "location_lat": None,
        "location_lon": None,
        "url": "",
        "start_at": 1713120000000,
        "start_timezone": "Asia/Taipei",
        "end_at": 1713123600000,
        "end_timezone": "Asia/Taipei",
        "all_day": False,
        "alerts": None,
        "recurrences": None,
        "parent_id": "",
        "type": TimeTreeEventType.NORMAL,
        "category": TimeTreeEventCategory.NORMAL,
        "relationships": {
            "label": {
                "data": {
                    "id": "12345,7",
                    "type": "label",
                }
            }
        },
    }


@pytest.fixture
def temp_event_file():
    """Create a temporary file with event data for testing."""
    event_data = {
        "events": [
            {
                "uuid": "test-uuid-1",
                "title": "測試活動 1",
            },
            {
                "uuid": "test-uuid-2",
                "title": "測試活動 2",
            },
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(event_data, f)
        temp_file_path = f.name

    yield temp_file_path

    # 測試後清理
    os.unlink(temp_file_path)


@pytest.fixture
def temp_public_event_file():
    """Create a temporary file with public event data for testing."""
    event_data = {
        "public_events": [
            {
                "uuid": "test-uuid-1",
                "title": "公開測試活動 1",
            },
            {
                "uuid": "test-uuid-2",
                "title": "公開測試活動 2",
            },
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(event_data, f)
        temp_file_path = f.name

    yield temp_file_path

    # 測試後清理
    os.unlink(temp_file_path)


@pytest.fixture
def temp_invalid_file():
    """Create a temporary file with invalid data for testing."""
    invalid_data = {"some_other_key": []}

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(invalid_data, f)
        temp_file_path = f.name

    yield temp_file_path

    # 測試後清理
    os.unlink(temp_file_path)


@pytest.fixture
def temp_directory():
    """Create a temporary directory with multiple files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 在臨時目錄中創建一些文件
        for i in range(3):
            with open(
                os.path.join(temp_dir, f"file_{i}.txt"), "w", encoding="utf-8"
            ) as f:
                f.write(f"Content of file {i}")

        yield temp_dir
