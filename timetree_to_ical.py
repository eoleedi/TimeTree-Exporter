"""
This module converts Timetree events to iCal format.
It is intended to be used with the Timetree API response files.
https://timetreeapp.com/api/v1/calendar/{calendar_id}/events/sync
"""
import json
import os
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from dateutil import tz


def convert_to_ical(events_raw: json, calendar: Calendar = None):
    """Convert Timetree events to iCal format"""
    if calendar is None:
        calendar = Calendar()

    for event_raw in events_raw:
        event = Event()

        # Add basic event details
        event.add("uid", event_raw["uuid"])
        event.add("summary", event_raw["title"])
        event.add("dtstamp", datetime.now(timezone.utc))

        # Add start and end times with timezone handling
        try:
            event.add(
                "dtstart",
                datetime.fromtimestamp(
                    event_raw["start_at"] / 1000, tz.gettz(event_raw["start_timezone"])
                ),
            )
            event.add(
                "dtend",
                datetime.fromtimestamp(
                    event_raw["end_at"] / 1000, tz.gettz(event_raw["end_timezone"])
                ),
            )
        except KeyError as error:
            print(f"Missing key in event data: {error}")
            continue

        # Add location if available
        if event_raw.get("location") != "":
            event.add("location", event_raw.get("location"))

        # Add description if available
        if event_raw.get("note") is not None:
            event.add("description", event_raw.get("note"))

        # Add URL if available
        if event_raw.get("url") is not None:
            event.add("url", event_raw.get("url"))

        # Add alarms if available
        for alert_minutes in event_raw.get("alerts", []):
            alarm = Event()
            alarm.add("action", "DISPLAY")
            alarm.add("description", "Reminder")
            alarm.add("trigger", timedelta(minutes=-alert_minutes))
            event.add_component(alarm)

        calendar.add_component(event)

    return calendar.to_ical()


def fetch_events(file_path):
    """Fetch events from Timetree response file"""
    try:
        with open(file_path, "r", encoding="UTF-8") as response_file:
            response_data = json.load(response_file)
            return response_data["events"]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []


if __name__ == "__main__":
    responses = os.listdir("responses")
    cal = Calendar()
    for response in responses:
        if not response.endswith(".json"):
            continue
        print(f"Parsing {response}")
        events_data = fetch_events(f"responses/{response}")
        if events_data:
            ICAL_DATA = convert_to_ical(events_data, cal)

    with open("timetree.ics", "wb") as f:
        f.write(ICAL_DATA)