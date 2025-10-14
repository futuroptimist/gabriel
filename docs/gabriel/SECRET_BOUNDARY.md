# Secrets Boundary

Gabriel keeps credentials and other sensitive material within a narrow trust boundary. This
document explains how local inference differs from token.place relaying, which privacy toggles
you can enable, and which modules are allowed to handle secrets.

## Local inference path

When local inference is enabled, prompts and completions never leave the host. Components inside
`gabriel/analysis` and `gabriel/ui` communicate through the abstractions published by
`gabriel/common` so that only vetted adapters touch plaintext data. Secrets are persisted via the
`SecretStore` protocol, which defaults to the environment-aware
`KeyringSecretStore`. The implementation stores credentials in the platform keyring when the
[`keyring`](https://pypi.org/project/keyring/) package is installed and falls back to sanitized
`GABRIEL_SECRET_<IDENTIFIER>` variables during development. Local inference runs entirely offline
and is the safest choice when network egress must be avoided.

## Token.place relay

Token.place relaying allows Gabriel to delegate inference to a hardened remote enclave. The
`gabriel/tokenplace.py` adapter encrypts prompts before transmission and decrypts responses once
returned. Encryption keys are delivered through the `KeyManager` and `EnvelopeEncryptor` protocols
in `gabriel/common`, keeping the integration decoupled from the feature modules. Secrets required to
authenticate with token.place are stored using the same `SecretStore` instance, making it obvious
when credentials cross the trust boundary.

## Privacy toggles

Users can explicitly choose between local inference and token.place relaying at runtime. CLI shims
and UI flows must surface these toggles so no secret or prompt leaves the device unintentionally.
Feature code **must not** bypass the `gabriel/common` interfaces when switching modes; doing so
would skip validation hooks that enforce encryption and audit logging.

## Authorized secret handlers

Only the following modules are permitted to work with plaintext secrets:

- `gabriel/common/secret_store.py` and its re-exports in `gabriel/secrets.py`
- `gabriel/tokenplace.py` when preparing encrypted payloads
- Persistence adapters that implement the `SecretStore` protocol for sanctioned backends

Feature modules in `gabriel/ingestion`, `gabriel/analysis`, and `gabriel/notify` consume secrets
indirectly by depending on the `SecretStore` protocol. This boundary keeps credential handling
reviewable and reduces the risk of accidental leakage.
