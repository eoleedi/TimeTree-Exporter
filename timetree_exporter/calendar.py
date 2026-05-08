"""TimeTree calendar domain object."""

from dataclasses import dataclass
from typing import Protocol


class CalendarApi(Protocol):
    """API methods needed by a selected calendar."""

    def get_events(self, calendar_id, calendar_name):
        """Return events for a calendar."""

    def get_labels(self, calendar_id):
        """Return labels for a calendar."""


@dataclass(frozen=True)
class Calendar:
    """TimeTree calendar Object."""

    api: CalendarApi
    metadata: dict

    @property
    def id(self):
        """Return the calendar id."""
        return self.metadata["id"]

    @property
    def name(self):
        """Return the calendar name."""
        return self.metadata["name"]

    @property
    def alias_code(self):
        """Return the calendar alias code."""
        return self.metadata["alias_code"]

    def get_events(self):
        """Return events for this calendar."""
        return self.api.get_events(self.id, self.name)

    def get_labels(self):
        """Return labels for this calendar."""
        return self.api.get_labels(self.id)
