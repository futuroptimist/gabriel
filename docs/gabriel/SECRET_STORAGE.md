# Encrypted Secret Storage

Gabriel can store tokens or other secrets using the
[keyring](https://pypi.org/project/keyring/) library. It relies on the
operating system's credential manager and is exposed through the
`gabriel.common.secret_store.KeyringSecretStore` implementation of the
`SecretStore` protocol.

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
``delete_secret`` helpers (which delegate to the default ``SecretStore`` instance)
gracefully fall back to sanitized environment
variables named ``GABRIEL_SECRET_<IDENTIFIER>``. The identifier is derived from
``<SERVICE>`` and ``<USERNAME>`` by converting them to uppercase, replacing each
punctuation character with an underscore, and preserving any trailing
separators so distinct credentials remain unique. This fallback avoids runtime
errors but does not provide encryption, so prefer using ``keyring`` whenever
possible. The library encrypts secrets using the platform's preferred backend
and prevents storing plaintext passwords in the repository or environment
variables.

## CLI Shortcuts

Install the project with `pip` or `uv` and use the bundled CLI to manage
secrets without writing custom scripts:

```bash
gabriel secret store "gabriel" sample-user --secret "my-token"
gabriel secret get "gabriel" sample-user
# Secret successfully retrieved. (Value not displayed for security reasons.)
gabriel secret delete "gabriel" sample-user
```

When a secret value is not provided via `--secret`, the command accepts input
from stdin (e.g. `printf` pipelines) or falls back to an interactive prompt.
The retrieval subcommand deliberately omits the secret value from stdout so that
logs and terminal scrollback do not expose it. Retrieve the secret in scripts
with `gabriel.utils.get_secret` if you need to process the value directly.
