"""
This module login in to TimeTree and converts Timetree events to iCal format.
"""

import argparse
import logging
import os
import re
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path

from icalendar import Calendar

from timetree_exporter import ICalEventFormatter, TimeTreeEvent, __version__
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
    metadatas = [metadata for metadata in metadatas if metadata["deactivated_at"] is None]

    if len(metadatas) == 0:
        logger.error("No active calendars found")
        raise ValueError

    if calendar_code:
        # Filter calendars by code
        filtered_metadatas = [
            metadata for metadata in metadatas if metadata["alias_code"] == calendar_code
        ]

        if len(filtered_metadatas) == 0:
            logger.error("No calendars found with the specified codes")
            use_code = False
        else:
            metadata = filtered_metadatas[0]
            print(f"Using calendar: {metadata['name']} (code: {metadata['alias_code']})")
            use_code = True

    if not use_code:
        # Print out the list of calendars for the user to choose from
        for i, metadata in enumerate(metadatas):
            print(
                f"{i + 1}. {metadata['name'] if metadata['name'] else 'Unnamed'} "
                f"(code: {metadata['alias_code']})"
            )

        # Ask the user to choose a calendar
        calendar_num = input("Which Calendar(s) do you want to export? (Default to 1): ") or "1"
        if not calendar_num.isdigit() or not 1 <= int(calendar_num) <= len(metadatas):
            raise ValueError(
                f"Invalid Calendar Number. Must be a number between 1 and {len(metadatas)}"
            )
        idx = int(calendar_num) - 1
        metadata = metadatas[idx]

    return calendar, metadata["id"], metadata["name"]


def get_events(email: str, password: str, calendar_code: str):
    """Get events from the Timetree API."""
    calendar, calendar_id, calendar_name = select_calendar(email, password, calendar_code)
    return calendar.get_events(calendar_id, calendar_name)


def create_calendar():
    """Create a new iCalendar object with standard properties."""
    cal = Calendar()
    cal.add("prodid", f"-//TimeTree Exporter {version('timetree_exporter')}//EN")
    cal.add("version", "2.0")
    return cal


def write_calendar(cal, output_path: str):
    """Write a calendar to an .ics file."""
    # Disable add missing timezones for since it causes issues with Google Calendar. See Issue #157
    # TODO: Revisit this after bug fixed in Google Calendar
    # cal.add_missing_timezones()

    # Transform the output path to a Path object for better handling
    path = Path(output_path)
    with path.open("wb") as f:
        f.write(cal.to_ical())
        logger.info("The .ics calendar file is saved to %s", path.resolve())


def sanitize_filename(name):
    """Sanitize a string for use as a filename component."""
    # Replace any non-alphanumeric characters (except hyphen/underscore) with underscore
    return re.sub(r"[^\w\-]", "_", name).strip("_")


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Timetree events to iCal format",
        prog="timetree_exporter",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output iCal file",
        default=str(Path.cwd() / "timetree.ics"),
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
    return parser.parse_args()


def resolve_email(cli_email):
    """Resolve email from CLI arg, env var, or prompt."""
    if cli_email:
        return cli_email
    env_email = os.environ.get("TIMETREE_EMAIL")
    if env_email:
        return env_email
    return input("Enter your email address: ")


def resolve_password():
    """Resolve password from env var or prompt."""
    env_password = os.environ.get("TIMETREE_PASSWORD")
    if env_password:
        return env_password
    return safe_getpass(prompt="Enter your password: ", echo_char="*")


def configure_logging(verbose):
    """Configure package logging level based on CLI flags."""
    if verbose:
        package_logger.setLevel(logging.DEBUG)


def list_labels_and_exit(calendar_api, calendar_id):
    """Print labels for a calendar and return."""
    labels = calendar_api.get_labels(calendar_id)
    if not labels:
        print("No labels found (the API response format may differ — use -v to debug)")
        return

    for i, (_label_id, label_info) in enumerate(labels.items(), 1):
        color_hex = (label_info.get("color") or "").strip()
        normalized = color_hex.lstrip("#")

        if len(normalized) == 6 and re.fullmatch(r"[0-9A-Fa-f]{6}", normalized):
            r = int(normalized[0:2], 16)
            g = int(normalized[2:4], 16)
            b = int(normalized[4:6], 16)
            dot = f"\033[38;2;{r};{g};{b}m●\033[0m"
        else:
            dot = "●"

        print(f"{i:>2}. {dot} {label_info['name']}")


def fetch_labels(calendar_api, calendar_id):
    """Fetch labels and log count."""
    labels = calendar_api.get_labels(calendar_id)
    logger.info("Found %d labels", len(labels))
    return labels


def build_single_calendar(events, labels):
    """Build single output calendar from events."""
    cal = create_calendar()
    label_lookup = {lid: info["name"] for lid, info in labels.items()} if labels else {}
    color_lookup = {lid: info["color"] for lid, info in labels.items()} if labels else {}

    for event in events:
        time_tree_event = TimeTreeEvent.from_dict(event)
        label_name = label_lookup.get(time_tree_event.label_id)
        color = color_lookup.get(time_tree_event.label_id)
        formatter = ICalEventFormatter(time_tree_event, label_name=label_name, color=color)
        ical_event = formatter.to_ical()
        if ical_event is not None:
            cal.add_component(ical_event)

    return cal


def group_events_by_label(events, labels):
    """Group converted iCal events by label id (or None for unlabeled)."""
    grouped = defaultdict(list)

    for event in events:
        time_tree_event = TimeTreeEvent.from_dict(event)
        label_info = labels.get(time_tree_event.label_id)
        label_name = label_info["name"] if label_info is not None else None
        color = label_info["color"] if label_info is not None else None
        formatter = ICalEventFormatter(time_tree_event, label_name=label_name, color=color)
        ical_event = formatter.to_ical()

        if ical_event is None:
            continue

        group_key = time_tree_event.label_id if label_info is not None else None
        grouped[group_key].append(ical_event)

    return grouped


def label_suffix_for_group(group_key, labels):
    """Return output filename suffix for a label group."""
    if group_key is None:
        return "unlabeled"
    name = sanitize_filename(labels[group_key]["name"])
    if name:
        return name
    return sanitize_filename(f"label_{group_key}")


def write_split_calendars(grouped_events, labels, output, event_count):
    """Write grouped events into separate calendar files."""
    output_path = Path(output)

    for group_key, ical_events in grouped_events.items():
        label_suffix = label_suffix_for_group(group_key, labels)
        cal = create_calendar()
        for ical_event in ical_events:
            cal.add_component(ical_event)
        if output_path.suffix:
            split_path = output_path.with_name(
                f"{output_path.stem}_{label_suffix}{output_path.suffix}"
            )
        else:
            split_path = output_path.with_name(f"{output_path.name}_{label_suffix}.ics")
        logger.info("%d events for label '%s'", len(ical_events), label_suffix)
        write_calendar(cal, split_path)

    total = sum(len(evts) for evts in grouped_events.values())
    logger.info(
        "A total of %d/%d events split into %d files",
        total,
        event_count,
        len(grouped_events),
    )


def main():
    """Main function for the Timetree Exporter."""
    args = parse_args()
    configure_logging(args.verbose)

    email = resolve_email(args.email)
    password = resolve_password()
    calendar_api, calendar_id, calendar_name = select_calendar(email, password, args.calendar_code)

    if args.list_labels:
        list_labels_and_exit(calendar_api, calendar_id)
        return

    events = calendar_api.get_events(calendar_id, calendar_name)
    logger.info("Found %d events", len(events))
    labels = fetch_labels(calendar_api, calendar_id)

    if args.split_by_label:
        grouped_events = group_events_by_label(events, labels)
        write_split_calendars(grouped_events, labels, args.output, len(events))
        return

    cal = build_single_calendar(events, labels)
    logger.info(
        "A total of %d/%d events are added to the calendar",
        len(cal.subcomponents),
        len(events),
    )

    write_calendar(cal, args.output)


if __name__ == "__main__":
    main()
