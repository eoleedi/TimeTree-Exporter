"""Tests for TimeTree calendar API helpers."""

from timetree_exporter.api.calendar import TimeTreeCalendar
from timetree_exporter.config import configure_developer_mode


class _FakeResponse:
    status_code = 200
    text = "{}"

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self, payload):
        self._payload = payload

    def get(self, *_args, **_kwargs):
        return _FakeResponse(self._payload)


def _calendar_with_metadata_response(payload, capture_raw_responses=True):
    calendar = TimeTreeCalendar("dummy-session-id", capture_raw_responses=capture_raw_responses)
    calendar.session = _FakeSession(payload)
    calendar.get_metadata()
    return calendar


def test_write_raw_responses_writes_captured_payloads(tmp_path):
    """Captured TimeTree responses should be available for offline inspection."""
    calendar = _calendar_with_metadata_response({"calendars": [{"name": "Family"}]})

    written = calendar.write_raw_responses(tmp_path)

    assert written == [tmp_path / "01_calendars.json"]
    assert '"name": "Family"' in written[0].read_text(encoding="utf-8")


def test_raw_event_response_filename_includes_calendar_id(tmp_path):
    """Raw event response filenames should identify the selected calendar."""
    calendar = TimeTreeCalendar("dummy-session-id", capture_raw_responses=True)
    calendar.session = _FakeSession({"events": [], "chunk": False})

    calendar.get_events(1, "Family & Work")

    assert calendar.write_raw_responses(tmp_path) == [tmp_path / "calendar_1/01_events_sync.json"]


def test_raw_label_response_filename_includes_calendar_id(tmp_path):
    """Raw label response filenames should identify the selected calendar."""
    calendar = TimeTreeCalendar("dummy-session-id", capture_raw_responses=True)
    calendar.session = _FakeSession({"calendar_labels": []})

    calendar.get_labels(1)

    assert calendar.write_raw_responses(tmp_path) == [tmp_path / "calendar_1/01_labels.json"]


def test_raw_responses_are_not_recorded_by_default():
    """Raw payloads should only be retained when developer mode enables capture."""
    calendar = _calendar_with_metadata_response({"calendars": []}, capture_raw_responses=False)

    assert calendar.raw_responses == []


def test_calendar_uses_global_developer_mode_for_raw_capture():
    """Calendar API should read raw capture state from global developer config."""
    configure_developer_mode(enabled=True)

    try:
        calendar = TimeTreeCalendar("dummy-session-id")
        assert calendar.capture_raw_responses is True
    finally:
        configure_developer_mode()


def test_api_calls_write_raw_responses_when_developer_output_is_configured(tmp_path):
    """API calls should write their own raw diagnostics when developer mode is active."""
    configure_developer_mode(raw_output_dir=tmp_path)

    try:
        calendar = TimeTreeCalendar("dummy-session-id")
        calendar.session = _FakeSession({"calendars": [{"name": "Family"}]})
        calendar.get_metadata()
        calendar.session = _FakeSession({"calendar_labels": []})
        calendar.get_labels(1)
    finally:
        configure_developer_mode()

    assert (tmp_path / "01_calendars.json").exists()
    assert (tmp_path / "calendar_1/02_labels.json").exists()
    assert not (tmp_path / "calendar_1/03_events_sync.json").exists()
