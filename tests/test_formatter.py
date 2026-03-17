"""Tests for the formatter module."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


from icalendar import Event
from icalendar.prop import vDuration
from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventType,
)
from timetree_exporter.formatter import ICalEventFormatter
from timetree_exporter.utils import convert_timestamp_to_datetime


def test_formatter_properties(normal_event_data):
    """Test the properties of the ICalEventFormatter."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event)

    assert formatter.uid == normal_event_data["uuid"]
    assert formatter.summary == normal_event_data["title"]
    assert formatter.description == normal_event_data["note"]
    assert formatter.location == normal_event_data["location"]
    assert formatter.url == normal_event_data["url"]
    assert formatter.related_to == normal_event_data["parent_id"]

    # Test created time
    created_dt = convert_timestamp_to_datetime(
        normal_event_data["created_at"] / 1000, ZoneInfo("UTC")
    )
    assert formatter.created.dt == created_dt

    # Test last modified time
    modified_dt = convert_timestamp_to_datetime(
        normal_event_data["updated_at"] / 1000, ZoneInfo("UTC")
    )
    assert formatter.last_modified.dt == modified_dt

    # Test geo
    assert formatter.geo.latitude == float(normal_event_data["location_lat"])
    assert formatter.geo.longitude == float(normal_event_data["location_lon"])

    # Test datetime properties
    start_dt = convert_timestamp_to_datetime(
        normal_event_data["start_at"] / 1000,
        ZoneInfo(normal_event_data["start_timezone"]),
    )
    end_dt = convert_timestamp_to_datetime(
        normal_event_data["end_at"] / 1000, ZoneInfo(normal_event_data["end_timezone"])
    )
    assert formatter.dtstart.dt == start_dt
    assert formatter.dtend.dt == end_dt

    # Test alarms
    alarms = formatter.alarms
    assert len(alarms) == 2
    assert alarms[0]["action"] == "DISPLAY"
    assert alarms[0]["description"] == "Reminder"
    assert alarms[0]["trigger"] == vDuration(timedelta(minutes=-15))
    assert alarms[1]["action"] == "DISPLAY"
    assert alarms[1]["description"] == "Reminder"
    assert alarms[1]["trigger"] == vDuration(timedelta(minutes=-60))


def test_to_ical_normal_event(normal_event_data):
    """Test converting a normal TimeTreeEvent to an iCal event."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert isinstance(ical_event, Event)
    assert ical_event["uid"] == normal_event_data["uuid"]
    assert ical_event["summary"] == normal_event_data["title"]
    assert ical_event["description"] == normal_event_data["note"]
    assert ical_event["location"] == normal_event_data["location"]
    assert ical_event["url"] == normal_event_data["url"]
    assert ical_event["related-to"] == normal_event_data["parent_id"]

    # Verify that the event has alarms
    components = list(ical_event.subcomponents)
    assert len(components) == 2  # Two alarms
    assert all(component.name == "VALARM" for component in components)

    # Verify recurrence rule
    assert "RRULE" in ical_event
    assert ical_event["RRULE"]["FREQ"] == ["WEEKLY"]
    assert ical_event["RRULE"]["COUNT"] == [5]


def test_to_ical_birthday_event(birthday_event_data):
    """Test converting a birthday TimeTreeEvent to an iCal event."""
    event = TimeTreeEvent.from_dict(birthday_event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    # Birthday events should be skipped
    assert ical_event is None


def test_to_ical_memo_event(memo_event_data):
    """Test converting a memo TimeTreeEvent to an iCal event."""
    event = TimeTreeEvent.from_dict(memo_event_data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    # Memo events should be skipped
    assert ical_event is None


def test_all_day_event(birthday_event_data):
    """Test formatting an all-day event."""
    # Modify to a normal event that's all-day (not a birthday)
    all_day_data = birthday_event_data.copy()
    all_day_data["type"] = TimeTreeEventType.NORMAL

    event = TimeTreeEvent.from_dict(all_day_data)
    formatter = ICalEventFormatter(event)

    # Test that dtstart and dtend use vDate instead of vDatetime for all-day events

    assert isinstance(formatter.dtstart.dt, datetime)
    assert (
        formatter.dtstart.dt.date()
        == convert_timestamp_to_datetime(
            all_day_data["start_at"] / 1000, ZoneInfo(all_day_data["start_timezone"])
        ).date()
    )

    # Check to_ical produces a valid event
    ical_event = formatter.to_ical()
    assert isinstance(ical_event, Event)
    assert ical_event["summary"] == all_day_data["title"]


def test_no_alarms_location_url(normal_event_data):
    """Test event formatting without optional fields."""
    # Create an event without alarms, location, and URL
    data = normal_event_data.copy()
    data["alerts"] = None
    data["location"] = ""
    data["location_lat"] = None
    data["location_lon"] = None
    data["url"] = ""

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)

    assert not formatter.alarms
    assert formatter.location is None
    assert formatter.geo is None
    assert formatter.url is None

    # Check the iCal event
    ical_event = formatter.to_ical()
    assert "location" not in ical_event
    assert "geo" not in ical_event
    assert "url" not in ical_event

    # Verify no alarms were added
    components = list(ical_event.subcomponents)
    assert len(components) == 0


def test_categories_with_label_name(normal_event_data):
    """Test that CATEGORIES is set when label_name is provided."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event, label_name="Work")
    assert formatter.categories == "Work"

    ical_event = formatter.to_ical()
    assert "CATEGORIES" in ical_event
    assert ical_event["CATEGORIES"].cats == ["Work"]


def test_categories_without_label_name(normal_event_data):
    """Test that CATEGORIES is not set when label_name is None."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event)
    assert formatter.categories is None

    ical_event = formatter.to_ical()
    assert "CATEGORIES" not in ical_event


def test_different_timezones(normal_event_data):
    """Test event with different start and end timezones."""
    # Create an event with different start and end timezones
    data = normal_event_data.copy()
    data["start_timezone"] = "America/New_York"  # EDT/EST
    data["end_timezone"] = "Asia/Tokyo"  # JST

    # Set specific timestamps
    ny_time = datetime(2023, 6, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York"))
    data["start_at"] = int(ny_time.timestamp() * 1000)

    tokyo_time = datetime(2023, 6, 16, 8, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
    data["end_at"] = int(tokyo_time.timestamp() * 1000)

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)

    # Test timezone properties are correctly set
    assert formatter.dtstart.dt.tzinfo.key == "America/New_York"
    assert formatter.dtend.dt.tzinfo.key == "Asia/Tokyo"

    # Verify the actual datetime values
    assert formatter.dtstart.dt == ny_time
    assert formatter.dtend.dt == tokyo_time

    # Convert both to UTC for comparison of the actual time (not just representation)
    start_utc = formatter.dtstart.dt.astimezone(ZoneInfo("UTC"))
    end_utc = formatter.dtend.dt.astimezone(ZoneInfo("UTC"))

    # Verify the time difference is preserved
    # Tokyo time is 13 hours ahead of New York during EDT
    expected_hours_diff = (
        tokyo_time.astimezone(ZoneInfo("UTC")) - ny_time.astimezone(ZoneInfo("UTC"))
    ).total_seconds() / 3600
    actual_hours_diff = (end_utc - start_utc).total_seconds() / 3600
    assert actual_hours_diff == expected_hours_diff

    # Check iCal event preserves timezone information
    ical_event = formatter.to_ical()
    assert ical_event["dtstart"].dt.tzinfo.key == "America/New_York"
    assert ical_event["dtend"].dt.tzinfo.key == "Asia/Tokyo"
