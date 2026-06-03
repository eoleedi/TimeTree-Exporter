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
    recurring_uuid: str
    event_type: int
    category: int
    label_id: int = None
    comments: list = None

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
            recurring_uuid=event_data.get("recurring_uuid"),
            event_type=event_data.get("type"),
            category=event_data.get("category"),
            label_id=cls._extract_label_id(event_data),
            comments=event_data.get("comments"),
        )

    def __str__(self):
        return self.title


@dataclass
class TimeTreePublicEvent(TimeTreeEvent):
    """TimeTree public calendar event from the API v2 public_events response."""

    headline: str = None
    overview: str = None
    link_url: str = None
    location_address: str = None
    location_url: str = None
    location_note: str = None
    label_name: str = None
    label_color: str = None
    category_names: list = None
    image_urls: list = None
    thumbnail_image_urls: list = None
    video_urls: list = None
    until_at: int = None
    source_url: str = None

    @staticmethod
    def _extract_cover_image_urls(event_data):
        """Return public event cover image URLs."""
        return [
            image["url"]
            for image in event_data.get("images", {}).get("cover", [])
            if image.get("url")
        ]

    @staticmethod
    def _extract_thumbnail_image_urls(event_data):
        """Return public event thumbnail image URLs."""
        return [
            image["thumbnail_url"]
            for image in event_data.get("images", {}).get("cover", [])
            if image.get("thumbnail_url")
        ]

    @staticmethod
    def _extract_video_urls(event_data):
        """Return public event video URLs."""
        return [video["url"] for video in event_data.get("videos", []) if video.get("url")]

    @staticmethod
    def _build_note(event_data):
        """Build an ICS description from public event text and links."""
        parts = []
        for value in (event_data.get("note"),):
            if value:
                parts.append(value)

        video_urls = TimeTreePublicEvent._extract_video_urls(event_data)
        if video_urls:
            parts.append("Videos:\n" + "\n".join(video_urls))

        return "\n\n".join(parts)

    @staticmethod
    def _build_location(event_data):
        """Build a display location from public event location fields."""
        return " ".join(
            value
            for value in (event_data.get("location_name"), event_data.get("location_address"))
            if value
        )

    @staticmethod
    def _extract_category_names(event_data):
        """Return public hashtag/category names."""
        names = []
        for hashtag in event_data.get("public_calendar_hashtags", []):
            if isinstance(hashtag, str):
                names.append(hashtag)
            elif isinstance(hashtag, dict):
                name = hashtag.get("name") or hashtag.get("hashtag") or hashtag.get("title")
                if name:
                    names.append(name)
        return names

    @classmethod
    def from_dict(cls, event_data: dict):
        """Create TimeTreePublicEvent object from public calendar JSON data."""
        label = event_data.get("public_calendar_label") or {}
        color = label.get("color")
        if color is None:
            color = event_data.get("color")
        label_color = cls._format_color(color)
        label_id = label.get("label_id")
        if label_id is None:
            label_id = cls._extract_label_id(event_data)
        image_urls = cls._extract_cover_image_urls(event_data)
        thumbnail_image_urls = cls._extract_thumbnail_image_urls(event_data)
        video_urls = cls._extract_video_urls(event_data)
        category_names = cls._extract_category_names(event_data)
        return cls(
            uuid=event_data.get("uuid") or event_data.get("id"),
            title=event_data.get("title"),
            created_at=event_data.get("created_at"),
            updated_at=event_data.get("updated_at"),
            note=cls._build_note(event_data),
            location=event_data.get("location") or cls._build_location(event_data),
            location_lat=event_data.get("location_lat"),
            location_lon=event_data.get("location_lon"),
            url=event_data.get("link_url"),
            start_at=event_data.get("start_at"),
            start_timezone=event_data.get("start_timezone"),
            end_at=event_data.get("end_at"),
            end_timezone=event_data.get("end_timezone"),
            all_day=event_data.get("all_day"),
            alerts=event_data.get("alerts"),
            recurrences=event_data.get("recurrences"),
            parent_id=event_data.get("parent_id"),
            recurring_uuid=event_data.get("recurring_uuid"),
            event_type=event_data.get("type", TimeTreeEventType.NORMAL),
            category=event_data.get("category", TimeTreeEventCategory.NORMAL),
            label_id=label_id,
            headline=event_data.get("headline"),
            overview=event_data.get("overview"),
            link_url=event_data.get("link_url"),
            location_address=event_data.get("location_address"),
            location_url=event_data.get("location_url"),
            location_note=event_data.get("location_note"),
            label_name=label.get("name"),
            label_color=label_color,
            category_names=category_names,
            image_urls=image_urls,
            thumbnail_image_urls=thumbnail_image_urls,
            video_urls=video_urls,
            until_at=event_data.get("until_at"),
            source_url=event_data.get("url"),
        )

    @staticmethod
    def _format_color(color):
        """Convert public label color to an ICS-compatible hex string."""
        if isinstance(color, int):
            return f"#{color:06x}"
        return color


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
