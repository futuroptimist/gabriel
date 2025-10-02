"""Secret management helpers with optional keyring integration."""

from __future__ import annotations

import getpass
import os
import re
import sys
from typing import Final

SECRET_ENV_PREFIX: Final[str] = "GABRIEL_SECRET_"


def _env_secret_key(service: str, username: str) -> str:
    """Return a normalized environment variable key for ``service`` and ``username``."""

    raw = f"{service}_{username}"
    sanitized = re.sub(r"\W", "_", raw)
    if sanitized.strip("_"):
        sanitized = sanitized.lstrip("_")
    else:
        sanitized = "IDENTIFIER"
    safe = sanitized.upper()
    return f"{SECRET_ENV_PREFIX}{safe}"


def store_secret(service: str, username: str, secret: str) -> None:
    """Store ``secret`` using ``keyring`` or environment variables."""

    try:
        import keyring
    except ImportError:  # pragma: no cover - exercised via tests
        os.environ[_env_secret_key(service, username)] = secret
    else:
        keyring.set_password(service, username, secret)


def get_secret(service: str, username: str) -> str | None:
    """Retrieve a stored secret if available."""

    try:
        import keyring
    except ImportError:  # pragma: no cover - exercised via tests
        return os.environ.get(_env_secret_key(service, username))

    return keyring.get_password(service, username)


def delete_secret(service: str, username: str) -> None:
    """Delete a stored secret if present."""

    try:
        import keyring
    except ImportError:  # pragma: no cover - exercised via tests
        os.environ.pop(_env_secret_key(service, username), None)
    else:
        keyring.delete_password(service, username)


def read_secret_from_input(provided: str | None) -> str:
    """Return a secret value from ``provided`` or interactively when ``None``."""

    if provided is not None:
        return provided

    if not sys.stdin.isatty():
        value = sys.stdin.read().rstrip("\n")
        if value:
            return value
        raise SystemExit("No secret data received from stdin.")

    return getpass.getpass("Secret: ")  # pragma: no cover - interactive prompt


# Backwards compatibility for previous private helper name.
_read_secret_from_input = read_secret_from_input


__all__ = [
    "SECRET_ENV_PREFIX",
    "_env_secret_key",
    "store_secret",
    "get_secret",
    "delete_secret",
    "read_secret_from_input",
]
