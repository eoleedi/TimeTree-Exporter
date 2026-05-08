"""Build and write iCalendar exports from TimeTree events."""

import logging
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path

from icalendar import Calendar

from timetree_exporter import ICalEventFormatter, TimeTreeEvent
from timetree_exporter.cli import sanitize_filename
from timetree_exporter.utils import add_bounded_timezones_before_events

logger = logging.getLogger(__name__)


def create_calendar():
    """Create a new iCalendar object with standard properties."""
    cal = Calendar()
    cal.add("prodid", f"-//TimeTree Exporter {version('timetree_exporter')}//EN")
    cal.add("version", "2.0")
    return cal


def write_calendar(cal, output_path: str):
    """Write a calendar to an .ics file."""
    add_bounded_timezones_before_events(cal)

    path = Path(output_path)
    with path.open("wb") as f:
        f.write(cal.to_ical())
        logger.info("The .ics calendar file is saved to %s", path.resolve())


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
