"""TimeTree calendar domain object."""

from dataclasses import dataclass
from typing import Protocol


class CalendarApi(Protocol):
    """API methods needed by a selected calendar."""

    def get_events(
        self,
        calendar_id,
        calendar_name,
        calendar_users=None,
        include_comments=False,
        num_workers=10,
    ):
        """Return events for a calendar."""

    def get_public_events(self, calendar_id, calendar_name):
        """Return events for a public calendar."""

    def get_public_labels(self, calendar_id):
        """Return labels for a public calendar."""

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
        return self.metadata.get("alias_code")

    @property
    def is_public(self):
        """Return whether this calendar should use the public calendar API."""
        return self.metadata.get("public", False)

    def get_events(self, include_comments=False, num_workers=10):
        """Return events for this calendar."""
        if self.is_public:
            return self.api.get_public_events(self.id, self.name)
        return self.api.get_events(
            self.id,
            self.name,
            self.metadata.get("calendar_users"),
            include_comments=include_comments,
            num_workers=num_workers,
        )

    def get_labels(self):
        """Return labels for this calendar."""
        if self.is_public:
            return self.api.get_public_labels(self.id)
        return self.api.get_labels(self.id)
