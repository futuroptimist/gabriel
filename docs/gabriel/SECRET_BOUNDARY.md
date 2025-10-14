# Secrets Boundary

Gabriel treats credential material, access tokens, memory snippets, and any user-supplied
context as **secrets**. This document explains how those secrets are partitioned across the
four-module architecture, when they may cross process boundaries, and which safeguards gate
outbound requests. The guidance applies to new development as we extract shared interfaces into
`gabriel/common` and migrate features into the `ingestion`, `analysis`, `notify`, and `ui`
packages.

## Inference paths

### Local inference

Local inference keeps prompts and completions on the host. Contributors may wire in engines such
as `llama-cpp-python` or other offline runtimes mentioned in the README without contacting the
network.【F:README.md†L4-L12】 Secrets collected during ingestion stay in-process and must only be
persisted through the `gabriel.common.SecretStore` abstraction (see below). No module should
attempt to bypass the store to reach disk or third-party services.

### token.place relay

When encrypted inference is required, Gabriel talks to a co-hosted token.place relay using the
`TokenPlaceClient`. The client enforces SAFE_MODE egress checks before issuing HTTP requests and
attaches bearer credentials only when configured.【F:gabriel/notify/tokenplace.py†L13-L119】 The relay path
is opt-in: new code must not call token.place unless the operator has explicitly configured the
base URL and API key via the upcoming notifier settings.

## Privacy toggles and runtime configuration

Gabriel ships with SAFE_MODE enabled by default. The flag prevents outbound HTTP requests unless
the target host appears in the local allowlist file, and it can be overridden by setting
`SAFE_MODE=false` in tightly controlled lab environments.【F:gabriel/security/policies/egress_control.py†L35-L113】
The allowlist location defaults to `gabriel/security/policies/allowlist.json`; operators may point
to an alternate JSON file by setting `EGRESS_ALLOWLIST_PATH`.

When SAFE_MODE blocks an attempted request, the policy logs a structured warning so developers can
spot unexpected egress during local testing. Do not add new network integrations without extending
the allowlist or documenting why SAFE_MODE should be disabled for a specific workflow.

## Module responsibilities

- **`gabriel.ingestion`** collects local evidence and secrets under user control. It may depend on
  `gabriel.common.SecretStore` to persist encrypted material and `gabriel.common.InferenceClient`
  to interface with either local inference or the token.place relay.
- **`gabriel.analysis`** receives sanitized records from ingestion or common services. It never reads
  raw secrets directly. Access to encryption keys, credentials, or key management APIs must flow
  through the `gabriel.common.KeyManager` protocol.
- **`gabriel.notify`** prepares outbound alerts and orchestrates relay delivery. It may translate
  between local storage and token.place, but it cannot fetch secrets from ingestion or analysis
  modules; instead, it consumes data provided via `gabriel.common` factories.
- **`gabriel.ui`** surfaces ergonomic entry points such as the CLI and viewer. These tools only
  expose redacted previews of sensitive information and should rely on `gabriel.common` façade
  objects for any stateful interactions.

Each feature module depends on `gabriel.common` rather than importing from its siblings. Legacy
shims like `gabriel.secrets` or `gabriel.tokenplace` remain for compatibility but simply import
from `gabriel.common` and `gabriel.notify` respectively so the boundary stays explicit.

## Who may handle secrets?

Only the following components interact with plaintext secrets:

1. `gabriel.common.SecretStore` implementations and the command-line helpers that invoke them.
2. Ingestion utilities that collect data with explicit user consent before passing it to common
   services for persistence or analysis.
3. Notification adapters that package ciphertext for delivery and require temporary access to
   encryption keys via `gabriel.common.KeyManager`.

Analysis logic, UI layers, and any third-party integrations must consume sanitized data structures
that omit raw secrets. When in doubt, treat the data as confidential and route it through
`gabriel.common` so the right auditing hooks can run.

## Developer checklist

- Review this document before introducing new storage backends or relay code paths.
- Ensure SAFE_MODE remains enabled in production profiles; document any exceptions.
- When adding a dependency on token.place, add explicit configuration switches and update the
  allowlist artifacts so operators can reason about the egress surface.
- Update this file whenever the supported toggles, protocols, or module responsibilities change.
