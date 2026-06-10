"""Build and write iCalendar exports from TimeTree events."""

import logging
import re
from collections import defaultdict
from importlib.metadata import version
from pathlib import Path

from icalendar import Calendar as ICalendar

from timetree_exporter import ICalEventFormatter, TimeTreeEvent, TimeTreePublicEvent
from timetree_exporter.utils import add_bounded_timezones_before_events

logger = logging.getLogger(__name__)


class Exporter:
    """Export a selected TimeTree calendar to one or more iCalendar files."""

    def __init__(
        self, calendar, output, split_by_label=False, include_comments=False, num_workers=10
    ):
        self.calendar = calendar
        self.output = output
        self.split_by_label = split_by_label
        self.include_comments = include_comments
        self.num_workers = num_workers

    def export(self):
        """Fetch labels and events, then write the configured iCalendar output."""
        events = self.calendar.get_events(
            include_comments=self.include_comments, num_workers=self.num_workers
        )
        logger.info("Found %d events", len(events))

        labels = self.calendar.get_labels()
        if self.calendar.is_public and not labels:
            labels = public_labels_from_events(events)
        logger.info("Found %d labels", len(labels))

        event_cls = TimeTreePublicEvent if self.calendar.is_public else TimeTreeEvent

        if self.split_by_label:
            grouped_events = group_events_by_label(events, labels, event_cls=event_cls)
            write_split_calendars(grouped_events, labels, self.output, len(events))
            return

        cal = build_single_calendar(events, labels, event_cls=event_cls)
        logger.info(
            "A total of %d/%d events are added to the calendar",
            len(cal.subcomponents),
            len(events),
        )
        write_calendar(cal, self.output)


def create_calendar():
    """Create a new iCalendar object with standard properties."""
    cal = ICalendar()
    cal.add("prodid", f"-//TimeTree Exporter {version('timetree_exporter')}//EN")
    cal.add("version", "2.0")
    return cal


def sanitize_filename(name):
    """Sanitize a string for use as an export filename component."""
    return re.sub(r"[^\w\-]", "_", name).strip("_")


def write_calendar(cal, output_path: str | Path):
    """Write a calendar to an .ics file."""
    add_bounded_timezones_before_events(cal)

    path = Path(output_path)
    with path.open("wb") as f:
        f.write(cal.to_ical())
        logger.info("The .ics calendar file is saved to %s", path.resolve())


def public_labels_from_events(events):
    """Build label metadata from public calendar event payloads."""
    labels = {}
    for event in events:
        label = event.get("public_calendar_label") or {}
        label_id = label.get("label_id")
        if label_id is None:
            continue
        color = label.get("color")
        if color is None:
            color = event.get("color", "")
        labels[label_id] = {
            "name": str(label.get("name") or ""),
            "color": f"#{color:06x}" if isinstance(color, int) else color,
        }
    return labels


def build_single_calendar(events, labels, event_cls=TimeTreeEvent):
    """Build single output calendar from events."""
    cal = create_calendar()
    label_lookup = {lid: info["name"] for lid, info in labels.items()} if labels else {}
    color_lookup = {lid: info["color"] for lid, info in labels.items()} if labels else {}

    for event in events:
        time_tree_event = event_cls.from_dict(event)
        label_name = label_lookup.get(time_tree_event.label_id) or getattr(
            time_tree_event, "label_name", None
        )
        color = color_lookup.get(time_tree_event.label_id) or getattr(
            time_tree_event, "label_color", None
        )
        formatter = ICalEventFormatter(
            time_tree_event,
            label_name=label_name,
            color=color,
            category_names=getattr(time_tree_event, "category_names", None),
        )
        ical_event = formatter.to_ical()
        if ical_event is not None:
            cal.add_component(ical_event)

    return cal


def group_events_by_label(events, labels, event_cls=TimeTreeEvent):
    """Group converted iCal events by label id (or None for unlabeled)."""
    grouped = defaultdict(list)

    for event in events:
        time_tree_event = event_cls.from_dict(event)
        label_info = labels.get(time_tree_event.label_id)
        if label_info is not None:
            label_name = label_info["name"]
            color = label_info["color"]
        else:
            label_name = getattr(time_tree_event, "label_name", None)
            color = getattr(time_tree_event, "label_color", None)
        formatter = ICalEventFormatter(
            time_tree_event,
            label_name=label_name,
            color=color,
            category_names=getattr(time_tree_event, "category_names", None),
        )
        ical_event = formatter.to_ical()

        if ical_event is None:
            continue

        group_key = time_tree_event.label_id if label_name or color else None
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
