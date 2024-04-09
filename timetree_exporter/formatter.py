"""
This module provides the ICalEventFormatter class 
for formatting TimeTree events into iCalendar format.
"""

from datetime import datetime, timedelta
from icalendar import Event, vRecur, vDate, vDatetime, vGeo
from icalendar.prop import vDDDLists
from icalendar.parser import Contentline
from dateutil import tz
from timetree_exporter.event import TimeTreeEvent, TimeTreeEventType
from timetree_exporter.utils import convert_timestamp_to_datetime


class ICalEventFormatter:
    """
    Class for formatting TimeTree events into iCalendar format.
    """

    def __init__(self, time_tree_event: TimeTreeEvent):
        self.time_tree_event = time_tree_event

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
            convert_timestamp_to_datetime(
                self.time_tree_event.created_at / 1000, tz.tzutc()
            )
        )

    @property
    def last_modify(self):
        """Return the last modification time of the event."""
        return vDatetime(
            convert_timestamp_to_datetime(
                self.time_tree_event.updated_at / 1000, tz.tzutc()
            )
        )

    @property
    def description(self):
        """Return the note of the event."""
        return self.time_tree_event.note if self.time_tree_event.note != "" else None

    @property
    def location(self):
        """Return the location of the event."""
        return (
            self.time_tree_event.location
            if self.time_tree_event.location != ""
            else None
        )

    @property
    def geo(self):
        """Return the geolocation of the event."""
        if (
            self.time_tree_event.location_lat is None
            or self.time_tree_event.location_lon is None
        ):
            return None
        return vGeo(
            (self.time_tree_event.location_lat, self.time_tree_event.location_lon)
        )

    @property
    def url(self):
        """Return the URL of the event."""
        return self.time_tree_event.url if self.time_tree_event.url != "" else None

    @property
    def related_to(self):
        """Return the parent ID of the event."""
        return self.time_tree_event.parent_id

    def get_datetime(self, is_start_time):
        """Return the start or end time of the event."""
        if is_start_time:
            time = self.time_tree_event.start_at
            timezone = self.time_tree_event.start_timezone
        else:
            time = self.time_tree_event.end_at
            timezone = self.time_tree_event.end_timezone

        if self.time_tree_event.all_day:
            return vDate(
                convert_timestamp_to_datetime(
                    time / 1000,
                    tz.gettz(timezone),
                )
            )
        return vDatetime(
            convert_timestamp_to_datetime(
                time / 1000,
                tz.gettz(timezone),
            )
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
    def alerts(self):
        """Return the alerts of the event."""
        alerts = []
        for alert in self.time_tree_event.alerts:
            alarm = Event()
            alarm.add("action", "DISPLAY")
            alarm.add("description", "Reminder")
            alarm.add("trigger", timedelta(minutes=-alert))
            alerts.append(alarm)
        return alerts

    def add_recurrences(self, event):
        """Add recurrences to iCal event"""
        for recurrence in self.time_tree_event.recurrences:
            contentline = Contentline(recurrence)
            name, parameters, value = contentline.parts()
            if name.lower() == "rrule":
                event.add(name, vRecur.from_ical(value), parameters)
            elif name.lower() == "exdate" or name.lower() == "rdate":
                event.add(name, vDDDLists.from_ical(value), parameters)
            else:
                raise ValueError(f"Unknown recurrence type: {name}")

    def to_ical(self) -> Event:
        """Return the iCal event."""
        if (
            self.time_tree_event.event_type == TimeTreeEventType.BIRTHDAY
        ):  # Skip if event is a birthday
            return None

        event = Event()

        event.add("uid", self.uid)
        event.add("summary", self.summary)
        event.add("dtstamp", datetime.now(tz.tzutc()))
        event.add("created", self.created)
        event.add("last-modify", self.last_modify)
        event.add("dtstart", self.dtstart)
        event.add("dtend", self.dtend)

        if self.location:
            event.add("location", self.location)
        if self.geo:
            event.add("geo", self.geo)
        if self.url:
            event.add("url", self.url)
        if self.description:
            event.add("description", self.description)
        if self.related_to:
            event.add("related-to", self.related_to)

        for alert in self.alerts:
            event.add_component(alert)

        self.add_recurrences(event)

        return event
