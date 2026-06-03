"""
This module provides the ICalEventFormatter class
for formatting TimeTree events into iCalendar format.
"""

import logging
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from icalendar import Alarm, Event, vDate, vDatetime, vGeo, vRecur
from icalendar.parser import Contentline
from icalendar.prop import vDDDLists

from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventCategory,
    TimeTreeEventType,
)
from timetree_exporter.utils import convert_timestamp_to_datetime

logger = logging.getLogger(__name__)


class ICalEventFormatter:
    """
    Class for formatting TimeTree events into iCalendar format.
    """

    def __init__(
        self,
        time_tree_event: TimeTreeEvent,
        label_name: str = None,
        color: str = None,
        category_names: list = None,
    ):
        self.time_tree_event = time_tree_event
        self.label_name = label_name
        self._color = color
        self.category_names = category_names or []

    @property
    def color(self):
        """Return the validated color value."""
        if self._color is None:
            return None
        if self._is_valid_hex_color(self._color):
            return self._color
        logger.warning("Invalid color format: %s. Expected hex color (e.g., #RRGGBB)", self._color)
        return None

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        """Validate hex color format."""
        if not isinstance(color, str):
            return False
        color = color.strip()
        # Check for hex color format: #RRGGBB or #RRGGBBAA
        if color.startswith("#") and len(color) in (7, 9):
            try:
                int(color[1:], 16)
                return True
            except ValueError:
                return False
        return False

    @property
    def categories(self):
        """Return label and public hashtag names as CATEGORIES."""
        categories = []
        if self.label_name:
            categories.append(self.label_name)
        categories.extend(self.category_names)
        return categories or None

    @property
    def uid(self):
        """Return the UUID of the event."""
        return self.time_tree_event.uuid

    @property
    def summary(self):
        """Return the title of the event."""
        return self.time_tree_event.title

    @property
    def created(self):
        """Return the creation time of the event."""
        return vDatetime(
            convert_timestamp_to_datetime(self.time_tree_event.created_at / 1000, ZoneInfo("UTC"))
        )

    @property
    def last_modified(self):
        """Return the last modification time of the event."""
        return vDatetime(
            convert_timestamp_to_datetime(self.time_tree_event.updated_at / 1000, ZoneInfo("UTC"))
        )

    @property
    def description(self):
        """Return the note of the event."""
        return self.time_tree_event.note if self.time_tree_event.note != "" else None

    @property
    def comments(self):
        """Return event comments."""
        return self.time_tree_event.comments or []

    @property
    def location(self):
        """Return the location of the event."""
        return self.time_tree_event.location if self.time_tree_event.location != "" else None

    @property
    def location_altrep(self):
        """Return an alternate representation URI for the location."""
        return getattr(self.time_tree_event, "location_url", None)

    @property
    def geo(self):
        """Return the geolocation of the event."""
        if self.time_tree_event.location_lat is None or self.time_tree_event.location_lon is None:
            return None
        return vGeo((self.time_tree_event.location_lat, self.time_tree_event.location_lon))

    @property
    def url(self):
        """Return the URL of the event."""
        return self.time_tree_event.url if self.time_tree_event.url != "" else None

    @property
    def source(self):
        """Return the source URL of the event."""
        return getattr(self.time_tree_event, "source_url", None)

    @property
    def images(self):
        """Return image URLs for the event."""
        return getattr(self.time_tree_event, "image_urls", None) or []

    @property
    def thumbnail_images(self):
        """Return thumbnail image URLs for the event."""
        return getattr(self.time_tree_event, "thumbnail_image_urls", None) or []

    @property
    def related_to(self):
        """Return the related event UID."""
        return self.time_tree_event.recurring_uuid or self.time_tree_event.parent_id

    def get_datetime(self, is_start_time):
        """Return the start or end time of the event."""
        if is_start_time:
            time = self.time_tree_event.start_at
            timezone = self.time_tree_event.start_timezone
        else:
            time = self.time_tree_event.end_at
            timezone = self.time_tree_event.end_timezone

        if self.time_tree_event.all_day:
            datetime_value = convert_timestamp_to_datetime(
                time / 1000,
                ZoneInfo(timezone),
            )
            if not is_start_time:
                # RFC 5545 all-day DTEND is exclusive.
                datetime_value += timedelta(days=1)
            return vDate(datetime_value)
        return vDatetime(
            convert_timestamp_to_datetime(
                time / 1000,
                ZoneInfo(timezone),
            ),
            params={"TZID": timezone} if timezone != "UTC" else {},
        )

    @property
    def dtstart(self):
        """Return the start time of the event."""
        return self.get_datetime(is_start_time=True)

    @property
    def dtend(self):
        """Return the end time of the event."""
        return self.get_datetime(is_start_time=False)

    @property
    def alarms(self):
        """Return the alarms of the event."""
        if self.time_tree_event.alerts is None:
            return []
        alarms = []
        for alert in self.time_tree_event.alerts:
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add("description", "Reminder")
            alarm.add("trigger", timedelta(minutes=-alert))
            alarms.append(alarm)
        return alarms

    def add_recurrences(self, event):
        """Add recurrences to iCal event"""
        if self.time_tree_event.recurrences is None:
            return
        for recurrence in self.time_tree_event.recurrences:
            contentline = Contentline(recurrence)
            name, parameters, value = contentline.parts()
            if name.lower() == "rrule":
                recurrence_rule = vRecur.from_ical(value)
                until = recurrence_rule.get("UNTIL")
                if "COUNT" in recurrence_rule and until:
                    logger.error("RRULE must not include both COUNT and UNTIL: %s", recurrence)
                    raise ValueError("RRULE must not include both COUNT and UNTIL")
                if (
                    until
                    and not self.time_tree_event.all_day
                    and isinstance(until[0], date)
                    and not isinstance(until[0], datetime)
                ):
                    local_until = datetime.combine(
                        until[0],
                        time(23, 59, 59),
                        ZoneInfo(self.time_tree_event.start_timezone),
                    )
                    recurrence_rule["UNTIL"] = [local_until.astimezone(ZoneInfo("UTC"))]
                event.add(name, recurrence_rule, parameters)
            elif name.lower() == "exdate" or name.lower() == "rdate":
                event.add(name, vDDDLists.from_ical(value), parameters)
            else:
                logger.error("Unknown recurrence type: %s", name)
                raise ValueError(f"Unknown recurrence type: {name}")

    def to_ical(self) -> Event:
        """Return the iCal event."""
        if (
            self.time_tree_event.event_type == TimeTreeEventType.BIRTHDAY
        ):  # Skip if event is a birthday
            logger.debug(
                "Skipping birthday event\n \
                    uid: %s \n \
                    summary: '%s' \n \
                    time: %s ~ %s \n \
                    ",
                self.uid,
                self.summary,
                self.dtstart.dt.strftime("%Y-%m-%d %H:%M:%S"),
                self.dtend.dt.strftime("%Y-%m-%d %H:%M:%S"),
            )

            return None
        if self.time_tree_event.category == TimeTreeEventCategory.MEMO:
            # Skip if event is a memo
            logger.debug(
                "Skipping memo event\n \
                    uid: %s \n \
                    summary: '%s' \n \
                    time: %s ~ %s \n \
                    ",
                self.uid,
                self.summary,
                self.dtstart.dt.strftime("%Y-%m-%d %H:%M:%S"),
                self.dtend.dt.strftime("%Y-%m-%d %H:%M:%S"),
            )

            return None

        event = Event()

        event.add("uid", self.uid)
        event.add("summary", self.summary)
        event.add("dtstamp", datetime.now(ZoneInfo("UTC")))
        event.add("created", self.created)
        event.add("last-modified", self.last_modified)
        event.add("dtstart", self.dtstart)
        event.add("dtend", self.dtend)

        if self.location:
            params = {"ALTREP": self.location_altrep} if self.location_altrep else {}
            event.add("location", self.location, parameters=params)
        if self.geo:
            event.add("geo", self.geo)
        if self.url:
            event.add("url", self.url)
        if self.source:
            event.add("source", self.source, parameters={"VALUE": "URI"})
        for image_url in self.images:
            event.add("image", image_url, parameters={"VALUE": "URI", "DISPLAY": "FULLSIZE"})
        for image_url in self.thumbnail_images:
            event.add("image", image_url, parameters={"VALUE": "URI", "DISPLAY": "THUMBNAIL"})
        if self.description:
            event.add("description", self.description)
        for comment in self.comments:
            event.add("comment", comment)
        if self.related_to:
            event.add("related-to", self.related_to)
        if self.categories:
            event.add("categories", self.categories)
        if self.color:
            event.add("color", self.color)

        for alarm in self.alarms:
            event.add_component(alarm)

        self.add_recurrences(event)

        return event
