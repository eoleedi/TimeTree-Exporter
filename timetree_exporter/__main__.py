"""
This module login in to TimeTree and converts Timetree events to iCal format.
"""

import argparse
import logging
import os
from importlib.metadata import version
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter, __version__
from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import TimeTreeCalendar
from timetree_exporter.utils import safe_getpass

logger = logging.getLogger(__name__)
package_logger = logging.getLogger(__package__)


def get_events(email: str, password: str, calendar_code: str):
    """Get events from the Timetree API."""
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

    # Get events from the selected calendar
    calendar_id = metadata["id"]
    calendar_name = metadata["name"]

    return calendar.get_events(calendar_id, calendar_name)


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

    # Set up calendar
    cal = Calendar()
    cal.add("prodid", f"-//TimeTree Exporter {version('timetree_exporter')}//EN")
    cal.add("version", "2.0")

    events = get_events(email, password, args.calendar_code)

    logger.info("Found %d events", len(events))

    # Add events to calendar
    for event in events:
        time_tree_event = TimeTreeEvent.from_dict(event)
        formatter = ICalEventFormatter(time_tree_event)
        ical_event = formatter.to_ical()
        if ical_event is None:
            continue
        cal.add_component(ical_event)

    logger.info(
        "A total of %d/%d events are added to the calendar",
        len(cal.subcomponents),
        len(events),
    )

    # Add the required timezone information
    cal.add_missing_timezones()

    # Write calendar to file
    with open(args.output, "wb") as f:  # Path Traversal Vulnerability if on a server
        f.write(cal.to_ical())
        logger.info(
            "The .ics calendar file is saved to %s", os.path.abspath(args.output)
        )


if __name__ == "__main__":
    main()
