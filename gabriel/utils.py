import argparse
import getpass
import os
import re
import sys
from decimal import ROUND_FLOOR, Decimal, InvalidOperation, localcontext

"""Utility helpers for arithmetic operations and secret management."""


Numeric = float | int | Decimal


def _to_decimal(value: Numeric) -> Decimal:
    """Return ``value`` as a :class:`~decimal.Decimal`.

    Floats are converted via ``str`` to avoid binary rounding artefacts.
    """

    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    msg = f"Unsupported numeric type: {type(value)!r}"
    raise TypeError(msg)


def add(a: Numeric, b: Numeric) -> Decimal:
    """Return the sum of ``a`` and ``b`` with decimal precision."""

    return _to_decimal(a) + _to_decimal(b)


def subtract(a: Numeric, b: Numeric) -> Decimal:
    """Return the result of ``a`` minus ``b`` with decimal precision."""

    return _to_decimal(a) - _to_decimal(b)


def multiply(a: Numeric, b: Numeric) -> Decimal:
    """Return the product of ``a`` and ``b`` with decimal precision."""

    return _to_decimal(a) * _to_decimal(b)


def divide(a: Numeric, b: Numeric) -> Decimal:
    """Return the result of ``a`` divided by ``b`` with decimal precision."""

    denominator = _to_decimal(b)
    if denominator == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return _to_decimal(a) / denominator


def power(a: Numeric, b: Numeric) -> Decimal:
    """Return ``a`` raised to the power of ``b`` with decimal precision."""

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
    """Return ``a`` modulo ``b`` with decimal precision."""

    denominator = _to_decimal(b)
    if denominator == 0:
        raise ZeroDivisionError("Cannot modulo by zero.")
    numerator = _to_decimal(a)
    quotient = (numerator / denominator).to_integral_value(rounding=ROUND_FLOOR)
    return numerator - denominator * quotient


def floordiv(a: Numeric, b: Numeric) -> Decimal:
    """Return the floor division of ``a`` by ``b`` with decimal precision."""

    denominator = _to_decimal(b)
    if denominator == 0:
        raise ZeroDivisionError("Cannot floor-divide by zero.")
    numerator = _to_decimal(a)
    return (numerator / denominator).to_integral_value(rounding=ROUND_FLOOR)


def sqrt(a: Numeric) -> Decimal:
    """Return the square root of ``a`` with decimal precision.

    Raises
    ------
    ValueError
        If ``a`` is negative.
    """

    value = _to_decimal(a)
    if value < 0:
        raise ValueError("Cannot take the square root of a negative number.")
    try:
        return value.sqrt()
    except InvalidOperation as error:  # pragma: no cover - mirrored in decimal
        raise ValueError("Cannot take the square root of a negative number.") from error


def _env_secret_key(service: str, username: str) -> str:
    """Return a normalized environment variable key for ``service`` and ``username``."""

    raw = f"{service}_{username}"
    sanitized = re.sub(r"\W", "_", raw)
    if sanitized.strip("_"):
        sanitized = sanitized.lstrip("_")
    else:
        sanitized = "IDENTIFIER"
    safe = sanitized.upper()
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


def _read_secret_from_input(provided: str | None) -> str:
    """Return a secret value from ``provided`` or interactively when ``None``."""

    if provided is not None:
        return provided

    if not sys.stdin.isatty():
        value = sys.stdin.read().rstrip("\n")
        if value:
            return value
        raise SystemExit("No secret data received from stdin.")

    return getpass.getpass("Secret: ")  # pragma: no cover - interactive prompt


SECRET_CMD_STORE = "store"  # nosec B105 - CLI command name  # pragma: allowlist secret
SECRET_CMD_GET = "get"  # nosec B105 - CLI command name  # pragma: allowlist secret
SECRET_CMD_DELETE = "delete"  # nosec B105 - CLI command name  # pragma: allowlist secret


def main(argv: list[str] | None = None) -> None:
    """Run arithmetic and secret management helpers from the command line.

    Parameters
    ----------
    argv:
        Optional list of arguments to parse instead of ``sys.argv``.
    """

    parser = argparse.ArgumentParser(description="Gabriel utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_binary(name: str) -> None:
        sp = subparsers.add_parser(name)
        sp.add_argument("a", type=Decimal)
        sp.add_argument("b", type=Decimal)

    for name in ("add", "subtract", "multiply", "divide", "power", "modulo", "floordiv"):
        add_binary(name)

    sqrt_parser = subparsers.add_parser("sqrt")
    sqrt_parser.add_argument("a", type=Decimal)

    secret_parser = subparsers.add_parser("secret", help="Manage stored secrets")
    secret_subparsers = secret_parser.add_subparsers(dest="secret_command", required=True)

    secret_store = secret_subparsers.add_parser(SECRET_CMD_STORE, help="Store a secret value")
    secret_store.add_argument("service", help="Service identifier for the secret")
    secret_store.add_argument("username", help="Username associated with the secret")
    secret_store.add_argument(
        "--secret",
        dest="secret",
        help="Secret value; reads from stdin or prompts when omitted",
    )

    secret_get = secret_subparsers.add_parser(SECRET_CMD_GET, help="Retrieve a stored secret")
    secret_get.add_argument("service")
    secret_get.add_argument("username")

    secret_delete = secret_subparsers.add_parser(SECRET_CMD_DELETE, help="Delete a stored secret")
    secret_delete.add_argument("service")
    secret_delete.add_argument("username")

    args = parser.parse_args(argv)

    funcs = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
        "power": power,
        "modulo": modulo,
        "floordiv": floordiv,
    }

    if args.command == "sqrt":
        print(sqrt(args.a))
        return

    if args.command == "secret":
        if args.secret_command == SECRET_CMD_STORE:
            secret_value = _read_secret_from_input(args.secret)
            store_secret(args.service, args.username, secret_value)
            print("Secret stored.")
            return
        if args.secret_command == SECRET_CMD_GET:
            retrieved = get_secret(args.service, args.username)
            if retrieved is None:
                raise SystemExit("No secret stored for the requested service/user.")
            print("Secret successfully retrieved. (Value not displayed for security reasons.)")
            return
        if args.secret_command == SECRET_CMD_DELETE:
            delete_secret(args.service, args.username)
            print("Secret deleted.")
            return
        raise SystemExit("Unknown secret command.")  # pragma: no cover - argparse guards choices

    print(funcs[args.command](args.a, args.b))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
