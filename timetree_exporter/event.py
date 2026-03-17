"""This module provides the TimeTreeEvent class for representing TimeTree events."""

from dataclasses import dataclass


@dataclass
class TimeTreeEvent:
    """TimeTree event class"""

    # pylint: disable=too-many-instance-attributes

    uuid: str
    title: str
    created_at: int
    updated_at: int
    recurrences: list
    alerts: list
    url: str
    note: str
    start_at: int
    end_at: int
    all_day: bool
    start_timezone: str
    end_timezone: str
    location_lat: str
    location_lon: str
    location: str
    parent_id: str
    event_type: int
    category: int
    label_id: int = None

    @staticmethod
    def _extract_label_id(event_data: dict):
        """Extract label_id from event data, trying multiple formats."""
        # Try direct `label_id` key
        label_id = event_data.get("label_id")
        if label_id is not None:
            return label_id

        # Try JSON:API relationships format
        try:
            rel_id = event_data["relationships"]["label"]["data"]["id"]
            # Format may be "calendar_id,label_number" — extract the label number
            if isinstance(rel_id, str) and "," in rel_id:
                return int(rel_id.split(",")[-1])
            return int(rel_id)
        except (KeyError, TypeError, ValueError):
            pass

        return None

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
            label_id=cls._extract_label_id(event_data),
        )

    def __str__(self):
        return self.title


@dataclass
class TimeTreeEventType(enumerate):
    """TimeTree event type enumeration"""

    NORMAL = 0
    BIRTHDAY = 1


@dataclass
class TimeTreeEventCategory(enumerate):
    """TimeTree event category enumeration"""

    NORMAL = 1
    MEMO = 2
