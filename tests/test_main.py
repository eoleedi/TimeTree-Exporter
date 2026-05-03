"""Tests for CLI entry helpers in __main__."""

from timetree_exporter.__main__ import label_suffix_for_group, list_labels_and_exit


class _FakeCalendarApi:
    def get_labels(self, _calendar_id):
        return {
            "1": {"name": "Valid", "color": "#ff00aa"},
            "2": {"name": "Empty", "color": ""},
            "3": {"name": "Malformed", "color": "#zzzzzz"},
        }


def test_list_labels_and_exit_handles_invalid_or_missing_color(capsys):
    """Listing labels should not fail when color is empty or malformed."""
    list_labels_and_exit(_FakeCalendarApi(), "dummy-calendar-id")

    output = capsys.readouterr().out

    assert "Valid" in output
    assert "Empty" in output
    assert "Malformed" in output
    assert "\033[38;2;255;0;170m●\033[0m" in output


def test_label_suffix_for_group_uses_label_id_when_name_is_empty():
    """Unnamed color-only labels should still produce unique output filenames."""
    labels = {3: {"name": "", "color": "#ff00aa"}}

    assert label_suffix_for_group(3, labels) == "label_3"


def test_label_suffix_for_group_sanitizes_label_name():
    """Named labels should keep their name while remaining filename safe."""
    labels = {3: {"name": "Work / Home", "color": "#ff00aa"}}

    assert label_suffix_for_group(3, labels) == "Work___Home"
