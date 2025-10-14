"""Compatibility layer for secret management helpers."""

from __future__ import annotations

from gabriel.common.secret_store import (
    DEFAULT_SECRET_STORE,
    SECRET_ENV_PREFIX,
    KeyringSecretStore,
    _env_secret_key,
    read_secret_from_input,
)

store_secret = DEFAULT_SECRET_STORE.store
get_secret = DEFAULT_SECRET_STORE.retrieve
delete_secret = DEFAULT_SECRET_STORE.delete

# Backwards compatibility for previous private helper name.
_read_secret_from_input = read_secret_from_input

__all__ = [
    "SECRET_ENV_PREFIX",
    "_env_secret_key",
    "store_secret",
    "get_secret",
    "delete_secret",
    "read_secret_from_input",
    "KeyringSecretStore",
]
