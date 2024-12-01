"""
This module contains the User class, which is responsible for handling user-related operations.
"""

import uuid
import logging
from typing import Union
import requests
from timetree_exporter.api.const import API_BASEURI, API_USER_AGENT

logger = logging.getLogger(__name__)


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
        raise AuthenticationError("Login failed")

    try:
        session_id = response.cookies["_session_id"]
        return session_id
    except KeyError:
        return None


class AuthenticationError(Exception):
    """
    Exception raised when the user is not authorized to access the resource.
    """
