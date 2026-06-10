"""Tests for the formatter module."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from icalendar import Event
from icalendar.prop import vDuration

from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventType,
    TimeTreePublicEvent,
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


def test_to_ical_includes_comments(normal_event_data):
    """Event comments should be exported as COMMENT properties."""
    data = normal_event_data.copy()
    data["comments"] = ["First comment", "Second comment"]
    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)

    assert formatter.description == "測試備註"
    assert formatter.comments == ["First comment", "Second comment"]

    ical_event = formatter.to_ical()

    assert ical_event["description"] == "測試備註"
    assert ical_event["comment"] == ["First comment", "Second comment"]


def test_related_to_prefers_recurring_uuid(normal_event_data):
    """RELATED-TO should reference the parent event UID, not internal parent id."""
    data = normal_event_data.copy()
    data["parent_id"] = "parent-api-id"
    data["recurring_uuid"] = "parent-event-uuid"
    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert formatter.related_to == "parent-event-uuid"
    assert ical_event["related-to"] == "parent-event-uuid"


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


def test_multi_day_all_day_event_dtend_is_exclusive(normal_event_data):
    """Test all-day multi-day events export with exclusive iCal DTEND."""
    data = normal_event_data.copy()
    data.update(
        {
            "start_at": int(
                datetime(2024, 8, 14, tzinfo=ZoneInfo("Asia/Taipei")).timestamp() * 1000
            ),
            "end_at": int(datetime(2024, 8, 16, tzinfo=ZoneInfo("Asia/Taipei")).timestamp() * 1000),
            "all_day": True,
            "alerts": None,
            "recurrences": None,
        }
    )

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["dtstart"].dt.date() == date(2024, 8, 14)
    assert ical_event["dtend"].dt.date() == date(2024, 8, 17)


def test_rrule_until_date_for_timed_event_is_converted_to_utc(normal_event_data):
    """Test date-only RRULE UNTIL uses local end-of-day converted to UTC."""
    data = normal_event_data.copy()
    data.update(
        {
            "recurrences": ["RRULE:FREQ=WEEKLY;UNTIL=20220524"],
            "end_timezone": "Asia/Taipei",
            "all_day": False,
        }
    )

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["RRULE"]["UNTIL"] == [
        datetime(2022, 5, 24, 15, 59, 59, tzinfo=ZoneInfo("UTC"))
    ]


def test_rrule_until_date_uses_start_timezone(normal_event_data):
    """Test date-only RRULE UNTIL is interpreted in DTSTART timezone."""
    data = normal_event_data.copy()
    data.update(
        {
            "recurrences": ["RRULE:FREQ=WEEKLY;UNTIL=20220524"],
            "start_timezone": "Asia/Tokyo",
            "end_timezone": "Asia/Taipei",
            "all_day": False,
        }
    )

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["RRULE"]["UNTIL"] == [
        datetime(2022, 5, 24, 14, 59, 59, tzinfo=ZoneInfo("UTC"))
    ]


def test_rrule_until_date_for_all_day_event_stays_date(normal_event_data):
    """Test all-day date-only RRULE UNTIL remains a date."""
    data = normal_event_data.copy()
    data.update(
        {
            "recurrences": ["RRULE:FREQ=YEARLY;UNTIL=20220524"],
            "end_timezone": "Asia/Taipei",
            "all_day": True,
        }
    )

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["RRULE"]["UNTIL"] == [date(2022, 5, 24)]


def test_public_recurrence_does_not_map_until_at(normal_event_data):
    """Public until_at should not synthesize recurrence bounds."""
    data = normal_event_data.copy()
    data.pop("uuid")
    data.update(
        {
            "id": "public-event-id",
            "recurrences": ["RRULE:FREQ=MONTHLY"],
            "until_at": int(datetime(2085, 4, 1, tzinfo=ZoneInfo("UTC")).timestamp() * 1000),
        }
    )

    event = TimeTreePublicEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["RRULE"]["FREQ"] == ["MONTHLY"]
    assert "UNTIL" not in ical_event["RRULE"]


def test_rrule_rejects_count_with_until(normal_event_data):
    """RRULEs with both COUNT and UNTIL should fail loudly."""
    data = normal_event_data.copy()
    data.update(
        {
            "recurrences": ["RRULE:FREQ=DAILY;UNTIL=20251130;COUNT=3;INTERVAL=7"],
            "all_day": True,
        }
    )

    event = TimeTreeEvent.from_dict(data)
    formatter = ICalEventFormatter(event)

    try:
        formatter.to_ical()
    except ValueError as exc:
        assert str(exc) == "RRULE must not include both COUNT and UNTIL"
    else:
        raise AssertionError("expected invalid RRULE to raise ValueError")


def test_public_until_at_is_not_added_when_count_is_present(normal_event_data):
    """Public until_at should not create invalid COUNT plus UNTIL rules."""
    data = normal_event_data.copy()
    data.pop("uuid")
    data.update(
        {
            "id": "public-event-id",
            "recurrences": ["RRULE:FREQ=DAILY;COUNT=1;INTERVAL=14"],
            "until_at": int(datetime(2025, 12, 11, tzinfo=ZoneInfo("UTC")).timestamp() * 1000),
        }
    )

    event = TimeTreePublicEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["RRULE"]["COUNT"] == [1]
    assert "UNTIL" not in ical_event["RRULE"]


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
    assert formatter.categories == ["Work"]

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


def test_categories_with_additional_category_names(normal_event_data):
    """Test that additional public category names are included in CATEGORIES."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    formatter = ICalEventFormatter(event, label_name="Work", category_names=["Sale", "Food"])

    assert formatter.categories == ["Work", "Sale", "Food"]

    ical_event = formatter.to_ical()
    assert ical_event["CATEGORIES"].cats == ["Work", "Sale", "Food"]


def test_public_images_are_exported_as_image_properties(normal_event_data):
    """Public cover images should be exported as RFC 7986 IMAGE properties."""
    data = normal_event_data.copy()
    data.pop("uuid")
    data["id"] = "public-event-id"
    data["images"] = {
        "cover": [
            {
                "url": "https://example.com/image.jpg",
                "thumbnail_url": "https://example.com/thumb.jpg",
            }
        ]
    }

    event = TimeTreePublicEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()
    serialized = ical_event.to_ical().decode()

    assert "IMAGE;DISPLAY=FULLSIZE;VALUE=URI:https://example.com/image.jpg" in serialized
    assert "IMAGE;DISPLAY=THUMBNAIL;VALUE=URI:https://example.com/thumb.jpg" in serialized


def test_public_location_url_is_exported_as_location_altrep(normal_event_data):
    """Public location URLs should be exported as LOCATION ALTREP."""
    data = normal_event_data.copy()
    data.pop("uuid")
    data["id"] = "public-event-id"
    data["location"] = "Public Venue"
    data["location_url"] = "https://example.com/location"

    event = TimeTreePublicEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["LOCATION"] == "Public Venue"
    assert ical_event["LOCATION"].params["ALTREP"] == "https://example.com/location"


def test_public_event_uses_link_url_as_ical_url_and_timetree_url_as_source(normal_event_data):
    """Public campaign links should be URL, while TimeTree permalinks are SOURCE."""
    data = normal_event_data.copy()
    data.pop("uuid")
    data["id"] = "public-event-id"
    data["url"] = "https://timetr.ee/p/public-event-id"
    data["link_url"] = "https://example.com/campaign"

    event = TimeTreePublicEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert ical_event["URL"] == "https://example.com/campaign"
    assert ical_event["SOURCE"] == "https://timetr.ee/p/public-event-id"
    assert ical_event["SOURCE"].params["VALUE"] == "URI"


def test_public_event_without_link_url_has_source_but_no_ical_url(normal_event_data):
    """Public TimeTree permalinks should not become URL when link_url is absent."""
    data = normal_event_data.copy()
    data.pop("uuid")
    data.pop("url")
    data["id"] = "public-event-id"
    data["url"] = "https://timetr.ee/p/public-event-id"

    event = TimeTreePublicEvent.from_dict(data)
    formatter = ICalEventFormatter(event)
    ical_event = formatter.to_ical()

    assert "URL" not in ical_event
    assert ical_event["SOURCE"] == "https://timetr.ee/p/public-event-id"


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
