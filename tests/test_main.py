"""Tests for CLI entry helpers in __main__."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from timetree_exporter.cli import (
    DEVELOPER_MODE_ENV,
    RAW_OUTPUT_DIR,
    list_labels_and_exit,
    raw_output_dir,
)
from timetree_exporter.config import configure_developer_mode, get_raw_output_dir
from timetree_exporter.event import TimeTreeEvent
from timetree_exporter.exporter import (
    Exporter,
    create_calendar,
    label_suffix_for_group,
    write_calendar,
)
from timetree_exporter.formatter import ICalEventFormatter


class _FakeCalendarApi:
    def get_labels(self, _calendar_id):
        return {
            "1": {"name": "Valid", "color": "#ff00aa"},
            "2": {"name": "Empty", "color": ""},
            "3": {"name": "Malformed", "color": "#zzzzzz"},
        }


class _FakeExportCalendarApi:
    def __init__(self, events, labels):
        self.events = events
        self.labels = labels
        self.fetched_events_for = None
        self.fetched_labels_for = None

    def get_events(self, calendar_id, calendar_name):
        self.fetched_events_for = (calendar_id, calendar_name)
        return self.events

    def get_labels(self, calendar_id):
        self.fetched_labels_for = calendar_id
        return self.labels


class _Args:
    def __init__(self, developer_mode=False, raw_output_dir=None):
        self.developer_mode = developer_mode
        self.raw_output_dir = raw_output_dir


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


def test_developer_raw_output_dir_is_disabled_by_default(monkeypatch):
    """Raw API output should stay off unless developer mode is enabled."""
    monkeypatch.delenv(DEVELOPER_MODE_ENV, raising=False)

    assert raw_output_dir(_Args()) is None


def test_developer_mode_enabled_uses_environment_variable(monkeypatch):
    """Developer mode should follow the Homebrew-style environment opt-in."""
    monkeypatch.setenv(DEVELOPER_MODE_ENV, "1")

    assert raw_output_dir(_Args()) == RAW_OUTPUT_DIR


def test_developer_mode_enabled_ignores_non_opt_in_values(monkeypatch):
    """Only an explicit 1 should enable developer mode from the environment."""
    monkeypatch.setenv(DEVELOPER_MODE_ENV, "0")

    assert raw_output_dir(_Args()) is None


def test_developer_raw_output_dir_uses_default_for_developer_mode():
    """Developer mode should dump raw responses to an ignored default directory."""
    assert raw_output_dir(_Args(developer_mode=True)) == RAW_OUTPUT_DIR


def test_developer_raw_output_dir_allows_explicit_override():
    """The raw output directory option should control where debug payloads are written."""
    assert raw_output_dir(_Args(raw_output_dir="tmp/raw")) == "tmp/raw"


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


def test_exporter_fetches_labels_and_writes_single_calendar(tmp_path, normal_event_data):
    """Exporter should own fetching labels, fetching events, and writing output."""
    api = _FakeExportCalendarApi([normal_event_data], {})
    output_path = tmp_path / "calendar.ics"

    Exporter(output_path).export(api, "calendar-id", "Calendar Name")

    serialized = output_path.read_text(encoding="utf-8")
    assert api.fetched_events_for == ("calendar-id", "Calendar Name")
    assert api.fetched_labels_for == "calendar-id"
    assert "SUMMARY:測試一般活動" in serialized


def test_exporter_writes_split_calendars_by_label(tmp_path, labeled_event_data):
    """Exporter should write split files when configured to split by label."""
    api = _FakeExportCalendarApi(
        [labeled_event_data],
        {3: {"name": "Work / Home", "color": "#ff00aa"}},
    )
    output_path = tmp_path / "calendar.ics"

    Exporter(output_path, split_by_label=True).export(api, "calendar-id", "Calendar Name")

    split_path = tmp_path / "calendar_Work___Home.ics"
    serialized = split_path.read_text(encoding="utf-8")
    assert not output_path.exists()
    assert "SUMMARY:測試有標籤活動" in serialized


def test_developer_mode_globally_enables_raw_output():
    """Developer mode should be readable globally by modules."""
    configure_developer_mode(enabled=True)

    try:
        assert get_raw_output_dir() == RAW_OUTPUT_DIR
    finally:
        configure_developer_mode()
