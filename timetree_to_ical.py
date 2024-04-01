"""
This module converts Timetree events to iCal format.
It is intended to be used with the Timetree API response files.
https://timetreeapp.com/api/v1/calendar/{calendar_id}/events/sync
"""

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from icalendar import (
    Calendar,
    Event,
    vRecur,
    vDate,
    vDatetime,
    vGeo,
)
from icalendar.prop import vDDDLists
from icalendar.parser import Contentline
from dateutil import tz

params_timetree2ical = {
    "note": "description",
    "location": "location",
    "url": "url",
}


def add_recurrences(event, event_raw):
    """Add recurrences to iCal event"""
    for recurrence in event_raw["recurrences"]:
        contentline = Contentline(recurrence)
        name, parameters, value = contentline.parts()
        if name.lower() == "rrule":
            event.add(name, vRecur.from_ical(value), parameters)
        elif name.lower() == "exdate" or name.lower() == "rdate":
            event.add(name, vDDDLists.from_ical(value), parameters)
        else:
            raise ValueError(f"Unknown recurrence type: {name}")


def add_event_datetime(event, event_raw, key):
    """Add event start or end time to iCal event"""
    if key not in ["start", "end"]:
        raise ValueError("Key must be 'start' or 'end'")

    event_datetime = datetime.fromtimestamp(
        event_raw[f"{key}_at"] / 1000, tz.gettz(event_raw[f"{key}_timezone"])
    )
    if event_raw["all_day"]:
        event.add(f"dt{key}", vDate(event_datetime))
    else:
        event.add(f"dt{key}", vDatetime(event_datetime))


def add_event_detail(event, event_raw, key, default=None):
    """Add event detail to iCal event"""
    value = event_raw.get(key, default)
    if value is not None and value != "":
        event.add(params_timetree2ical[key], value)


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
        event.add(
            "created",
            vDatetime(
                datetime.fromtimestamp(event_raw["created_at"] / 1000, tz.gettz("UTC"))
            ),
        )
        event.add(
            "last-modify",
            vDatetime(
                datetime.fromtimestamp(event_raw["updated_at"] / 1000, tz.gettz("UTC"))
            ),
        )

        # Add start and end times with timezone handling
        try:
            for key in ["start", "end"]:
                add_event_datetime(event, event_raw, key)
        except KeyError as error:
            print(f"Missing key in event data: {error}")
            continue

        # Add details if available
        for key in ["location", "note", "url"]:
            add_event_detail(event, event_raw, key)

        # Add lan, lon if available
        if event_raw.get("location_lat") and event_raw.get("location_lon"):
            event.add(
                "geo", vGeo((event_raw["location_lat"], event_raw["location_lon"]))
            )

        # Add recurrences if available
        if len(event_raw.get("recurrences")):  # Check if it's empty list
            add_recurrences(event, event_raw)

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
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Convert Timetree events to iCal format"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output iCal file",
        default="timetree.ics",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        help="Path to the Timetree response file(s)/folder",
        nargs="+",
        default=["responses"],
    )
    args = parser.parse_args()

    # Handling multiple files or folders
    filenames = []
    for path in args.path:
        if os.path.isdir(path):
            filenames += [os.path.join(path, file) for file in os.listdir(path)]
        elif os.path.isfile(path):
            filenames.append(path)
        else:
            print(f"Invalid path: {path}")

    # Convert to iCal format
    cal = Calendar()
    for filename in filenames:
        # Skip non-JSON files
        if not filename.endswith(".json"):
            print(f"Skipping {filename} (Invalid file type, should be .json)")
            continue
        print(f"Parsing {filename}")
        events_data = fetch_events(filename)
        if events_data:
            ICAL_DATA = convert_to_ical(events_data, cal)
            with open(args.output, "wb") as f:
                f.write(ICAL_DATA)
