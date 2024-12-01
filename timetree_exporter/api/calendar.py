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
