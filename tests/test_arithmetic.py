"""Unit tests for :mod:`gabriel.arithmetic`."""

from __future__ import annotations

from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from gabriel.arithmetic import (
    add,
    divide,
    floordiv,
    modulo,
    multiply,
    power,
    sqrt,
    subtract,
)


def test_add_negative_numbers() -> None:
    assert add(-1, -2) == Decimal("-3")  # nosec B101


def test_add_floats() -> None:
    assert add(1.5, 2.5) == Decimal("4.0")  # nosec B101


def test_add_invalid_type() -> None:
    with pytest.raises(TypeError):
        add("1", 2)  # type: ignore[arg-type]


def test_subtract() -> None:
    assert subtract(5, 3) == Decimal("2")  # nosec B101


def test_subtract_negative_result() -> None:
    assert subtract(3, 5) == Decimal("-2")  # nosec B101


def test_subtract_floats() -> None:
    assert subtract(5.5, 3.5) == Decimal("2.0")  # nosec B101


def test_multiply() -> None:
    assert multiply(2, 3) == Decimal("6")  # nosec B101


def test_multiply_negative_numbers() -> None:
    assert multiply(-2, -3) == Decimal("6")  # nosec B101


def test_multiply_with_negative_number() -> None:
    assert multiply(-2, 3) == Decimal("-6")  # nosec B101


def test_multiply_floats() -> None:
    assert multiply(2.5, 4.0) == Decimal("10.0")  # nosec B101


def test_divide() -> None:
    assert divide(6, 3) == Decimal("2")  # nosec B101


def test_divide_negative_numbers() -> None:
    assert divide(-6, 3) == Decimal("-2")  # nosec B101
    assert divide(6, -3) == Decimal("-2")  # nosec B101
    assert divide(-6, -3) == Decimal("2")  # nosec B101


def test_divide_floats() -> None:
    assert divide(7.5, 2.5) == Decimal("3.0")  # nosec B101


def test_divide_by_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)


def test_power() -> None:
    assert power(2, 3) == Decimal("8")  # nosec B101


def test_power_floats() -> None:
    assert power(2.0, 3.0) == Decimal("8.0")  # nosec B101


def test_power_fractional_exponent() -> None:
    assert power(9, 0.5) == Decimal("3.0")  # nosec B101


def test_power_zero_negative_exponent() -> None:
    with pytest.raises(ZeroDivisionError):
        power(0, -1)


def test_power_zero_negative_fractional_exponent() -> None:
    with pytest.raises(ZeroDivisionError):
        power(0, Decimal("-0.5"))


def test_power_zero_fractional_positive_exponent() -> None:
    assert power(0, Decimal("0.5")) == Decimal("0")  # nosec B101


def test_power_invalid_complex_result() -> None:
    with pytest.raises(ValueError):
        power(-8, 0.5)


def test_power_fractional_extreme_precision() -> None:
    assert power(Decimal("1e-400"), Decimal("0.5")) == Decimal("1E-200")  # nosec B101


def test_modulo() -> None:
    assert modulo(5, 2) == Decimal("1")  # nosec B101


def test_modulo_floats() -> None:
    assert modulo(5.5, 2.0) == Decimal("1.5")  # nosec B101


def test_modulo_negative_dividend() -> None:
    assert modulo(-7, 2) == Decimal("1")  # nosec B101


def test_modulo_negative_divisor() -> None:
    assert modulo(7, -2) == Decimal("-1")  # nosec B101


def test_modulo_by_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        modulo(1, 0)


def test_floordiv() -> None:
    assert floordiv(7, 2) == Decimal("3")  # nosec B101


def test_floordiv_negative_numbers() -> None:
    assert floordiv(-7, 2) == Decimal("-4")  # nosec B101
    assert floordiv(7, -2) == Decimal("-4")  # nosec B101
    assert floordiv(-7, -2) == Decimal("3")  # nosec B101


def test_floordiv_floats() -> None:
    assert floordiv(7.5, 2.5) == Decimal("3")  # nosec B101


def test_floordiv_by_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        floordiv(1, 0)


def test_sqrt() -> None:
    assert sqrt(9) == Decimal("3")  # nosec B101
    assert sqrt(2.25) == Decimal("1.5")  # nosec B101


def test_sqrt_negative() -> None:
    with pytest.raises(ValueError):
        sqrt(-1)


@settings(max_examples=200, deadline=None)
@given(st.integers(-(10**6), 10**6), st.integers(-(10**6), 10**6))
def test_add_commutative(a: int, b: int) -> None:
    assert add(a, b) == add(b, a)  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.integers(-(10**6), 10**6), st.integers(-(10**6), 10**6))
def test_multiply_commutative(a: int, b: int) -> None:
    assert multiply(a, b) == multiply(b, a)  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.integers(-(10**6), 10**6), st.integers(-(10**6), 10**6))
def test_subtract_inverse_of_add(a: int, b: int) -> None:
    assert subtract(add(a, b), b) == a  # nosec B101


@settings(max_examples=200, deadline=None)
@given(
    st.integers(-(10**3), 10**3),
    st.integers(-(10**3), 10**3).filter(lambda value: value != 0),
)
def test_divide_inverse_of_multiply(a: int, b: int) -> None:
    result = divide(multiply(a, b), b)
    assert result == pytest.approx(float(a))  # nosec B101


@settings(max_examples=200, deadline=None)
@given(
    st.integers(-(10**3), 10**3),
    st.integers(-(10**3), 10**3).filter(lambda value: value != 0),
)
def test_divmod_identity(a: int, b: int) -> None:
    quotient = floordiv(a, b)
    remainder = modulo(a, b)
    assert quotient * b + remainder == a  # nosec B101
    if b > 0:
        assert 0 <= remainder < b  # nosec B101
    else:
        assert b < remainder <= 0  # nosec B101


@settings(max_examples=200, deadline=None)
@given(st.floats(min_value=-(10**3), max_value=10**3, allow_nan=False, allow_infinity=False))
def test_sqrt_inverse_of_square(value: float) -> None:
    squared = value * value
    result = sqrt(squared)
    assert float(result) == pytest.approx(abs(value))  # nosec B101
