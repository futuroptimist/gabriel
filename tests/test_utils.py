import builtins
from decimal import Decimal

import keyring
import pytest
from keyring.backend import KeyringBackend

from gabriel.utils import (
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
    assert add(1, 2) == Decimal("3")  # nosec B101


def test_add_negative_numbers():
    assert add(-1, -2) == Decimal("-3")  # nosec B101


def test_add_floats():
    assert add(1.5, 2.5) == Decimal("4.0")  # nosec B101


def test_add_invalid_type():
    with pytest.raises(TypeError):
        add("1", 2)


def test_subtract():
    assert subtract(5, 3) == Decimal("2")  # nosec B101


def test_subtract_negative_result():
    assert subtract(3, 5) == Decimal("-2")  # nosec B101


def test_subtract_floats():
    assert subtract(5.5, 3.5) == Decimal("2.0")  # nosec B101


def test_multiply():
    assert multiply(2, 3) == Decimal("6")  # nosec B101


def test_multiply_negative_numbers():
    assert multiply(-2, -3) == Decimal("6")  # nosec B101


def test_multiply_with_negative_number():
    assert multiply(-2, 3) == Decimal("-6")  # nosec B101


def test_multiply_floats():
    assert multiply(2.5, 4.0) == Decimal("10.0")  # nosec B101


def test_divide():
    assert divide(6, 3) == Decimal("2")  # nosec B101


def test_divide_negative_numbers():
    assert divide(-6, 3) == Decimal("-2")  # nosec B101
    assert divide(6, -3) == Decimal("-2")  # nosec B101
    assert divide(-6, -3) == Decimal("2")  # nosec B101


def test_divide_floats():
    assert divide(7.5, 2.5) == Decimal("3.0")  # nosec B101


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


def test_power():
    assert power(2, 3) == Decimal("8")  # nosec B101


def test_power_floats():
    assert power(2.0, 3.0) == Decimal("8.0")  # nosec B101


def test_power_fractional_exponent():
    assert power(9, 0.5) == Decimal("3.0")  # nosec B101


def test_power_zero_negative_exponent():
    with pytest.raises(ZeroDivisionError):
        power(0, -1)


def test_power_zero_negative_fractional_exponent():
    with pytest.raises(ZeroDivisionError):
        power(0, Decimal("-0.5"))


def test_power_zero_fractional_positive_exponent():
    assert power(0, Decimal("0.5")) == Decimal("0")  # nosec B101


def test_power_invalid_complex_result():
    with pytest.raises(ValueError):
        power(-8, 0.5)


def test_power_fractional_extreme_precision():
    assert power(Decimal("1e-400"), Decimal("0.5")) == Decimal("1E-200")  # nosec B101


def test_modulo():
    assert modulo(5, 2) == Decimal("1")  # nosec B101


def test_modulo_floats():
    assert modulo(5.5, 2.0) == Decimal("1.5")  # nosec B101


def test_modulo_negative_dividend():
    assert modulo(-7, 2) == Decimal("1")  # nosec B101


def test_modulo_negative_divisor():
    assert modulo(7, -2) == Decimal("-1")  # nosec B101


def test_modulo_by_zero():
    with pytest.raises(ZeroDivisionError):
        modulo(1, 0)


def test_floordiv():
    assert floordiv(7, 2) == Decimal("3")  # nosec B101


def test_floordiv_negative_numbers():
    assert floordiv(-7, 2) == Decimal("-4")  # nosec B101
    assert floordiv(7, -2) == Decimal("-4")  # nosec B101
    assert floordiv(-7, -2) == Decimal("3")  # nosec B101


def test_floordiv_floats():
    assert floordiv(7.5, 2.5) == Decimal("3")  # nosec B101


def test_floordiv_by_zero():
    with pytest.raises(ZeroDivisionError):
        floordiv(1, 0)


def test_sqrt():
    assert sqrt(9) == Decimal("3")  # nosec B101
    assert sqrt(2.25) == Decimal("1.5")  # nosec B101


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
    assert capsys.readouterr().out.strip() == "5"  # nosec B101


def test_cli_sqrt(capsys):
    main(["sqrt", "9"])
    assert capsys.readouterr().out.strip() == "3"  # nosec B101
