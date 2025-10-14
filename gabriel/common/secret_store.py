"""Secret store implementations that satisfy :mod:`gabriel.common.interfaces`."""

from __future__ import annotations

import getpass
import os
import re
import sys
from typing import Final

from .interfaces import SecretStore

SECRET_ENV_PREFIX: Final[str] = "GABRIEL_SECRET_"


def _normalize_identifier(value: str) -> str:
    """Return a sanitized identifier for environment variable keys."""
    sanitized = re.sub(r"\W", "_", value)
    if sanitized.strip("_"):
        return sanitized.lstrip("_")
    return "IDENTIFIER"


def _env_secret_key(service: str, username: str) -> str:
    """Return a normalized environment variable key for ``service`` and ``username``."""
    combined = f"{service}_{username}"
    identifier = _normalize_identifier(combined)
    return f"{SECRET_ENV_PREFIX}{identifier.upper()}"


class KeyringSecretStore(SecretStore):
    """Secret store that prefers ``keyring`` but falls back to environment variables."""

    def store(self, service: str, username: str, secret: str, /) -> None:  # noqa: D401
        try:
            import keyring
        except ImportError:  # pragma: no cover - exercised via unit tests
            os.environ[_env_secret_key(service, username)] = secret
        else:
            keyring.set_password(service, username, secret)

    def retrieve(self, service: str, username: str, /) -> str | None:  # noqa: D401
        try:
            import keyring
        except ImportError:  # pragma: no cover - exercised via unit tests
            return os.environ.get(_env_secret_key(service, username))
        return keyring.get_password(service, username)

    def delete(self, service: str, username: str, /) -> None:  # noqa: D401
        try:
            import keyring
        except ImportError:  # pragma: no cover - exercised via unit tests
            os.environ.pop(_env_secret_key(service, username), None)
        else:
            keyring.delete_password(service, username)


DEFAULT_SECRET_STORE: SecretStore = KeyringSecretStore()


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


__all__ = [
    "DEFAULT_SECRET_STORE",
    "KeyringSecretStore",
    "SECRET_ENV_PREFIX",
    "_env_secret_key",
    "read_secret_from_input",
]
