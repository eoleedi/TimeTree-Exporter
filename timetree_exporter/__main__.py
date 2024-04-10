"""
This module converts Timetree events to iCal format.
It is intended to be used with the Timetree API response files.
https://timetreeapp.com/api/v1/calendar/{calendar_id}/events/sync
"""

import argparse
import logging
import os
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter
from timetree_exporter.utils import get_events_from_file, paths_to_filelist


logger = logging.getLogger(__name__)
package_logger = logging.getLogger(__package__)


def main():
    """Main function for the Timetree Exporter."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Convert Timetree events to iCal format",
        prog="timetree_exporter",
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to the Timetree response file(s)/folder",
        nargs="+",
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
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        package_logger.setLevel(logging.DEBUG)

    cal = Calendar()
    filenames = paths_to_filelist(args.input)
    imported_events_count = 0

    for filename in filenames:
        # Skip non-JSON files
        if not filename.endswith(".json"):
            logger.warning("Skipping %s (Invalid file type, should be .json)", filename)
            continue
        logger.info("Parsing %s", filename)

        # Get events from file
        events = get_events_from_file(filename)
        if events is None:
            continue

        imported_events_count += len(events)

        # Add events to calendar
        for event in events:
            time_tree_event = TimeTreeEvent.from_dict(event)
            formatter = ICalEventFormatter(time_tree_event)
            ical_event = formatter.to_ical()
            if ical_event is None:
                continue
            cal.add_component(ical_event)
    logger.info(
        "A Total of %d/%d events added to the calendar",
        len(cal.subcomponents),
        imported_events_count,
    )

    # Write calendar to file
    with open(args.output, "wb") as f:  # Path Traversal Vulnerability if on a server
        f.write(cal.to_ical())
        logger.info(
            "The .ics calendar file is saved to %s", os.path.abspath(args.output)
        )


if __name__ == "__main__":
    main()
