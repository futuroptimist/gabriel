# Secrets Boundary and Inference Paths

Gabriel keeps private material on the user's machine by default. This note clarifies
how we separate secret handling across the codebase, how local inference differs from
relaying prompts through [token.place](https://github.com/futuroptimist/token.place),
and which toggles let operators pick the right privacy posture for their environment.

## Two inference strategies

### Fully local execution

* Load a local model by following [OFFLINE.md](OFFLINE.md). Setting
  `GABRIEL_MODEL_PATH` to a GGUF checkpoint keeps prompts, completions, and telemetry
  on the workstation. No relay credentials are required, and outbound network access
  can remain blocked.
* Safe mode remains enabled. With `SAFE_MODE=true` (the default), the egress policy
  rejects any HTTP/S traffic unless explicitly allowlisted. Local inference works
  without modifying the allowlist because it never opens a socket.

### token.place relay

* Use `gabriel.tokenplace.TokenPlaceClient` for encrypted inference when a
  workstation needs to lean on a stronger GPU. The helper signs requests and enforces
  the egress policy before each HTTP call, so a misconfigured relay cannot bypass
  Gabriel's guard rails.
* The default allowlist already includes `token.place`. Operators running a private
  relay must point `EGRESS_ALLOWLIST_PATH` at a customized JSON file that lists the
  relay host name or IP. Requiring an explicit allowlist entry keeps the boundary
  obvious during audits.
* Provide relay credentials via the system keyring or `GABRIEL_SECRET_<IDENTIFIER>`
  fallbacks using `gabriel.secrets.store_secret`. The client never persists API keys
  outside those helpers.

## Privacy toggles and controls

The following toggles integrate with `EgressControlPolicy` so that whichever inference path is
active, outbound access stays deliberate and observable.

* **SAFE_MODE** (default `true`): Blocks HTTP/S unless the destination is allowlisted. Disable it
  only inside trusted sandboxes used for development.
* **EGRESS_ALLOWLIST_PATH** (default `gabriel/security/policies/allowlist.json`): Points to the
  domains or IPs that safe mode permits. Add self-hosted relay hosts to the JSON document before
  routing traffic their way.
* **GABRIEL_MODEL_PATH** (unset by default): When provided, loads a local GGUF model so inference
  remains offline and secrets never leave the machine.
* **`gabriel secret …` CLI**: Writes relay credentials to the keyring or sanitized environment
  variables when keyring support is unavailable.

## Secrets boundary

Gabriel's refactor concentrates secret-aware code in two places:

* `gabriel/common` (planned) will expose typed interfaces such as `KeyManager` and
  `SecretStore`. Existing helpers in `gabriel/secrets.py` continue to back those
  contracts until the migration lands.
* `gabriel/notify` (planned) will perform alert delivery, persistence, and relay
  integration. `gabriel/tokenplace.py` lives here once the module split is complete.

Modules under `gabriel/ingestion` and `gabriel/analysis` must not read secrets
directly; they depend on `gabriel/common` abstractions instead. `gabriel/ui` only
receives opaque handles returned by those interfaces, keeping API keys, key material,
and encrypted payloads outside the presentation layer.

Until the four-module layout is finalized, treat `gabriel/secrets.py`,
`gabriel/tokenplace.py`, and `gabriel/security/` as the only modules permitted to
handle sensitive values. Pull requests that introduce new secret handling logic must
update this document alongside the implementation.
