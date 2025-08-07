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
```

Install `keyring` with `pip install keyring` if it is not already
available. The library encrypts secrets using the platform's preferred
backend and avoids storing plaintext passwords in the repository or
environment variables.
