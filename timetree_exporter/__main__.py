"""
This module login in to TimeTree and converts Timetree events to iCal format.
"""

import argparse
import logging
import os
import re
from collections import defaultdict
from importlib.metadata import version
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter, __version__
from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import TimeTreeCalendar
from timetree_exporter.utils import safe_getpass

logger = logging.getLogger(__name__)
package_logger = logging.getLogger(__package__)


def select_calendar(email: str, password: str, calendar_code: str):
    """Authenticate and select a calendar. Returns (calendar_api, calendar_id, calendar_name)."""
    use_code = bool(calendar_code)
    session_id = login(email, password)
    calendar = TimeTreeCalendar(session_id)
    metadatas = calendar.get_metadata()

    # Filter out deactivated calendars
    metadatas = [
        metadata for metadata in metadatas if metadata["deactivated_at"] is None
    ]

    if len(metadatas) == 0:
        logger.error("No active calendars found")
        raise ValueError

    if calendar_code:
        # Filter calendars by code
        filtered_metadatas = [
            metadata
            for metadata in metadatas
            if metadata["alias_code"] == calendar_code
        ]

        if len(filtered_metadatas) == 0:
            logger.error("No calendars found with the specified codes")
            use_code = False
        else:
            metadata = filtered_metadatas[0]
            print(
                f"Using calendar: {metadata['name']} (code: {metadata['alias_code']})"
            )
            use_code = True

    if not use_code:
        # Print out the list of calendars for the user to choose from
        for i, metadata in enumerate(metadatas):
            print(
                f"{i+1}. {metadata['name'] if metadata['name'] else 'Unnamed'} "
                f"(code: {metadata['alias_code']})"
            )

        # Ask the user to choose a calendar
        calendar_num = (
            input("Which Calendar(s) do you want to export? (Default to 1): ") or "1"
        )
        if not calendar_num.isdigit() or not 1 <= int(calendar_num) <= len(metadatas):
            raise ValueError(
                f"Invalid Calendar Number. Must be a number between 1 and {len(metadatas)}"
            )
        idx = int(calendar_num) - 1
        metadata = metadatas[idx]

    return calendar, metadata["id"], metadata["name"]


def get_events(email: str, password: str, calendar_code: str):
    """Get events from the Timetree API."""
    calendar, calendar_id, calendar_name = select_calendar(
        email, password, calendar_code
    )
    return calendar.get_events(calendar_id, calendar_name)


def create_calendar():
    """Create a new iCalendar object with standard properties."""
    cal = Calendar()
    cal.add("prodid", f"-//TimeTree Exporter {version('timetree_exporter')}//EN")
    cal.add("version", "2.0")
    return cal


def write_calendar(cal, output_path):
    """Write a calendar to an .ics file."""
    cal.add_missing_timezones()
    with open(output_path, "wb") as f:
        f.write(cal.to_ical())
        logger.info(
            "The .ics calendar file is saved to %s", os.path.abspath(output_path)
        )


def sanitize_filename(name):
    """Sanitize a string for use as a filename component."""
    # Replace any non-alphanumeric characters (except hyphen/underscore) with underscore
    return re.sub(r"[^\w\-]", "_", name).strip("_")


def main():
    """Main function for the Timetree Exporter."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Convert Timetree events to iCal format",
        prog="timetree_exporter",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output iCal file",
        default=os.path.join(os.getcwd(), "timetree.ics"),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        help="Email address",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--calendar_code",
        type=str,
        help="The Calendar Code you want to export",
        default=None,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--list-labels",
        help="List labels for the selected calendar and exit",
        action="store_true",
    )
    parser.add_argument(
        "--split-by-label",
        help="Export events into separate .ics files grouped by label",
        action="store_true",
    )
    args = parser.parse_args()

    if args.email:
        email = args.email
    elif os.environ.get("TIMETREE_EMAIL"):
        email = os.environ.get("TIMETREE_EMAIL")
    else:
        email = input("Enter your email address: ")

    if os.environ.get("TIMETREE_PASSWORD"):
        password = os.environ.get("TIMETREE_PASSWORD")
    else:
        password = safe_getpass(prompt="Enter your password: ", echo_char="*")

    # Set logging level
    if args.verbose:
        package_logger.setLevel(logging.DEBUG)

    calendar_api, calendar_id, calendar_name = select_calendar(
        email, password, args.calendar_code
    )

    # --list-labels: print labels and exit
    if args.list_labels:
        labels = calendar_api.get_labels(calendar_id)
        if not labels:
            print("No labels found (the API response format may differ — use -v to debug)")
        else:
            for i, (_label_id, label_info) in enumerate(labels.items(), 1):
                print(f"{i}. {label_info['name']} ({label_info['color']})")
        return

    events = calendar_api.get_events(calendar_id, calendar_name)
    logger.info("Found %d events", len(events))

    # Fetch labels if splitting by label
    labels = {}
    if args.split_by_label:
        labels = calendar_api.get_labels(calendar_id)
        logger.info("Found %d labels", len(labels))

    if args.split_by_label:
        # Group events by label_id
        grouped = defaultdict(list)
        for event in events:
            time_tree_event = TimeTreeEvent.from_dict(event)
            formatter_label_name = None
            group_key = None

            if time_tree_event.label_id is not None and time_tree_event.label_id in labels:
                label_info = labels[time_tree_event.label_id]
                formatter_label_name = label_info["name"]
                group_key = time_tree_event.label_id
            else:
                group_key = None  # unlabeled

            formatter = ICalEventFormatter(time_tree_event, label_name=formatter_label_name)
            ical_event = formatter.to_ical()
            if ical_event is not None:
                grouped[group_key].append(ical_event)

        # Write each group to a separate file
        output_stem, output_ext = os.path.splitext(args.output)
        if not output_ext:
            output_ext = ".ics"

        for group_key, ical_events in grouped.items():
            if group_key is None:
                label_suffix = "unlabeled"
            else:
                label_suffix = sanitize_filename(labels[group_key]["name"])

            cal = create_calendar()
            for ical_event in ical_events:
                cal.add_component(ical_event)

            output_path = f"{output_stem}_{label_suffix}{output_ext}"
            logger.info(
                "%d events for label '%s'", len(ical_events), label_suffix
            )
            write_calendar(cal, output_path)

        total = sum(len(evts) for evts in grouped.values())
        logger.info(
            "A total of %d/%d events split into %d files",
            total, len(events), len(grouped),
        )
    else:
        # Standard single-file export
        cal = create_calendar()

        # Build label lookup for CATEGORIES
        label_lookup = {}
        if labels:
            label_lookup = {lid: info["name"] for lid, info in labels.items()}

        for event in events:
            time_tree_event = TimeTreeEvent.from_dict(event)
            label_name = label_lookup.get(time_tree_event.label_id)
            formatter = ICalEventFormatter(time_tree_event, label_name=label_name)
            ical_event = formatter.to_ical()
            if ical_event is None:
                continue
            cal.add_component(ical_event)

        logger.info(
            "A total of %d/%d events are added to the calendar",
            len(cal.subcomponents),
            len(events),
        )

        write_calendar(cal, args.output)


if __name__ == "__main__":
    main()
