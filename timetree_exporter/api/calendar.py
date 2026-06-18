"""
Timetree calendar API
"""

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    def get_public_labels(self, calendar_id: int):
        """
        Get labels for a public calendar.
        """
        url = f"{API_V2_BASEURI}/public_calendars/{calendar_id}"
        response = self.session.get(
            url,
            headers={"Content-Type": "application/json", "X-Timetreea": API_USER_AGENT},
        )
        if response.status_code != 200:
            logger.error(response.text)
            raise HTTPError("Failed to get public calendar labels")

        r_json = response.json()
        self._record_raw_response(f"public_calendar_{calendar_id}/metadata", r_json)
        labels = self._parse_public_labels(r_json)
        logger.debug("Parsed %d public labels: %s", len(labels), labels)
        return labels

    @staticmethod
    def _parse_public_labels(r_json):
        """Parse labels from a public calendar metadata response."""
        labels = {}
        public_calendar = r_json.get("public_calendar") or {}
        for label in public_calendar.get("public_calendar_labels", []):
            label_id = label.get("label_id")
            if label_id is None:
                continue
            labels[label_id] = {
                "name": str(label.get("name") or ""),
                "color": TimeTreeCalendar._format_color(label.get("color", "")),
            }
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

    @staticmethod
    def _extract_activity_comment(activity):
        """Return comment text from a TimeTree activity payload when present."""
        comment = activity.get("comment")
        if isinstance(comment, str):
            return comment
        if isinstance(comment, dict):
            for key in ("body", "text", "content", "message"):
                if comment.get(key):
                    return comment[key]

        attachment = activity.get("attachment")
        if isinstance(attachment, dict) and attachment.get("content"):
            return attachment["content"]

        for key in ("body", "text", "content", "message"):
            if activity.get(key):
                return activity[key]

        return None

    @staticmethod
    def _calendar_user_names(calendar_users):
        """Return calendar user names keyed by user id."""
        names = {}
        for user in calendar_users or []:
            user_id = user.get("user_id") or user.get("id")
            name = user.get("name")
            if user_id is not None and name:
                names[user_id] = name
        return names

    @staticmethod
    def _format_activity_comment(activity, comment, user_names):
        """Add the activity author name to a comment when known."""
        author_name = user_names.get(activity.get("author_id"))
        if author_name:
            return f"{author_name}: {comment}"
        return comment

    def get_event_activities(
        self,
        calendar_id: int,
        event_uuid: str,
        since: int = 0,
        user_names=None,
    ):
        """Get activities for an event."""
        user_names = user_names or {}
        url = f"{API_BASEURI}/calendar/{calendar_id}/event/{event_uuid}/activities?since={since}"
        response = self.session.get(
            url,
            headers={
                "Content-Type": "application/json",
                "X-Timetreea": API_USER_AGENT,
            },
        )
        if response.status_code != 200:
            logger.warning("Failed to get activities for event %s", event_uuid)
            logger.debug(response.text)
            return []

        r_json = response.json()
        self._record_raw_response(
            f"calendar_{calendar_id}/event_{event_uuid}/activities_since_{since}", r_json
        )
        activities = r_json.get("activities") or r_json.get("event_activities", [])
        comments = []
        for activity in activities:
            comment = self._extract_activity_comment(activity)
            if comment:
                comments.append(self._format_activity_comment(activity, comment, user_names))
        if r_json.get("chunk") is True:
            comments.extend(
                self.get_event_activities(calendar_id, event_uuid, r_json["since"], user_names)
            )
        return comments

    def add_event_comments(self, calendar_id: int, events, calendar_users=None, num_workers=10):
        """Attach comments from event activities to event payloads using thread pool."""
        user_names = self._calendar_user_names(calendar_users)

        events_by_uuid = {event.get("uuid"): event for event in events if event.get("uuid")}

        if not events_by_uuid:
            return events

        # Use ThreadPoolExecutor to fetch activities concurrently.
        max_workers = max(1, num_workers)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all activity fetch tasks
            future_to_event_uuid = {
                executor.submit(
                    self.get_event_activities,
                    calendar_id,
                    event_uuid,
                    user_names=user_names,
                ): event_uuid
                for event_uuid in events_by_uuid
            }

            # Collect results as they complete
            for future in as_completed(future_to_event_uuid):
                event_uuid = future_to_event_uuid[future]
                try:
                    comments = future.result()
                    if comments:
                        events_by_uuid[event_uuid]["comments"] = comments
                except Exception as e:
                    logger.warning("Failed to fetch activities for event %s: %s", event_uuid, e)

        return events

    def get_events(
        self,
        calendar_id: int,
        calendar_name: str = None,
        calendar_users=None,
        include_comments: bool = False,
        num_workers: int = 10,
    ):
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

        if include_comments:
            logger.warning(
                "Exporting comments requires extra TimeTree requests per event and may take "
                "much longer or trigger rate limits."
            )
            return self.add_event_comments(calendar_id, events, calendar_users, num_workers)
        return events

    def get_public_events(self, calendar_id: int, calendar_name: str = None):
        """
        Get events from a public calendar.
        """
        url = f"{API_V2_BASEURI}/public_calendars/{calendar_id}/public_events"
        events = []
        cursor = None
        while True:
            params = {"from": PUBLIC_EVENTS_FROM}
            if cursor:
                params["cursor"] = cursor
            response = self.session.get(
                url,
                headers={"Content-Type": "application/json", "X-Timetreea": API_USER_AGENT},
                params=params,
            )
            if response.status_code != 200:
                if calendar_name is not None:
                    logger.error("Failed to get events of the public calendar '%s'", calendar_name)
                else:
                    logger.error("Failed to get events of the public calendar")
                logger.error(response.text)
                raise HTTPError("Failed to get public calendar events")

            r_json = response.json()
            response_name = f"public_calendar_{calendar_id}/public_events"
            if cursor:
                response_name = f"{response_name}_cursor_{cursor}"
            self._record_raw_response(response_name, r_json)
            events.extend(r_json["public_events"])
            paging = r_json.get("paging") or {}
            if not paging.get("next"):
                break
            cursor = paging.get("next_cursor")
            if not cursor:
                logger.error("Public events response has paging.next but no next_cursor")
                raise HTTPError("Failed to get public calendar events")

        logger.info("Fetched %d public events", len(events))
        logger.debug(
            "Top 5 fetched public events: \n %s",
            json.dumps(events[:5], indent=2, ensure_ascii=False),
        )

        return events
