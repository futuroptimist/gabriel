import builtins
import os
import string

import keyring
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from keyring.backend import KeyringBackend

from gabriel.utils import (
    _env_secret_key,
    add,
    delete_secret,
    divide,
    floordiv,
    get_secret,
    main,
    modulo,
    multiply,
    power,
    sqrt,
    store_secret,
    subtract,
)


def test_add():
    assert add(1, 2) == 3  # nosec B101


def test_add_negative_numbers():
    assert add(-1, -2) == -3  # nosec B101


def test_add_floats():
    assert add(1.5, 2.5) == 4.0  # nosec B101


def test_subtract():
    assert subtract(5, 3) == 2  # nosec B101


def test_subtract_negative_result():
    assert subtract(3, 5) == -2  # nosec B101


def test_subtract_floats():
    assert subtract(5.5, 3.5) == 2.0  # nosec B101


def test_multiply():
    assert multiply(2, 3) == 6  # nosec B101


def test_multiply_negative_numbers():
    assert multiply(-2, -3) == 6  # nosec B101


def test_multiply_with_negative_number():
    assert multiply(-2, 3) == -6  # nosec B101


def test_multiply_floats():
    assert multiply(2.5, 4.0) == 10.0  # nosec B101


def test_divide():
    assert divide(6, 3) == 2  # nosec B101


def test_divide_negative_numbers():
    assert divide(-6, 3) == -2  # nosec B101
    assert divide(6, -3) == -2  # nosec B101
    assert divide(-6, -3) == 2  # nosec B101


def test_divide_floats():
    assert divide(7.5, 2.5) == 3.0  # nosec B101


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


def test_power():
    assert power(2, 3) == 8  # nosec B101


def test_power_floats():
    assert power(2.0, 3.0) == 8.0  # nosec B101


def test_modulo():
    assert modulo(5, 2) == 1  # nosec B101


def test_modulo_floats():
    assert modulo(5.5, 2.0) == 1.5  # nosec B101


def test_modulo_by_zero():
    with pytest.raises(ZeroDivisionError):
        modulo(1, 0)


def test_floordiv():
    assert floordiv(7, 2) == 3  # nosec B101


def test_floordiv_negative_numbers():
    assert floordiv(-7, 2) == -4  # nosec B101
    assert floordiv(7, -2) == -4  # nosec B101
    assert floordiv(-7, -2) == 3  # nosec B101


def test_floordiv_floats():
    assert floordiv(7.5, 2.5) == 3.0  # nosec B101


def test_floordiv_by_zero():
    with pytest.raises(ZeroDivisionError):
        floordiv(1, 0)


def test_sqrt():
    assert sqrt(9) == 3.0  # nosec B101
    assert sqrt(2.25) == 1.5  # nosec B101


def test_sqrt_negative():
    with pytest.raises(ValueError):
        sqrt(-1)


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


def test_store_get_and_delete_secret():
    keyring.set_keyring(InMemoryKeyring())
    store_secret("service", "user", "hunter2")
    assert get_secret("service", "user") == "hunter2"  # nosec B101
    delete_secret("service", "user")
    assert get_secret("service", "user") is None  # nosec B101


def test_secret_env_fallback(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "keyring":
            raise ModuleNotFoundError
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    store_secret("svc", "user", "pw")
    assert get_secret("svc", "user") == "pw"  # nosec B101
    delete_secret("svc", "user")
    assert get_secret("svc", "user") is None  # nosec B101


def test_cli_add(capsys):
    main(["add", "2", "3"])
    assert capsys.readouterr().out.strip() == "5.0"  # nosec B101


def test_cli_sqrt(capsys):
    main(["sqrt", "9"])
    assert capsys.readouterr().out.strip() == "3.0"  # nosec B101


def test_env_secret_key_fallback_identifier():
    assert _env_secret_key("", "") == "GABRIEL_SECRET_IDENTIFIER"  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.integers(-(10**6), 10**6), st.integers(-(10**6), 10**6))
def test_add_commutative(a, b):
    assert add(a, b) == add(b, a)  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.integers(-(10**6), 10**6), st.integers(-(10**6), 10**6))
def test_multiply_commutative(a, b):
    assert multiply(a, b) == multiply(b, a)  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.integers(-(10**6), 10**6), st.integers(-(10**6), 10**6))
def test_subtract_inverse_of_add(a, b):
    assert subtract(add(a, b), b) == a  # nosec B101


@settings(max_examples=200, deadline=None)
@given(
    st.integers(-(10**3), 10**3),
    st.integers(-(10**3), 10**3).filter(lambda value: value != 0),
)
def test_divide_inverse_of_multiply(a, b):
    result = divide(multiply(a, b), b)
    assert result == pytest.approx(float(a))  # nosec B101


@settings(max_examples=200, deadline=None)
@given(
    st.integers(-(10**3), 10**3),
    st.integers(-(10**3), 10**3).filter(lambda value: value != 0),
)
def test_divmod_identity(a, b):
    quotient = floordiv(a, b)
    remainder = modulo(a, b)
    assert quotient * b + remainder == a  # nosec B101
    if b > 0:
        assert 0 <= remainder < b  # nosec B101
    else:
        assert b < remainder <= 0  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.floats(min_value=-(10**3), max_value=10**3, allow_nan=False, allow_infinity=False))
def test_sqrt_inverse_of_square(value):
    squared = value * value
    assert sqrt(squared) == pytest.approx(abs(value))  # nosec B101


IDENTIFIER_ALPHABET = string.ascii_letters + string.digits + "-_.:@/ "
SECRET_ALPHABET = string.ascii_letters + string.digits + string.punctuation + " "


@settings(max_examples=200, deadline=None)
@given(
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=32),
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=32),
)
def test_env_secret_key_is_normalized(service, username):
    key = _env_secret_key(service, username)
    assert key.startswith("GABRIEL_SECRET_")  # nosec B101
    prefix = "GABRIEL_SECRET_"
    suffix = key.removeprefix(prefix)
    assert suffix  # nosec B101
    assert suffix == suffix.upper()  # nosec B101
    assert "__" not in suffix  # nosec B101
    assert not suffix.startswith("_")  # nosec B101
    assert not suffix.endswith("_")  # nosec B101
    assert set(suffix) <= set(string.ascii_uppercase + string.digits + "_")  # nosec B101


@settings(max_examples=100, deadline=None)
@given(
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=16),
    st.text(IDENTIFIER_ALPHABET, min_size=1, max_size=16),
    st.text(SECRET_ALPHABET, min_size=1, max_size=64),
)
def test_secret_env_round_trip_property(service, username, secret):
    assume("\x00" not in secret)
    env_key = _env_secret_key(service, username)
    patch = pytest.MonkeyPatch()
    patch.delenv(env_key, raising=False)

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
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
