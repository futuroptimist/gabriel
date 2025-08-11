from gabriel.utils import (
    add,
    subtract,
    multiply,
    divide,
    store_secret,
    get_secret,
)
import keyring
from keyring.backend import KeyringBackend
import builtins
import pytest


def test_add():
    assert add(1, 2) == 3  # nosec B101


def test_add_negative_numbers():
    assert add(-1, -2) == -3  # nosec B101


def test_subtract():
    assert subtract(5, 3) == 2  # nosec B101


def test_subtract_negative_result():
    assert subtract(3, 5) == -2  # nosec B101


def test_multiply():
    assert multiply(2, 3) == 6  # nosec B101


def test_multiply_negative_numbers():
    assert multiply(-2, -3) == 6  # nosec B101


def test_multiply_with_negative_number():
    assert multiply(-2, 3) == -6  # nosec B101


def test_divide():
    assert divide(6, 3) == 2  # nosec B101


def test_divide_negative_numbers():
    assert divide(-6, -3) == 2  # nosec B101


def test_divide_with_negative_number():
    assert divide(-6, 3) == -2  # nosec B101


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


class InMemoryKeyring(KeyringBackend):
    """Simple in-memory keyring backend for testing."""

    priority = 1

    def __init__(self) -> None:
        self._storage: dict[tuple[str, str], str] = {}

    def get_password(self, system: str, username: str) -> str | None:  # noqa: D401
        return self._storage.get((system, username))

    def set_password(
        self, system: str, username: str, password: str
    ) -> None:  # noqa: D401
        self._storage[(system, username)] = password

    def delete_password(self, system: str, username: str) -> None:  # noqa: D401
        self._storage.pop((system, username), None)


def test_store_and_get_secret():
    keyring.set_keyring(InMemoryKeyring())
    store_secret("service", "user", "hunter2")
    assert get_secret("service", "user") == "hunter2"  # nosec B101


@pytest.mark.parametrize(
    "func,args",
    [
        (store_secret, ("svc", "user", "pw")),
        (get_secret, ("svc", "user")),
    ],
)
def test_keyring_missing(monkeypatch, func, args):
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "keyring":
            raise ModuleNotFoundError
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(RuntimeError, match="keyring"):  # nosec B101
        func(*args)
