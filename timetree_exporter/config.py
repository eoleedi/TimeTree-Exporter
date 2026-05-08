"""Runtime configuration shared across timetree_exporter modules."""

import os

DEVELOPER_MODE_ENV = "TIMETREE_EXPORTER_DEVELOPER"
RAW_OUTPUT_DIR = "raw-timetree"

_developer_mode = False
_raw_output_dir = None


def configure_developer_mode(enabled=False, raw_output_dir=None):
    """Configure developer diagnostics for the current process."""
    global _developer_mode, _raw_output_dir
    _developer_mode = enabled
    _raw_output_dir = raw_output_dir


def is_developer_mode():
    """Return whether developer diagnostics are enabled."""
    return _developer_mode or os.environ.get(DEVELOPER_MODE_ENV) == "1"


def resolve_raw_output_dir(developer_mode=False, raw_output_dir=None):
    """Return a raw response output directory for explicit settings."""
    if raw_output_dir:
        return raw_output_dir
    if developer_mode or os.environ.get(DEVELOPER_MODE_ENV) == "1":
        return RAW_OUTPUT_DIR
    return None


def get_raw_output_dir():
    """Return the configured raw API response output directory, if enabled."""
    return resolve_raw_output_dir(_developer_mode, _raw_output_dir)
