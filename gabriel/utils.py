import argparse
import math
import os
import re

"""Utility helpers for arithmetic operations and secret management."""


def add(a: float | int, b: float | int) -> float | int:
    """Return the sum of ``a`` and ``b``.

    Supports both integers and floats.
    """
    return a + b


def subtract(a: float | int, b: float | int) -> float | int:
    """Return the result of ``a`` minus ``b``.

    Supports both integers and floats.
    """
    return a - b


def multiply(a: float | int, b: float | int) -> float | int:
    """Return the product of ``a`` and ``b``.

    Supports both integers and floats.
    """
    return a * b


def divide(a: float | int, b: float | int) -> float:
    """Return the result of ``a`` divided by ``b``.

    Supports both integers and floats.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def power(a: float | int, b: float | int) -> float | int:
    """Return ``a`` raised to the power of ``b``.

    Supports both integers and floats.
    """
    return a**b


def modulo(a: float | int, b: float | int) -> float | int:
    """Return ``a`` modulo ``b``.

    Supports both integers and floats.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot modulo by zero.")
    return a % b


def floordiv(a: float | int, b: float | int) -> float:
    """Return the floor division of ``a`` by ``b``.

    Supports both integers and floats.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot floor-divide by zero.")
    return a // b


def sqrt(a: float | int) -> float:
    """Return the square root of ``a``.

    Supports both integers and floats.

    Raises
    ------
    ValueError
        If ``a`` is negative.
    """
    if a < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    return math.sqrt(a)


def _env_secret_key(service: str, username: str) -> str:
    """Return the environment variable key for a given ``service`` and ``username``."""

    safe = re.sub(r"\W+", "_", f"{service}_{username}").upper()
    return f"GABRIEL_SECRET_{safe}"


def store_secret(service: str, username: str, secret: str) -> None:
    """Store ``secret`` using ``keyring`` or environment variables.

    If the optional ``keyring`` dependency is unavailable, the secret is stored in an
    environment variable named via :func:`_env_secret_key`.

    Parameters
    ----------
    service:
        The name of the service associated with the secret.
    username:
        The user identifier for the secret.
    secret:
        The secret value to store.
    """
    try:
        import keyring
    except ImportError:  # pragma: no cover - exercised via tests
        os.environ[_env_secret_key(service, username)] = secret
    else:
        keyring.set_password(service, username, secret)


def get_secret(service: str, username: str) -> str | None:
    """Retrieve a stored secret.

    Attempts to use ``keyring`` and falls back to environment variables when the
    package is unavailable.

    Returns
    -------
    str | None
        The stored secret or ``None`` if no value is found.
    """
    try:
        import keyring
    except ImportError:  # pragma: no cover - exercised via tests
        return os.environ.get(_env_secret_key(service, username))

    return keyring.get_password(service, username)


def delete_secret(service: str, username: str) -> None:
    """Delete a stored secret.

    Works with ``keyring`` when available and otherwise clears the corresponding
    environment variable.
    """
    try:
        import keyring
    except ImportError:  # pragma: no cover - exercised via tests
        os.environ.pop(_env_secret_key(service, username), None)
    else:
        keyring.delete_password(service, username)


def main(argv: list[str] | None = None) -> None:
    """CLI for arithmetic helpers.

    Parameters
    ----------
    argv:
        Optional list of arguments. Defaults to :data:`sys.argv`.
    """

    parser = argparse.ArgumentParser(description="Gabriel arithmetic helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def two_arg(name: str, func) -> None:  # type: ignore[no-untyped-def]
        sub = subparsers.add_parser(name, help=f"{name.title()} two numbers")
        sub.add_argument("a", type=float)
        sub.add_argument("b", type=float)
        sub.set_defaults(func=func)

    two_arg("add", add)
    two_arg("subtract", subtract)
    two_arg("multiply", multiply)
    two_arg("divide", divide)
    two_arg("power", power)
    two_arg("modulo", modulo)
    two_arg("floordiv", floordiv)

    sqrt_parser = subparsers.add_parser("sqrt", help="Square root of a number")
    sqrt_parser.add_argument("a", type=float)
    sqrt_parser.set_defaults(func=sqrt)

    args = parser.parse_args(argv)

    if args.command == "sqrt":
        result = args.func(args.a)
    else:
        result = args.func(args.a, args.b)

    print(result)


if __name__ == "__main__":  # pragma: no cover - manual CLI execution
    main()
