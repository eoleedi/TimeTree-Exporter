"""Tests for the event module."""

from timetree_exporter.event import (
    TimeTreeEvent,
    TimeTreeEventCategory,
    TimeTreeEventType,
    TimeTreePublicEvent,
)


def test_event_creation(normal_event_data):
    """Test creating a TimeTreeEvent."""
    event = TimeTreeEvent(
        uuid=normal_event_data["uuid"],
        title=normal_event_data["title"],
        created_at=normal_event_data["created_at"],
        updated_at=normal_event_data["updated_at"],
        note=normal_event_data["note"],
        location=normal_event_data["location"],
        location_lat=normal_event_data["location_lat"],
        location_lon=normal_event_data["location_lon"],
        url=normal_event_data["url"],
        start_at=normal_event_data["start_at"],
        start_timezone=normal_event_data["start_timezone"],
        end_at=normal_event_data["end_at"],
        end_timezone=normal_event_data["end_timezone"],
        all_day=normal_event_data["all_day"],
        alerts=normal_event_data["alerts"],
        recurrences=normal_event_data["recurrences"],
        parent_id=normal_event_data["parent_id"],
        recurring_uuid=normal_event_data["recurring_uuid"],
        event_type=normal_event_data["type"],
        category=normal_event_data["category"],
    )

    assert event.uuid == normal_event_data["uuid"]
    assert event.title == normal_event_data["title"]
    assert event.created_at == normal_event_data["created_at"]
    assert event.updated_at == normal_event_data["updated_at"]
    assert event.note == normal_event_data["note"]
    assert event.location == normal_event_data["location"]
    assert event.location_lat == normal_event_data["location_lat"]
    assert event.location_lon == normal_event_data["location_lon"]
    assert event.url == normal_event_data["url"]
    assert event.start_at == normal_event_data["start_at"]
    assert event.start_timezone == normal_event_data["start_timezone"]
    assert event.end_at == normal_event_data["end_at"]
    assert event.end_timezone == normal_event_data["end_timezone"]
    assert event.all_day == normal_event_data["all_day"]
    assert event.alerts == normal_event_data["alerts"]
    assert event.recurrences == normal_event_data["recurrences"]
    assert event.parent_id == normal_event_data["parent_id"]
    assert event.recurring_uuid == normal_event_data["recurring_uuid"]
    assert event.event_type == normal_event_data["type"]
    assert event.category == normal_event_data["category"]


def test_from_dict(normal_event_data):
    """Test creating a TimeTreeEvent from a dictionary."""
    event = TimeTreeEvent.from_dict(normal_event_data)

    assert event.uuid == normal_event_data["uuid"]
    assert event.title == normal_event_data["title"]
    assert event.created_at == normal_event_data["created_at"]
    assert event.updated_at == normal_event_data["updated_at"]
    assert event.note == normal_event_data["note"]
    assert event.location == normal_event_data["location"]
    assert event.location_lat == normal_event_data["location_lat"]
    assert event.location_lon == normal_event_data["location_lon"]
    assert event.url == normal_event_data["url"]
    assert event.start_at == normal_event_data["start_at"]
    assert event.start_timezone == normal_event_data["start_timezone"]
    assert event.end_at == normal_event_data["end_at"]
    assert event.end_timezone == normal_event_data["end_timezone"]
    assert event.all_day == normal_event_data["all_day"]
    assert event.alerts == normal_event_data["alerts"]
    assert event.recurrences == normal_event_data["recurrences"]
    assert event.parent_id == normal_event_data["parent_id"]
    assert event.recurring_uuid == normal_event_data["recurring_uuid"]
    assert event.event_type == normal_event_data["type"]
    assert event.category == normal_event_data["category"]


def test_from_dict_with_comments(normal_event_data):
    """Test creating a TimeTreeEvent with activity comments."""
    data = normal_event_data.copy()
    data["comments"] = ["First comment", "Second comment"]

    event = TimeTreeEvent.from_dict(data)

    assert event.comments == ["First comment", "Second comment"]


def test_str_representation(normal_event_data):
    """Test the string representation of a TimeTreeEvent."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    assert str(event) == normal_event_data["title"]


def test_event_types():
    """Test the TimeTreeEventType enumeration."""
    assert TimeTreeEventType.NORMAL == 0
    assert TimeTreeEventType.BIRTHDAY == 1


def test_event_categories():
    """Test the TimeTreeEventCategory enumeration."""
    assert TimeTreeEventCategory.NORMAL == 1
    assert TimeTreeEventCategory.MEMO == 2


def test_from_dict_with_label_id(labeled_event_data):
    """Test creating a TimeTreeEvent with a direct label_id."""
    event = TimeTreeEvent.from_dict(labeled_event_data)
    assert event.label_id == 3


def test_from_dict_with_relationship_label(relationship_label_event_data):
    """Test creating a TimeTreeEvent with label in relationships format."""
    event = TimeTreeEvent.from_dict(relationship_label_event_data)
    assert event.label_id == 7


def test_from_dict_without_label(normal_event_data):
    """Test that label_id is None when no label data is present."""
    event = TimeTreeEvent.from_dict(normal_event_data)
    assert event.label_id is None


def test_public_event_from_dict_maps_public_api_fields(normal_event_data):
    """Public calendar events should normalize API v2 fields to TimeTreeEvent fields."""
    public_event_data = normal_event_data.copy()
    public_event_data.pop("uuid")
    public_event_data.pop("type")
    public_event_data.pop("category")
    public_event_data.pop("location")
    public_event_data["id"] = "public-event-id"
    public_event_data["location_name"] = "Public Venue"
    public_event_data["location_address"] = "1 Public Street"
    public_event_data["headline"] = "Public headline"
    public_event_data["overview"] = "Public overview"
    public_event_data["url"] = "https://timetr.ee/p/public-event-id"
    public_event_data["link_url"] = "https://example.com/campaign"
    public_event_data["location_url"] = "https://example.com/location"
    public_event_data["attachment"] = {
        "ogp": {
            "title": "OGP title",
            "description": "OGP description",
            "url": "https://example.com/ogp",
        }
    }
    public_event_data["images"] = {
        "cover": [
            {
                "url": "https://example.com/image.jpg",
                "thumbnail_url": "https://example.com/thumb.jpg",
            }
        ]
    }
    public_event_data["videos"] = [{"url": "https://example.com/video.mp4"}]
    public_event_data["public_calendar_hashtags"] = [
        {"name": "Shopping"},
        {"hashtag": "Sale"},
        "Rakuten",
    ]
    public_event_data["public_calendar_label"] = {
        "label_id": 9,
        "name": "Campaign",
    }
    public_event_data["color"] = 9732216

    event = TimeTreePublicEvent.from_dict(public_event_data)

    assert event.uuid == "public-event-id"
    assert event.location == "Public Venue 1 Public Street"
    assert event.event_type == TimeTreeEventType.NORMAL
    assert event.category == TimeTreeEventCategory.NORMAL
    assert event.label_id == 9
    assert event.label_name == "Campaign"
    assert event.label_color == "#948078"
    assert event.category_names == ["Shopping", "Sale", "Rakuten"]
    assert event.url == "https://example.com/campaign"
    assert event.source_url == "https://timetr.ee/p/public-event-id"
    assert event.link_url == "https://example.com/campaign"
    assert event.location_url == "https://example.com/location"
    assert event.image_urls == ["https://example.com/image.jpg"]
    assert event.thumbnail_image_urls == ["https://example.com/thumb.jpg"]
    assert event.video_urls == ["https://example.com/video.mp4"]
    assert "Public headline" not in event.note
    assert "Public overview" not in event.note
    assert "OGP title" not in event.note
    assert "OGP description" not in event.note
    assert "https://example.com/ogp" not in event.note
    assert "https://timetr.ee/p/public-event-id" not in event.note
    assert "https://example.com/image.jpg" not in event.note
    assert "https://example.com/location" not in event.note


def test_public_event_from_dict_preserves_zero_label_values(normal_event_data):
    """Public event parsing should treat zero color and label id as real values."""
    public_event_data = normal_event_data.copy()
    public_event_data.pop("uuid")
    public_event_data["id"] = "public-event-id"
    public_event_data["color"] = 9732216
    public_event_data["public_calendar_label"] = {
        "label_id": 0,
        "name": "Black",
        "color": 0,
    }

    event = TimeTreePublicEvent.from_dict(public_event_data)

    assert event.label_id == 0
    assert event.label_color == "#000000"
