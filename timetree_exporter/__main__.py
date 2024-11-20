"""
This module login in to TimeTree and converts Timetree events to iCal format.
"""

import argparse
import logging
import os
from getpass import getpass
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter
from timetree_exporter.auth import login
from timetree_exporter.calendar import TimeTreeCalendar


logger = logging.getLogger(__name__)
package_logger = logging.getLogger(__package__)


def get_events(email: str, password: str):
    """Get events from the Timetree API."""
    session_id = login(email, password)
    calendar = TimeTreeCalendar(session_id)
    metadatas = calendar.get_metadata()
    for i, metadata in enumerate(metadatas):
        print(f"{i+1}. id: {str(metadata['id'])}, name: {metadata['name']}")
    calendar_num = input("Which Calendar do you want to export?(Default to 1)")
    if calendar_num == "":
        calendar_num = 1
    elif not calendar_num.isdigit():
        print("Calendar Number must be a number")
        raise ValueError
    else:
        calendar_num = int(calendar_num)

    if calendar_num > len(metadatas) or calendar_num < 1:
        print("Invalid Calendar Number, must be between 1 and", len(metadatas))
        raise ValueError

    calendar_id = metadatas[int(calendar_num) - 1]["id"]
    calendar_name = metadatas[int(calendar_num) - 1]["name"]

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
        default="timetree.ics",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Email address",
        default=None,
    )
    args = parser.parse_args()

    if args.email is None:
        email = input("Enter your email address: ")
    else:
        email = args.email
    password = getpass("Enter your password: ")

    # Set logging level
    if args.verbose:
        package_logger.setLevel(logging.DEBUG)

    cal = Calendar()
    events = get_events(email, password)

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

    # Write calendar to file
    with open(args.output, "wb") as f:  # Path Traversal Vulnerability if on a server
        f.write(cal.to_ical())
        logger.info(
            "The .ics calendar file is saved to %s", os.path.abspath(args.output)
        )


if __name__ == "__main__":
    main()
