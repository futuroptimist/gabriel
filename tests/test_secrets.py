"""Unit tests for :mod:`gabriel.secrets` and CLI interactions."""

from __future__ import annotations

import builtins
import io
import os
import string
import sys

import keyring
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from keyring.backend import KeyringBackend

import gabriel.utils as utils_module
from gabriel.secrets import _env_secret_key, delete_secret, get_secret, store_secret
from gabriel.utils import main


class InMemoryKeyring(KeyringBackend):
    """Simple in-memory keyring backend for testing."""

    priority = 1

    def __init__(self) -> None:
        self._storage: dict[tuple[str, str], str] = {}

    def get_password(self, system: str, username: str) -> str | None:  # noqa: D401
        return self._storage.get((system, username))

    def set_password(self, system: str, username: str, password: str) -> None:  # noqa: D401
        self._storage[(system, username)] = password

    def delete_password(self, system: str, username: str) -> None:  # noqa: D401
        self._storage.pop((system, username), None)


def test_store_get_and_delete_secret() -> None:
    keyring.set_keyring(InMemoryKeyring())
    store_secret("service", "user", "hunter2")
    assert get_secret("service", "user") == "hunter2"  # nosec B101
    delete_secret("service", "user")
    assert get_secret("service", "user") is None  # nosec B101


def test_cli_add(capsys: pytest.CaptureFixture[str]) -> None:
    main(["add", "2", "3"])
    assert capsys.readouterr().out.strip() == "5"  # nosec B101


def test_cli_sqrt(capsys: pytest.CaptureFixture[str]) -> None:
    main(["sqrt", "9"])
    assert capsys.readouterr().out.strip() == "3"  # nosec B101


def test_cli_secret_store_get_delete(capsys: pytest.CaptureFixture[str]) -> None:
    keyring.set_keyring(InMemoryKeyring())

    main(["secret", "store", "svc", "user", "--secret", "hunter2"])
    assert capsys.readouterr().out.strip() == "Secret stored."  # nosec B101

    main(["secret", "get", "svc", "user"])
    get_output = capsys.readouterr().out.strip()
    assert (
        get_output == "Secret successfully retrieved. (Value not displayed for security reasons.)"
    )  # nosec B101
    assert "hunter2" not in get_output  # nosec B101
    assert get_secret("svc", "user") == "hunter2"  # nosec B101

    main(["secret", "delete", "svc", "user"])
    assert capsys.readouterr().out.strip() == "Secret deleted."  # nosec B101
    assert get_secret("svc", "user") is None  # nosec B101


def test_cli_secret_get_missing() -> None:
    keyring.set_keyring(InMemoryKeyring())

    with pytest.raises(SystemExit) as excinfo:
        main(["secret", "get", "svc", "user"])

    assert excinfo.value.code == "No secret stored for the requested service/user."  # nosec B101


def test_cli_secret_store_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    keyring.set_keyring(InMemoryKeyring())

    class FakeInput(io.StringIO):
        def isatty(self) -> bool:  # noqa: D401 - simple shim
            return False

    fake_stdin = FakeInput("vault-value\n")
    monkeypatch.setattr(sys, "stdin", fake_stdin)

    main(["secret", "store", "svc", "user"])
    assert capsys.readouterr().out.strip() == "Secret stored."  # nosec B101
    assert get_secret("svc", "user") == "vault-value"  # nosec B101


def test_cli_secret_store_requires_input(monkeypatch: pytest.MonkeyPatch) -> None:
    keyring.set_keyring(InMemoryKeyring())

    class FakeInput(io.StringIO):
        def isatty(self) -> bool:  # noqa: D401 - simple shim
            return False

    monkeypatch.setattr(sys, "stdin", FakeInput(""))

    with pytest.raises(SystemExit) as excinfo:
        main(["secret", "store", "svc", "user"])

    assert excinfo.value.code == "No secret data received from stdin."  # nosec B101


def test_env_secret_key_fallback_identifier() -> None:
    assert _env_secret_key("", "") == "GABRIEL_SECRET_IDENTIFIER"  # nosec B101


IDENTIFIER_ALPHABET = string.ascii_letters + string.digits + "-_.:@/ "
SECRET_ALPHABET = string.ascii_letters + string.digits + string.punctuation + " "


@settings(max_examples=200, deadline=None)
@given(
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=32),
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=32),
)
def test_env_secret_key_is_normalized(service: str, username: str) -> None:
    key = _env_secret_key(service, username)
    assert key.startswith("GABRIEL_SECRET_")  # nosec B101
    prefix = "GABRIEL_SECRET_"
    suffix = key.removeprefix(prefix)
    assert suffix  # nosec B101
    assert suffix == suffix.upper()  # nosec B101
    assert not suffix.startswith("_")  # nosec B101
    assert set(suffix) <= set(string.ascii_uppercase + string.digits + "_")  # nosec B101


def test_env_secret_key_preserves_underscore_uniqueness() -> None:
    baseline = _env_secret_key("foo", "bar")
    trailing_service = _env_secret_key("foo_", "bar")
    trailing_username = _env_secret_key("foo", "bar__")
    trailing_both = _env_secret_key("foo__", "bar__")

    assert baseline == "GABRIEL_SECRET_FOO_BAR"  # nosec B101
    assert trailing_service == "GABRIEL_SECRET_FOO__BAR"  # nosec B101
    assert trailing_username == "GABRIEL_SECRET_FOO_BAR__"  # nosec B101
    assert trailing_both == "GABRIEL_SECRET_FOO___BAR__"  # nosec B101


@settings(max_examples=100, deadline=None)
@given(
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=16),
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=16),
    st.text(SECRET_ALPHABET, min_size=1, max_size=64),
)
def test_secret_env_round_trip_property(service: str, username: str, secret: str) -> None:
    assume("\x00" not in secret)
    env_key = _env_secret_key(service, username)
    patch = pytest.MonkeyPatch()
    patch.delenv(env_key, raising=False)

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):  # type: ignore[override]
        if name == "keyring":
            raise ModuleNotFoundError
        return real_import(name, *args, **kwargs)

    patch.setattr(builtins, "__import__", fake_import)

    try:
        store_secret(service, username, secret)
        assert os.environ[env_key] == secret  # nosec B101
        assert get_secret(service, username) == secret  # nosec B101
        delete_secret(service, username)
        assert env_key not in os.environ  # nosec B101
    finally:
        patch.undo()


def test_utils_module_provides_env_secret_key_alias() -> None:
    assert utils_module._env_secret_key is _env_secret_key  # nosec B101
