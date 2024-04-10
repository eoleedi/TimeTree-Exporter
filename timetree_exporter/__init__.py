"""Init file for timetree_exporter package."""

import logging
from timetree_exporter.event import TimeTreeEvent
from timetree_exporter.formatter import ICalEventFormatter

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s ",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
