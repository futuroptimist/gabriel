"""Tests for :mod:`gabriel.common` exports."""

from __future__ import annotations

from gabriel.common import DEFAULT_SECRET_STORE, KeyringSecretStore, SecretStore


def test_default_secret_store_is_keyring() -> None:
    """The default secret store should be the keyring-backed implementation."""
    assert isinstance(DEFAULT_SECRET_STORE, KeyringSecretStore)


def test_secret_store_protocol_methods() -> None:
    """Protocol methods exist on the default secret store."""
    store: SecretStore = DEFAULT_SECRET_STORE
    assert hasattr(store, "store")
    assert hasattr(store, "retrieve")
    assert hasattr(store, "delete")
