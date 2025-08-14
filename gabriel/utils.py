def add(a: int, b: int) -> int:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Return the result of ``a`` minus ``b``."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Return the product of ``a`` and ``b``."""
    return a * b


def divide(a: float | int, b: float | int) -> float:
    """Return the result of ``a`` divided by ``b``.

    Supports both integers and floats.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def power(a: int, b: int) -> int:
    """Return ``a`` raised to the power of ``b``."""
    return a**b


def modulo(a: int, b: int) -> int:
    """Return ``a`` modulo ``b``."""
    if b == 0:
        raise ZeroDivisionError("Cannot modulo by zero.")
    return a % b


def floordiv(a: int, b: int) -> int:
    """Return the floor division of ``a`` by ``b``."""
    if b == 0:
        raise ZeroDivisionError("Cannot floor divide by zero.")
    return a // b


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
