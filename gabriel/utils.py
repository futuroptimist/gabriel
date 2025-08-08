def add(a: int, b: int) -> int:
    """Return the sum of ``a`` and ``b``."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Return the result of ``a`` minus ``b``."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Return the product of ``a`` and ``b``."""
    return a * b


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
    """
    import keyring

    keyring.set_password(service, username, secret)


def get_secret(service: str, username: str) -> str | None:
    """Retrieve a secret from the system keyring.

    Returns ``None`` if no secret is stored for the given ``service`` and ``username``.
    """
    import keyring

    return keyring.get_password(service, username)
