"""
Timetree calendar API
"""

import json
import logging

import requests
from requests.exceptions import HTTPError

from timetree_exporter.api.const import API_BASEURI, API_USER_AGENT

logger = logging.getLogger(__name__)


class TimeTreeCalendar:
    """
    Timetree calendar API
    """

    def __init__(self, session_id: str):
        self.session = requests.Session()
        self.session.cookies.set("_session_id", session_id)

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
        return response.json()["calendars"]

    def get_labels(self, calendar_id: int):
        """
        Get labels for a calendar.

        Tries multiple endpoint patterns since the internal API format
        may differ from the official JSON:API.
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
            url, response.status_code,
            json.dumps(response.json(), indent=2, ensure_ascii=False)
            if response.status_code == 200 else response.text,
        )

        labels = {}

        if response.status_code == 200:
            r_json = response.json()
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
        """Parse labels from various API response formats."""
        labels = {}

        # Internal API format: `calendar_labels` array
        if "calendar_labels" in r_json:
            for label in r_json["calendar_labels"]:
                label_id = label.get("id")
                labels[label_id] = {
                    "name": label.get("name", ""),
                    "color": TimeTreeCalendar._format_color(label.get("color", "")),
                }
            if labels:
                return labels

        # JSON:API `included` array format (official API)
        if "included" in r_json:
            for item in r_json["included"]:
                if item.get("type") == "label":
                    label_id = item.get("id")
                    attrs = item.get("attributes", {})
                    labels[label_id] = {
                        "name": attrs.get("name", ""),
                        "color": TimeTreeCalendar._format_color(
                            attrs.get("color", "")
                        ),
                    }
            if labels:
                return labels

        # Direct `labels` array at top level
        if "labels" in r_json:
            for label in r_json["labels"]:
                label_id = label.get("id")
                labels[label_id] = {
                    "name": label.get("name", ""),
                    "color": TimeTreeCalendar._format_color(label.get("color", "")),
                }
            if labels:
                return labels

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
        events = r_json["events"]
        logger.info("Fetched %d events", len(events))
        if r_json["chunk"] is True:
            events.extend(self.get_events_recur(calendar_id, r_json["since"]))

        logger.debug(
            "Top 5 fetched events: \n %s",
            json.dumps(events[:5], indent=2, ensure_ascii=False),
        )

        return events
