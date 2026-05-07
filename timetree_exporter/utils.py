"""Utility functions for Timetree Exporter"""

import getpass
import inspect
import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Timezone

logger = logging.getLogger(__name__)


def get_events_from_file(file_path) -> list:
    """Fetch events from Timetree response file"""
    try:
        with Path(file_path).open(encoding="UTF-8") as response_file:
            response_data = json.load(response_file)
            if "events" in response_data:
                return response_data["events"]
            if "public_events" in response_data:  # Partal support for public events
                return response_data["public_events"]
            logger.error(
                "Invalid response file: %s. \n No 'events' or 'public_events' column in the file",
                file_path,
            )
            return None
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return None


def paths_to_filelist(paths: list) -> list:
    """Converts a list of paths to a list of files"""
    filenames = []
    for path in paths:
        path_obj = Path(path)
        if path_obj.is_dir():
            filenames += [str(file) for file in path_obj.iterdir()]
        elif path_obj.is_file():
            filenames.append(path)
        else:
            logger.error("Invalid path: %s", path)
    return filenames


def convert_timestamp_to_datetime(timestamp, tzinfo=None):
    """
    Convert timestamp to datetime for both positive and negative timestamps on different platforms.
    """
    if tzinfo is None:
        tzinfo = ZoneInfo("UTC")
    if timestamp >= 0:
        return datetime.fromtimestamp(timestamp, tzinfo)
    return datetime.fromtimestamp(0, tzinfo) + timedelta(seconds=int(timestamp))


def get_timezone_date_ranges(cal):
    """Return the exported event date range for each referenced TZID."""
    ranges = {}

    for component in cal.subcomponents:
        if component.name != "VEVENT":
            continue

        for property_name in ("dtstart", "dtend"):
            property_value = component.get(property_name)
            if property_value is None:
                continue

            tzid = property_value.params.get("TZID")
            if not tzid:
                continue

            datetime_value = property_value.dt
            event_date = (
                datetime_value.date() if isinstance(datetime_value, datetime) else datetime_value
            )
            if not isinstance(event_date, date):
                continue

            first_date, last_date = ranges.get(tzid, (event_date, event_date))
            ranges[tzid] = (min(first_date, event_date), max(last_date, event_date))

    return ranges


def add_bounded_timezones_before_events(cal):
    """Add VTIMEZONE components bounded to the exported event date ranges."""
    timezone_components = []

    for tzid, (first_date, last_date) in sorted(get_timezone_date_ranges(cal).items()):
        logger.debug(
            "Adding VTIMEZONE for TZID=%s with date range %s to %s", tzid, first_date, last_date
        )
        try:
            timezone = Timezone.from_tzid(
                tzid,
                first_date=first_date - timedelta(days=1),
                last_date=last_date + timedelta(days=1),
            )
        except ValueError:
            logger.warning("Skipping unknown timezone: %s", tzid)
            continue

        timezone_components.append(timezone)

    if timezone_components:
        timezone_line_count = sum(
            len(timezone.to_ical().decode("utf-8").splitlines()) for timezone in timezone_components
        )
        if timezone_line_count > 200:
            logger.warning(
                "Generated VTIMEZONE blocks contain %d lines; Google Calendar may fail to "
                "import the file correctly or corrupt non-ASCII text",
                timezone_line_count,
            )
        cal.subcomponents = timezone_components + cal.subcomponents


def safe_getpass(prompt="Password: ", echo_char=None):
    """Safely get a password from the user, supporting echo_char for Python 3.14+.
    If echo_char is not supported, it falls back to the pwinput module if echo_char is needed.
    """
    sig = inspect.signature(getpass.getpass)
    if "echo_char" in sig.parameters:
        # Python 3.14+ supports echo_char
        return getpass.getpass(  # pylint: disable=E1123
            prompt=prompt, echo_char=echo_char
        )
    if echo_char is not None:
        # Use pwinput for echo_char support in older versions
        try:
            from pwinput import pwinput  # pylint: disable=C0415

            return pwinput(prompt=prompt, mask=echo_char)
        except ImportError as exc:
            logger.error("pwinput module is required for echo_char support.")
            raise ImportError("Please install pwinput to use echo_char functionality.") from exc
    else:
        # Fallback for older versions
        return getpass.getpass(prompt=prompt)
