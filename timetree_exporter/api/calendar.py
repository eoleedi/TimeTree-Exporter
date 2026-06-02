"""
Timetree calendar API
"""

import json
import logging
import re
from pathlib import Path

import requests
from requests.exceptions import HTTPError

from timetree_exporter.api.const import API_BASEURI, API_USER_AGENT, API_V2_BASEURI
from timetree_exporter.config import get_raw_output_dir

logger = logging.getLogger(__name__)

PUBLIC_EVENTS_FROM = 0


class TimeTreeCalendar:
    """
    Timetree calendar API
    """

    def __init__(self, session_id: str, capture_raw_responses: bool | None = None):
        self.session = requests.Session()
        self.session.cookies.set("_session_id", session_id)
        self.capture_raw_responses = (
            get_raw_output_dir() is not None
            if capture_raw_responses is None
            else capture_raw_responses
        )
        self.raw_responses = []

    def _record_raw_response(self, name, payload):
        """Keep raw API payloads available for debug output."""
        if not self.capture_raw_responses:
            return
        self.raw_responses.append((name, payload))
        raw_output_dir = get_raw_output_dir()
        if raw_output_dir:
            self._write_raw_response(raw_output_dir, len(self.raw_responses), name, payload)

    @staticmethod
    def _sanitize_path_part(name):
        """Sanitize a string for use as a path component."""
        return re.sub(r"[^\w\-]", "_", name).strip("_")

    def _write_raw_response(self, output_dir, index, name, payload):
        """Write one raw TimeTree API JSON payload to a directory."""
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        *dirs, filename = [self._sanitize_path_part(part) for part in name.split("/")]
        filename = f"{index:02d}_{filename or 'response'}.json"
        file_path = path.joinpath(*dirs, filename)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        logger.info("Wrote raw TimeTree response to %s", file_path)
        return file_path

    def get_metadata(self):
        """
        Get calendar metadata.
        """
        url = f"{API_BASEURI}/calendars?since=0"
        response = self.session.get(
            url,
            headers={
                "Content-Type": "application/json",
                "X-Timetreea": API_USER_AGENT,
            },
        )
        if response.status_code != 200:
            logger.error(response.text)
            raise HTTPError("Failed to get calendar metadata")
        r_json = response.json()
        self._record_raw_response("calendars", r_json)
        return r_json["calendars"]

    def get_labels(self, calendar_id: int):
        """
        Get labels for a calendar.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Timetreea": API_USER_AGENT,
        }

        # Call dedicated labels endpoint (internal API pattern)
        url = f"{API_BASEURI}/calendar/{calendar_id}/labels"
        response = self.session.get(url, headers=headers)
        logger.debug(
            "GET %s -> %d\n%s",
            url,
            response.status_code,
            json.dumps(response.json(), indent=2, ensure_ascii=False)
            if response.status_code == 200
            else response.text,
        )

        labels = {}

        if response.status_code == 200:
            r_json = response.json()
            self._record_raw_response(f"calendar_{calendar_id}/labels", r_json)
            labels = self._parse_labels(r_json)

        logger.debug("Parsed %d labels: %s", len(labels), labels)
        return labels

    @staticmethod
    def _format_color(color):
        """Convert a color value to hex string if it's an integer."""
        if isinstance(color, int):
            return f"#{color:06x}"
        return color

    @staticmethod
    def _parse_labels(r_json):
        """Parse labels from API response."""
        labels = {}

        if "calendar_labels" in r_json:
            for label in r_json["calendar_labels"]:
                label_id = label.get("id")
                labels[label_id] = {
                    "name": label.get("name", ""),
                    "color": TimeTreeCalendar._format_color(label.get("color", "")),
                }

        return labels

    def get_events_recur(self, calendar_id: int, since: int):
        """
        Get events from the calendar.(Recursively)
        """
        url = f"{API_BASEURI}/calendar/{calendar_id}/events/sync?since={since}"
        response = self.session.get(
            url,
            headers={
                "Content-Type": "application/json",
                "X-Timetreea": API_USER_AGENT,
            },
        )

        r_json = response.json()
        self._record_raw_response(f"calendar_{calendar_id}/events_sync_since_{since}", r_json)

        events = r_json["events"]
        logger.info("Fetched %d events", len(events))
        if r_json["chunk"] is True:
            events.extend(self.get_events_recur(calendar_id, r_json["since"]))
        return events

    def get_events(self, calendar_id: int, calendar_name: str = None):
        """
        Get events from the calendar.
        """
        url = f"{API_BASEURI}/calendar/{calendar_id}/events/sync"
        response = self.session.get(
            url,
            headers={"Content-Type": "application/json", "X-Timetreea": API_USER_AGENT},
        )
        if response.status_code != 200:
            if calendar_name is not None:
                logger.error("Failed to get events of the calendar '%s'", calendar_name)
            else:
                logger.error("Failed to get events of the calendar")
            logger.error(response.text)

        r_json = response.json()
        self._record_raw_response(f"calendar_{calendar_id}/events_sync", r_json)
        events = r_json["events"]
        logger.info("Fetched %d events", len(events))
        if r_json["chunk"] is True:
            events.extend(self.get_events_recur(calendar_id, r_json["since"]))

        logger.debug(
            "Top 5 fetched events: \n %s",
            json.dumps(events[:5], indent=2, ensure_ascii=False),
        )

        return events

    def get_public_events(self, calendar_id: int, calendar_name: str = None):
        """
        Get events from a public calendar.
        """
        url = f"{API_V2_BASEURI}/public_calendars/{calendar_id}/public_events"
        response = self.session.get(
            url,
            headers={"Content-Type": "application/json", "X-Timetreea": API_USER_AGENT},
            params={"from": PUBLIC_EVENTS_FROM},
        )
        if response.status_code != 200:
            if calendar_name is not None:
                logger.error("Failed to get events of the public calendar '%s'", calendar_name)
            else:
                logger.error("Failed to get events of the public calendar")
            logger.error(response.text)
            raise HTTPError("Failed to get public calendar events")

        r_json = response.json()
        self._record_raw_response(f"public_calendar_{calendar_id}/public_events", r_json)
        events = r_json["public_events"]
        logger.info("Fetched %d public events", len(events))
        logger.debug(
            "Top 5 fetched public events: \n %s",
            json.dumps(events[:5], indent=2, ensure_ascii=False),
        )

        return events
