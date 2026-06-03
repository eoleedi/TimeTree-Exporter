"""CLI helpers for timetree_exporter."""

import argparse
import logging
import os
import re
from pathlib import Path

from timetree_exporter import __version__
from timetree_exporter.config import (
    DEVELOPER_MODE_ENV,
    RAW_OUTPUT_DIR,
    resolve_raw_output_dir,
)
from timetree_exporter.utils import safe_getpass

package_logger = logging.getLogger(__package__)

__all__ = [
    "DEVELOPER_MODE_ENV",
    "RAW_OUTPUT_DIR",
    "configure_logging",
    "list_labels_and_exit",
    "parse_args",
    "raw_output_dir",
    "resolve_email",
    "resolve_password",
]


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Convert Timetree events to iCal format",
        prog="timetree_exporter",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output iCal file",
        default=str(Path.cwd() / "timetree.ics"),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--email",
        type=str,
        help="Email address",
        default=None,
    )
    parser.add_argument(
        "-c",
        "--calendar_code",
        type=str,
        help="The Calendar Code you want to export, or public calendar id with --public-calendar",
        default=None,
    )
    parser.add_argument(
        "--public-calendar",
        help="Export a public calendar by id without signing in",
        action="store_true",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--list-labels",
        help="List labels for the selected calendar and exit",
        action="store_true",
    )
    parser.add_argument(
        "--split-by-label",
        help="Export events into separate .ics files grouped by label",
        action="store_true",
    )
    parser.add_argument(
        "--include-comments",
        help=(
            "Export private event comments. This makes one or more extra TimeTree requests "
            "per event and may take much longer or trigger rate limits."
        ),
        action="store_true",
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        help="Number of concurrent threads for fetching comments (default: 10)",
        default=10,
    )
    parser.add_argument(
        "--developer-mode",
        help=(
            "Enable developer diagnostics, including raw TimeTree API response output "
            f"(or set {DEVELOPER_MODE_ENV}=1)"
        ),
        action="store_true",
    )
    parser.add_argument(
        "--raw-output-dir",
        type=str,
        help="Directory for developer-mode raw TimeTree API JSON responses",
        default=None,
    )
    return parser.parse_args()


def resolve_email(cli_email):
    """Resolve email from CLI arg, env var, or prompt."""
    if cli_email:
        return cli_email
    env_email = os.environ.get("TIMETREE_EMAIL")
    if env_email:
        return env_email
    return input("Enter your email address: ")


def resolve_password():
    """Resolve password from env var or prompt."""
    env_password = os.environ.get("TIMETREE_PASSWORD")
    if env_password:
        return env_password
    return safe_getpass(prompt="Enter your password: ", echo_char="*")


def configure_logging(verbose):
    """Configure package logging level based on CLI flags."""
    if verbose:
        package_logger.setLevel(logging.DEBUG)


def raw_output_dir(args):
    """Return the raw response output directory for parsed CLI args."""
    return resolve_raw_output_dir(args.developer_mode, args.raw_output_dir)


def list_labels_and_exit(calendar):
    """Print labels for a calendar and return."""
    labels = calendar.get_labels()
    if not labels:
        print("No labels found (the API response format may differ — use -v to debug)")
        return

    for i, (_label_id, label_info) in enumerate(labels.items(), 1):
        color_hex = (label_info.get("color") or "").strip()
        normalized = color_hex.lstrip("#")

        if len(normalized) == 6 and re.fullmatch(r"[0-9A-Fa-f]{6}", normalized):
            r = int(normalized[0:2], 16)
            g = int(normalized[2:4], 16)
            b = int(normalized[4:6], 16)
            dot = f"\033[38;2;{r};{g};{b}m●\033[0m"
        else:
            dot = "●"

        print(f"{i:>2}. {dot} {label_info['name']}")
