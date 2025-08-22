import math

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


def store_secret(service: str, username: str, secret: str) -> None:
    """Store ``secret`` in the system keyring.

    Parameters
    ----------
    service:
        The name of the service associated with the secret.
    username:
        The user identifier for the secret.
    secret:
        The secret value to store.

    Raises
    ------
    RuntimeError
        If the ``keyring`` package is not installed.
    """
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - exercised via tests
        raise RuntimeError(
            "The `keyring` package is required to store secrets. "
            "Install it via `pip install keyring`."
        ) from exc

    keyring.set_password(service, username, secret)


def get_secret(service: str, username: str) -> str | None:
    """Retrieve a secret from the system keyring.

    Returns
    -------
    str | None
        The stored secret or ``None`` if no value is found.

    Raises
    ------
    RuntimeError
        If the ``keyring`` package is not installed.
    """
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - exercised via tests
        raise RuntimeError(
            "The `keyring` package is required to retrieve secrets. "
            "Install it via `pip install keyring`."
        ) from exc

    return keyring.get_password(service, username)


def delete_secret(service: str, username: str) -> None:
    """Delete a secret from the system keyring."""
    try:
        import keyring
    except ImportError as exc:  # pragma: no cover - exercised via tests
        raise RuntimeError(
            "The `keyring` package is required to delete secrets. "
            "Install it via `pip install keyring`."
        ) from exc

    keyring.delete_password(service, username)


def main() -> None:
    """CLI entry point for arithmetic helpers."""
    import argparse

    parser = argparse.ArgumentParser(description="Gabriel arithmetic utilities")
    parser.add_argument(
        "operation",
        choices=[
            "add",
            "subtract",
            "multiply",
            "divide",
            "power",
            "modulo",
            "floordiv",
            "sqrt",
        ],
    )
    parser.add_argument("a", type=float)
    parser.add_argument("b", type=float, nargs="?")
    args = parser.parse_args()

    ops = {
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
        "power": power,
        "modulo": modulo,
        "floordiv": floordiv,
        "sqrt": sqrt,
    }

    if args.operation == "sqrt":
        result = ops[args.operation](args.a)
    else:
        if args.b is None:
            parser.error("operation requires two operands")
        result = ops[args.operation](args.a, args.b)

    print(result)


if __name__ == "__main__":
    main()
