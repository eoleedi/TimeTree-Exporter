"""Tests for CLI entry helpers in __main__."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from timetree_exporter.__main__ import (
    create_calendar,
    label_suffix_for_group,
    list_labels_and_exit,
    write_calendar,
)
from timetree_exporter.event import TimeTreeEvent
from timetree_exporter.formatter import ICalEventFormatter


class _FakeCalendarApi:
    def get_labels(self, _calendar_id):
        return {
            "1": {"name": "Valid", "color": "#ff00aa"},
            "2": {"name": "Empty", "color": ""},
            "3": {"name": "Malformed", "color": "#zzzzzz"},
        }


def test_list_labels_and_exit_handles_invalid_or_missing_color(capsys):
    """Listing labels should not fail when color is empty or malformed."""
    list_labels_and_exit(_FakeCalendarApi(), "dummy-calendar-id")

    output = capsys.readouterr().out

    assert "Valid" in output
    assert "Empty" in output
    assert "Malformed" in output
    assert "\033[38;2;255;0;170m●\033[0m" in output


def test_label_suffix_for_group_uses_label_id_when_name_is_empty():
    """Unnamed color-only labels should still produce unique output filenames."""
    labels = {3: {"name": "", "color": "#ff00aa"}}

    assert label_suffix_for_group(3, labels) == "label_3"


def test_label_suffix_for_group_sanitizes_label_name():
    """Named labels should keep their name while remaining filename safe."""
    labels = {3: {"name": "Work / Home", "color": "#ff00aa"}}

    assert label_suffix_for_group(3, labels) == "Work___Home"


def test_write_calendar_adds_bounded_vtimezone_before_events(tmp_path, normal_event_data):
    """Bounded VTIMEZONE components should be written before VEVENT blocks."""
    data = normal_event_data.copy()
    taipei_time = datetime(2024, 8, 14, 9, 30, tzinfo=ZoneInfo("Asia/Taipei"))
    data["start_at"] = int(taipei_time.timestamp() * 1000)
    data["end_at"] = int((taipei_time + timedelta(hours=1)).timestamp() * 1000)

    cal = create_calendar()
    cal.add_component(ICalEventFormatter(TimeTreeEvent.from_dict(data)).to_ical())
    output_path = tmp_path / "calendar.ics"

    write_calendar(cal, output_path)
    serialized = output_path.read_text(encoding="utf-8")

    assert "DTSTART;TZID=Asia/Taipei:20240814T093000" in serialized
    assert "BEGIN:VTIMEZONE" in serialized
    assert "TZID:Asia/Taipei" in serialized
    assert "TZOFFSETTO:+0800" in serialized
    assert serialized.index("BEGIN:VTIMEZONE") < serialized.index("BEGIN:VEVENT")
