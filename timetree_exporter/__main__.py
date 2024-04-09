"""
This module converts Timetree events to iCal format.
It is intended to be used with the Timetree API response files.
https://timetreeapp.com/api/v1/calendar/{calendar_id}/events/sync
"""

import argparse
from icalendar import Calendar
from timetree_exporter import TimeTreeEvent, ICalEventFormatter
from timetree_exporter.utils import get_events_from_file, paths_to_filelist


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
    args = parser.parse_args()

    cal = Calendar()
    filenames = paths_to_filelist(args.input)

    for filename in filenames:
        # Skip non-JSON files
        if not filename.endswith(".json"):
            print(f"Skipping {filename} (Invalid file type, should be .json)")
            continue
        print(f"Parsing {filename}")

        # Get events from file
        events = get_events_from_file(filename)
        if events is None:
            continue

        # Add events to calendar
        for event in events:
            time_tree_event = TimeTreeEvent.from_dict(event)
            formatter = ICalEventFormatter(time_tree_event)
            ical_event = formatter.to_ical()
            if ical_event is None:
                continue
            cal.add_component(ical_event)

    # Write calendar to file
    with open(args.output, "wb") as f:  # Path Traversal Vulnerability if on a server
        f.write(cal.to_ical())


if __name__ == "__main__":
    main()
