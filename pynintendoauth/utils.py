"""Nintendo auth utils."""

import logging
import base64
import hashlib
import random
import string

from urllib.parse import urlparse

_LOGGER = logging.getLogger(__name__)


def parse_response_token(token: str) -> dict:
    """Parses a response token."""
    _LOGGER.debug(">> Parsing response token.")
    try:
        url = urlparse(token)
        params = url.fragment.split("&")
        response = {}
        for param in params:
            response = {**response, param.split("=")[0]: param.split("=")[1]}
        return response
    except Exception as exc:
        raise ValueError("Invalid token provided.") from exc


def calc_hash(text: str):
    """Hash given text for login."""
    text = hashlib.sha256(text.encode()).digest()
    text = base64.urlsafe_b64encode(text).decode()
    return text.replace("=", "")


def gen_rand():
    """Generate random string."""
    return "".join(random.choice(string.ascii_letters) for _ in range(50))
