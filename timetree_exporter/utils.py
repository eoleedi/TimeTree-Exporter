"""Utility functions for Timetree Exporter"""

import json
import os


def get_events_from_file(file_path) -> list:
    """Fetch events from Timetree response file"""
    try:
        with open(file_path, "r", encoding="UTF-8") as response_file:
            response_data = json.load(response_file)
            return response_data["events"]
    except FileNotFoundError:
        print(f"File not found: {file_path}")
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
            print(f"Invalid path: {path}")
    return filenames
