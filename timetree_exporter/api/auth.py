"""
This module contains the User class, which is responsible for handling user-related operations.
"""

import logging
import uuid
from typing import Union

import requests

from timetree_exporter.api.const import API_BASEURI, API_USER_AGENT

logger = logging.getLogger(__name__)


def _extract_error_code(response: requests.Response) -> Union[int, None]:
    """Extract API error code from a login response body."""
    try:
        body = response.json()
    except ValueError:
        return None

    error = body.get("error")

    return error.get("code") if isinstance(error, dict) else None


def login(email, password) -> Union[str, None]:
    """
    Log in to the TimeTree app and return the session ID.
    """
    url = f"{API_BASEURI}/auth/email/signin"
    payload = {
        "uid": email,
        "password": password,
        "uuid": str(uuid.uuid4()).replace("-", ""),
    }
    headers = {
        "Content-Type": "application/json",
        "X-Timetreea": API_USER_AGENT,
    }

    response = requests.put(url, json=payload, headers=headers, timeout=10)

    if response.status_code != 200:
        logger.error("Login failed: %s", response.text)
        error_code = _extract_error_code(response)
        if error_code == -702:
            raise InvalidCredentialsError("Wrong email or password")
        if error_code == -495:
            raise RateLimitAuthenticationError("Rate limited, please try again later")
        raise AuthenticationError("Login failed")

    try:
        return response.cookies["_session_id"]
    except KeyError:
        return None


class AuthenticationError(Exception):
    """
    Exception raised when the user is not authorized to access the resource.
    """


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when email or password is invalid."""


class RateLimitAuthenticationError(AuthenticationError):
    """Exception raised when login is rate-limited by API."""
