"""Utility functions for Timetree Exporter"""

import json
import os
import logging
import inspect
import getpass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)


def get_events_from_file(file_path) -> list:
    """Fetch events from Timetree response file"""
    try:
        with open(file_path, "r", encoding="UTF-8") as response_file:
            response_data = json.load(response_file)
            if "events" in response_data:
                return response_data["events"]
            if "public_events" in response_data:  # Partal support for public events
                return response_data["public_events"]
            logger.error(
                "Invalid response file: %s. \n No 'events' or 'public_events' column in the file",
                file_path,
            )
            return None
    except FileNotFoundError:
        logger.error("File not found: %s", file_path)
        return None


def paths_to_filelist(paths: list) -> list:
    """Converts a list of paths to a list of files"""
    filenames = []
    for path in paths:
        if os.path.isdir(path):
            filenames += [os.path.join(path, file) for file in os.listdir(path)]
        elif os.path.isfile(path):
            filenames.append(path)
        else:
            logger.error("Invalid path: %s", path)
    return filenames


def convert_timestamp_to_datetime(timestamp, tzinfo=ZoneInfo("UTC")):
    """
    Convert timestamp to datetime for both positive and negative timestamps on different platforms.
    """
    if timestamp >= 0:
        return datetime.fromtimestamp(timestamp, tzinfo)
    return datetime.fromtimestamp(0, tzinfo) + timedelta(seconds=int(timestamp))


def safe_getpass(prompt="Password: ", echo_char=None):
    """Safely get a password from the user, supporting echo_char for Python 3.14+.
    If echo_char is not supported, it falls back to the pwinput module if echo_char is needed.
    """
    sig = inspect.signature(getpass.getpass)
    if "echo_char" in sig.parameters:
        # Python 3.14+ supports echo_char
        return getpass.getpass(  # pylint: disable=E1123
            prompt=prompt, echo_char=echo_char
        )
    if echo_char is not None:
        # Use pwinput for echo_char support in older versions
        try:
            from pwinput import pwinput  # pylint: disable=C0415

            return pwinput(prompt=prompt, mask=echo_char)
        except ImportError as exc:
            logger.error("pwinput module is required for echo_char support.")
            raise ImportError(
                "Please install pwinput to use echo_char functionality."
            ) from exc
    else:
        # Fallback for older versions
        return getpass.getpass(prompt=prompt)
