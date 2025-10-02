"""Arithmetic helpers using :mod:`decimal` for improved precision."""

from __future__ import annotations

from decimal import ROUND_FLOOR, Decimal, InvalidOperation, localcontext

Numeric = float | int | Decimal


def _to_decimal(value: Numeric) -> Decimal:
    """Return ``value`` as a :class:`~decimal.Decimal` instance."""

    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    msg = f"Unsupported numeric type: {type(value)!r}"
    raise TypeError(msg)


def add(a: Numeric, b: Numeric) -> Decimal:
    """Return the sum of ``a`` and ``b``."""

    return _to_decimal(a) + _to_decimal(b)


def subtract(a: Numeric, b: Numeric) -> Decimal:
    """Return the result of ``a`` minus ``b``."""

    return _to_decimal(a) - _to_decimal(b)


def multiply(a: Numeric, b: Numeric) -> Decimal:
    """Return the product of ``a`` and ``b``."""

    return _to_decimal(a) * _to_decimal(b)


def divide(a: Numeric, b: Numeric) -> Decimal:
    """Return the result of ``a`` divided by ``b``."""

    denominator = _to_decimal(b)
    if denominator == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return _to_decimal(a) / denominator


def power(a: Numeric, b: Numeric) -> Decimal:
    """Return ``a`` raised to the power of ``b``."""

    base = _to_decimal(a)
    exponent = _to_decimal(b)
    if exponent == exponent.to_integral_value():
        if base == 0 and exponent < 0:
            raise ZeroDivisionError("0.0 cannot be raised to a negative power")
        return base**exponent

    if base == 0:
        if exponent < 0:
            raise ZeroDivisionError("0.0 cannot be raised to a negative power")
        return Decimal(0)

    if base < 0:
        raise ValueError("Invalid power operation for complex result.")

    with localcontext() as ctx:
        ctx.prec += 10
        try:
            result = (exponent * base.ln()).exp()
        except (InvalidOperation, ValueError) as error:  # pragma: no cover - decimal domain errors
            raise ValueError("Invalid power operation for complex result.") from error

    return +result


def modulo(a: Numeric, b: Numeric) -> Decimal:
    """Return ``a`` modulo ``b``."""

    denominator = _to_decimal(b)
    if denominator == 0:
        raise ZeroDivisionError("Cannot modulo by zero.")
    numerator = _to_decimal(a)
    quotient = (numerator / denominator).to_integral_value(rounding=ROUND_FLOOR)
    return numerator - denominator * quotient


def floordiv(a: Numeric, b: Numeric) -> Decimal:
    """Return the floor division of ``a`` by ``b``."""

    denominator = _to_decimal(b)
    if denominator == 0:
        raise ZeroDivisionError("Cannot floor-divide by zero.")
    numerator = _to_decimal(a)
    return (numerator / denominator).to_integral_value(rounding=ROUND_FLOOR)


def sqrt(a: Numeric) -> Decimal:
    """Return the square root of ``a``."""

    value = _to_decimal(a)
    if value < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    try:
        return value.sqrt()
    except InvalidOperation as error:  # pragma: no cover - mirrored in decimal
        raise ValueError("Cannot take the square root of a negative number.") from error


__all__ = [
    "Numeric",
    "add",
    "subtract",
    "multiply",
    "divide",
    "power",
    "modulo",
    "floordiv",
    "sqrt",
]
