"""Init file for timetree_exporter package."""

import logging
from importlib.metadata import PackageNotFoundError, version

from timetree_exporter.event import TimeTreeEvent as TimeTreeEvent
from timetree_exporter.formatter import ICalEventFormatter as ICalEventFormatter

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

try:
    __version__ = version("timetree_exporter")
except PackageNotFoundError:
    __version__ = "unknown"
