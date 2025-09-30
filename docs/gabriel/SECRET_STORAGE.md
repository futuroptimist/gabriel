# Encrypted Secret Storage

Gabriel can store tokens or other secrets using the
[keyring](https://pypi.org/project/keyring/) library. It relies on the
operating system's credential manager.

## Example

```python
import keyring

SERVICE = "gabriel"
USERNAME = "sample-user"

def save_token(token: str) -> None:
    """Save token to the system keyring."""
    keyring.set_password(SERVICE, USERNAME, token)

def load_token() -> str | None:
    """Retrieve token from the system keyring."""
    return keyring.get_password(SERVICE, USERNAME)

def delete_token() -> None:
    """Remove token from the system keyring."""
    keyring.delete_password(SERVICE, USERNAME)
```

Install `keyring` with `pip install keyring` if it is not already available.
When the package is missing, Gabriel's ``store_secret``, ``get_secret``, and
``delete_secret`` helpers gracefully fall back to sanitized environment
variables named ``GABRIEL_SECRET_<IDENTIFIER>``. The identifier is derived from
``<SERVICE>`` and ``<USERNAME>`` by uppercasing them, collapsing punctuation to
single underscores, and trimming leading or trailing separators to prevent
unstable keys. This fallback avoids runtime errors but does not provide
encryption, so prefer using ``keyring`` whenever possible. The library encrypts
secrets using the platform's preferred backend and prevents storing plaintext
passwords in the repository or environment variables.
