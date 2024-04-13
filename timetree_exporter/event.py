"""This module provides the TimeTreeEvent class for representing TimeTree events."""

import dataclasses


class TimeTreeEvent:
    """TimeTree event class"""

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        uuid: str,
        title: str,
        created_at: int,
        updated_at: int,
        recurrences: list,
        alerts: list,
        url: str,
        note: str,
        start_at: int,
        end_at: int,
        all_day: bool,
        start_timezone: str,
        end_timezone: str,
        location_lat: str,
        location_lon: str,
        location: str,
        parent_id: str,
        event_type: int,
        category: int,
    ):
        # pylint: disable=too-many-arguments
        # pylint: disable=too-many-locals
        self.uuid = uuid
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.note = note
        self.location = location
        self.location_lat = location_lat
        self.location_lon = location_lon
        self.url = url
        self.start_at = start_at
        self.start_timezone = start_timezone
        self.end_at = end_at
        self.end_timezone = end_timezone
        self.all_day = all_day
        self.alerts = alerts
        self.recurrences = recurrences
        self.parent_id = parent_id
        self.event_type = event_type
        self.category =  category

    @classmethod
    def from_dict(cls, event_data: dict):
        """Create TimeTreeEvent object from JSON data"""
        return cls(
            uuid=event_data.get("uuid"),
            title=event_data.get("title"),
            created_at=event_data.get("created_at"),
            updated_at=event_data.get("updated_at"),
            note=event_data.get("note"),
            location=event_data.get("location"),
            location_lat=event_data.get("location_lat"),
            location_lon=event_data.get("location_lon"),
            url=event_data.get("url"),
            start_at=event_data.get("start_at"),
            start_timezone=event_data.get("start_timezone"),
            end_at=event_data.get("end_at"),
            end_timezone=event_data.get("end_timezone"),
            all_day=event_data.get("all_day"),
            alerts=event_data.get("alerts"),
            recurrences=event_data.get("recurrences"),
            parent_id=event_data.get("parent_id"),
            event_type=event_data.get("type"),
            category=event_data.get("category"),
        )

    def __str__(self):
        return self.title


@dataclasses.dataclass
class TimeTreeEventType(enumerate):
    """TimeTree event type enumeration"""

    NORMAL = 0
    BIRTHDAY = 1


@dataclasses.dataclass
class TimeTreeEventCategory(enumerate):
    """TimeTree event category enumeration"""

    NORMAL = 1
    MEMO = 2
