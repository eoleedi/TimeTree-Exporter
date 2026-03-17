"""Tests for the event module."""

from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventType,
    TimeTreeEventCategory,
)


def test_event_creation(normal_event_data):
    """Test creating a TimeTreeEvent."""
    event = TimeTreeEvent(
        uuid=normal_event_data["uuid"],
        title=normal_event_data["title"],
        created_at=normal_event_data["created_at"],
        updated_at=normal_event_data["updated_at"],
        note=normal_event_data["note"],
        location=normal_event_data["location"],
        location_lat=normal_event_data["location_lat"],
        location_lon=normal_event_data["location_lon"],
        url=normal_event_data["url"],
        start_at=normal_event_data["start_at"],
        start_timezone=normal_event_data["start_timezone"],
        end_at=normal_event_data["end_at"],
        end_timezone=normal_event_data["end_timezone"],
        all_day=normal_event_data["all_day"],
        alerts=normal_event_data["alerts"],
        recurrences=normal_event_data["recurrences"],
        parent_id=normal_event_data["parent_id"],
        event_type=normal_event_data["type"],
        category=normal_event_data["category"],
    )

    assert event.uuid == normal_event_data["uuid"]
    assert event.title == normal_event_data["title"]
    assert event.created_at == normal_event_data["created_at"]
    assert event.updated_at == normal_event_data["updated_at"]
    assert event.note == normal_event_data["note"]
    assert event.location == normal_event_data["location"]
    assert event.location_lat == normal_event_data["location_lat"]
    assert event.location_lon == normal_event_data["location_lon"]
    assert event.url == normal_event_data["url"]
    assert event.start_at == normal_event_data["start_at"]
    assert event.start_timezone == normal_event_data["start_timezone"]
    assert event.end_at == normal_event_data["end_at"]
    assert event.end_timezone == normal_event_data["end_timezone"]
    assert event.all_day == normal_event_data["all_day"]
    assert event.alerts == normal_event_data["alerts"]
    assert event.recurrences == normal_event_data["recurrences"]
    assert event.parent_id == normal_event_data["parent_id"]
    assert event.event_type == normal_event_data["type"]
    assert event.category == normal_event_data["category"]


def test_from_dict(normal_event_data):
    """Test creating a TimeTreeEvent from a dictionary."""
    event = TimeTreeEvent.from_dict(normal_event_data)

    assert event.uuid == normal_event_data["uuid"]
    assert event.title == normal_event_data["title"]
    assert event.created_at == normal_event_data["created_at"]
    assert event.updated_at == normal_event_data["updated_at"]
    assert event.note == normal_event_data["note"]
    assert event.location == normal_event_data["location"]
    assert event.location_lat == normal_event_data["location_lat"]
    assert event.location_lon == normal_event_data["location_lon"]
    assert event.url == normal_event_data["url"]
    assert event.start_at == normal_event_data["start_at"]
    assert event.start_timezone == normal_event_data["start_timezone"]
    assert event.end_at == normal_event_data["end_at"]
    assert event.end_timezone == normal_event_data["end_timezone"]
    assert event.all_day == normal_event_data["all_day"]
    assert event.alerts == normal_event_data["alerts"]
    assert event.recurrences == normal_event_data["recurrences"]
    assert event.parent_id == normal_event_data["parent_id"]
    assert event.event_type == normal_event_data["type"]
    assert event.category == normal_event_data["category"]


def test_str_representation(normal_event_data):
    """Test the string representation of a TimeTreeEvent."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    assert str(event) == normal_event_data["title"]


def test_event_types():
    """Test the TimeTreeEventType enumeration."""
    assert TimeTreeEventType.NORMAL == 0
    assert TimeTreeEventType.BIRTHDAY == 1


def test_event_categories():
    """Test the TimeTreeEventCategory enumeration."""
    assert TimeTreeEventCategory.NORMAL == 1
    assert TimeTreeEventCategory.MEMO == 2


def test_from_dict_with_label_id(labeled_event_data):
    """Test creating a TimeTreeEvent with a direct label_id."""
    event = TimeTreeEvent.from_dict(labeled_event_data)
    assert event.label_id == 3


def test_from_dict_with_relationship_label(relationship_label_event_data):
    """Test creating a TimeTreeEvent with label in relationships format."""
    event = TimeTreeEvent.from_dict(relationship_label_event_data)
    assert event.label_id == 7


def test_from_dict_without_label(normal_event_data):
    """Test that label_id is None when no label data is present."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    assert event.label_id is None
