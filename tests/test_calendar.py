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


class _RecordingSession(_FakeSession):
    def __init__(self, payload):
        super().__init__(payload)
        self.requested_url = None
        self.requested_params = None

    def get(self, url, **kwargs):
        self.requested_url = url
        self.requested_params = kwargs.get("params")
        return _FakeResponse(self._payload)


class _PagingSession:
    def __init__(self, payloads):
        self._payloads = list(payloads)
        self.requested_params = []

    def get(self, _url, **kwargs):
        self.requested_params.append(kwargs.get("params"))
        return _FakeResponse(self._payloads.pop(0))


class _UrlPayloadSession:
    def __init__(self, payloads):
        self._payloads = payloads
        self.requested_urls = []

    def get(self, url, **_kwargs):
        self.requested_urls.append(url)
        return _FakeResponse(self._payloads[url])


def _calendar_with_metadata_response(payload, capture_raw_responses=True):
    calendar = TimeTreeCalendar("dummy-session-id", capture_raw_responses=capture_raw_responses)
    calendar.session = _FakeSession(payload)
    calendar.get_metadata()
    return calendar


def test_raw_event_response_filename_includes_calendar_id(tmp_path):
    """Raw event response filenames should identify the selected calendar."""
    configure_developer_mode(raw_output_dir=tmp_path)

    try:
        calendar = TimeTreeCalendar("dummy-session-id")
        calendar.session = _FakeSession({"events": [], "chunk": False})
        calendar.get_events(1, "Family & Work")
    finally:
        configure_developer_mode()

    assert (tmp_path / "calendar_1/01_events_sync.json").exists()


def test_raw_label_response_filename_includes_calendar_id(tmp_path):
    """Raw label response filenames should identify the selected calendar."""
    configure_developer_mode(raw_output_dir=tmp_path)

    try:
        calendar = TimeTreeCalendar("dummy-session-id")
        calendar.session = _FakeSession({"calendar_labels": []})
        calendar.get_labels(1)
    finally:
        configure_developer_mode()

    assert (tmp_path / "calendar_1/01_labels.json").exists()


def test_get_public_labels_uses_public_calendar_metadata_endpoint():
    """Public calendar labels should come from metadata, not event payloads."""
    calendar = TimeTreeCalendar("dummy-session-id")
    session = _RecordingSession(
        {
            "public_calendar": {
                "public_calendar_labels": [
                    {"label_id": 4, "name": "Public Campaign", "color": 9732216}
                ]
            }
        }
    )
    calendar.session = session

    labels = calendar.get_public_labels("public-calendar-id")

    assert session.requested_url.endswith("/api/v2/public_calendars/public-calendar-id")
    assert session.requested_params is None
    assert labels == {4: {"name": "Public Campaign", "color": "#948078"}}


def test_parse_public_labels_skips_missing_id_and_coerces_name():
    """Malformed public labels should not create None keys, and names should be strings."""
    labels = TimeTreeCalendar._parse_public_labels(
        {
            "public_calendar": {
                "public_calendar_labels": [
                    {"name": "Missing ID", "color": 0},
                    {"label_id": 0, "name": None, "color": 0},
                ]
            }
        }
    )

    assert labels == {0: {"name": "", "color": "#000000"}}


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


def test_get_public_events_uses_public_calendar_endpoint():
    """Public calendar exports should use the API v2 public_events endpoint."""
    calendar = TimeTreeCalendar("dummy-session-id")
    session = _RecordingSession({"public_events": [{"id": "public-event-id"}]})
    calendar.session = session

    events = calendar.get_public_events("public-calendar-id", "Public Calendar")

    assert session.requested_url.endswith(
        "/api/v2/public_calendars/public-calendar-id/public_events"
    )
    assert session.requested_params == {"from": 0}
    assert events == [{"id": "public-event-id"}]


def test_get_events_adds_comments_from_activity_endpoint():
    """Private event exports should include event comments from activities."""
    calendar = TimeTreeCalendar("dummy-session-id")
    session = _UrlPayloadSession(
        {
            "https://timetreeapp.com/api/v1/calendar/1/events/sync": {
                "events": [{"id": 10, "uuid": "event-uuid"}],
                "chunk": False,
            },
            "https://timetreeapp.com/api/v1/calendar/1/event/event-uuid/activities?since=0": {
                "event_activities": [
                    {"author_id": 10, "comment": {"body": "First comment"}},
                    {"author_id": 11, "comment": "Second comment"},
                    {"author_id": 12, "attachment": {"content": "Third comment"}},
                    {"action": "updated"},
                ],
                "chunk": True,
                "since": 123,
            },
            "https://timetreeapp.com/api/v1/calendar/1/event/event-uuid/activities?since=123": {
                "activities": [{"author_id": 10, "message": "Fourth comment"}],
                "chunk": False,
            },
        }
    )
    calendar.session = session

    events = calendar.get_events(
        1,
        "Family",
        [
            {"user_id": 10, "name": "Alice"},
            {"id": 11, "name": "Bob"},
        ],
        include_comments=True,
    )

    assert session.requested_urls == [
        "https://timetreeapp.com/api/v1/calendar/1/events/sync",
        "https://timetreeapp.com/api/v1/calendar/1/event/event-uuid/activities?since=0",
        "https://timetreeapp.com/api/v1/calendar/1/event/event-uuid/activities?since=123",
    ]
    assert events == [
        {
            "id": 10,
            "uuid": "event-uuid",
            "comments": [
                "Alice: First comment",
                "Bob: Second comment",
                "Third comment",
                "Alice: Fourth comment",
            ],
        }
    ]


def test_get_events_does_not_fetch_comments_by_default():
    """Private event exports should avoid per-event activity calls by default."""
    calendar = TimeTreeCalendar("dummy-session-id")
    session = _UrlPayloadSession(
        {
            "https://timetreeapp.com/api/v1/calendar/1/events/sync": {
                "events": [{"id": 10, "uuid": "event-uuid"}],
                "chunk": False,
            }
        }
    )
    calendar.session = session

    events = calendar.get_events(1, "Family")

    assert session.requested_urls == ["https://timetreeapp.com/api/v1/calendar/1/events/sync"]
    assert events == [{"id": 10, "uuid": "event-uuid"}]


def test_get_public_events_follows_pagination_cursor():
    """Public calendar exports should follow the public_events paging envelope."""
    calendar = TimeTreeCalendar("dummy-session-id")
    session = _PagingSession(
        [
            {
                "public_events": [{"id": "first-event"}],
                "paging": {"next": True, "next_cursor": "next-page"},
            },
            {
                "public_events": [{"id": "second-event"}],
                "paging": {"next": False},
            },
        ]
    )
    calendar.session = session

    events = calendar.get_public_events("public-calendar-id", "Public Calendar")

    assert session.requested_params == [
        {"from": 0},
        {"from": 0, "cursor": "next-page"},
    ]
    assert events == [{"id": "first-event"}, {"id": "second-event"}]


def test_raw_public_event_response_filename_includes_calendar_id(tmp_path):
    """Raw public event response filenames should identify the selected public calendar."""
    configure_developer_mode(raw_output_dir=tmp_path)

    try:
        calendar = TimeTreeCalendar("dummy-session-id")
        calendar.session = _FakeSession({"public_events": []})
        calendar.get_public_events("public-calendar-id", "Public Calendar")
    finally:
        configure_developer_mode()

    assert (tmp_path / "public_calendar_public-calendar-id/01_public_events.json").exists()
