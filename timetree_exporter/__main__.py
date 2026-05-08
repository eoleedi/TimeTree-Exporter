"""
This module login in to TimeTree and converts Timetree events to iCal format.
"""

import logging

from timetree_exporter.api.auth import login
from timetree_exporter.api.calendar import TimeTreeCalendar
from timetree_exporter.cli import (
    configure_logging,
    list_labels_and_exit,
    parse_args,
    raw_output_dir,
    resolve_email,
    resolve_password,
)
from timetree_exporter.exporter import Exporter

logger = logging.getLogger(__name__)


def select_calendar(
    email: str,
    password: str,
    calendar_code: str,
    capture_raw_responses: bool = False,
):
    """Authenticate and select a calendar. Returns (calendar_api, calendar_id, calendar_name)."""
    use_code = bool(calendar_code)
    session_id = login(email, password)
    calendar = TimeTreeCalendar(session_id, capture_raw_responses=capture_raw_responses)
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


def main():
    """Main function for the Timetree Exporter."""
    args = parse_args()
    configure_logging(args.verbose)
    raw_dir = raw_output_dir(args)

    email = resolve_email(args.email)
    password = resolve_password()
    calendar_api, calendar_id, calendar_name = select_calendar(
        email,
        password,
        args.calendar_code,
        capture_raw_responses=raw_dir is not None,
    )

    if args.list_labels:
        list_labels_and_exit(calendar_api, calendar_id)
        if raw_dir:
            written = calendar_api.write_raw_responses(raw_dir)
            logger.info("Wrote %d raw TimeTree response(s) to %s", len(written), raw_dir)
        return

    exporter = Exporter(
        calendar_api,
        calendar_id,
        calendar_name,
        args.output,
        split_by_label=args.split_by_label,
    )
    exporter.export()

    if raw_dir:
        written = calendar_api.write_raw_responses(raw_dir)
        logger.info("Wrote %d raw TimeTree response(s) to %s", len(written), raw_dir)


if __name__ == "__main__":
    main()
