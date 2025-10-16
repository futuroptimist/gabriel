# jobbot3000 Polish Initiative — Snapshot and Delivery Plan

> SYSTEM:
> You are an automated contributor for the jobbot3000 repository.
> PURPOSE:
> Polish jobbot3000 by tightening architecture and hardening the web UX.
> USAGE NOTES:
>
> - Use this prompt for system-level polish spanning backend modules, shared flows, and the
>   web client.

## Snapshot (2025-09-30)

### Services and flows

```mermaid
flowchart LR
    subgraph Scraping
      Providers{{"src/modules/scraping/providers/*"}} -->|jobs| Bus
    end
    CLI[/bin/jobbot.js/] -->|orchestrates| Bus{{"src/shared/events/bus.js"}}
    Bus -->|scraping:jobs:fetch| HTTPClient[
      "src/services/http.js"\n(re-export of shared client)
    ]
    HTTPClient --> FetchRetry[
      "src/shared/http/fetch.js"\nretries + circuit breaker
    ]
    FetchRetry --> ExternalAPIs[(ATS APIs)]
    Bus -->|enrichment:resume:pipeline| ResumePipeline[
      "src/modules/enrichment/pipeline/resume.js"
    ]
    ResumePipeline --> Scoring[
      "src/modules/scoring/index.js"\nscore & shortlist
    ]
    Scoring --> Notifications[
      "src/modules/notifications/index.js"\nalerts & exports
    ]
```

- `src/services/http.js` is a façade over `src/shared/http/client.js` to keep legacy imports stable.
- `createHttpClient` layers default headers, rate limiting, abort handling, and circuit breaker
  hooks.
- `fetchWithRetry` serializes requests per host, performs exponential backoff, and blocks private
  IPs.
- The module event bus wires CLI/web calls to scraping, enrichment, scoring, and notification
  handlers.
- `runResumePipeline` stages resume ingestion into load → normalize → analyze, surfacing metadata
  for scoring.

### UI surface

- **Web server:** `src/web/server.js` and `src/web/config.js` host the Express-style server,
  health checks, and feature toggles.
- **Commands:** `src/web/command-registry.js` plus `src/web/command-adapter.js` validate
  summarize, match, shortlist, listings, analytics, and track payloads.
- **Schemas:** `src/web/schemas.js` centralizes coercion helpers so HTTP payloads land in typed
  objects.
- **Audits:** `src/web/audits.js` streams structured events into `JOBBOT_AUDIT_LOG`, honoring
  redaction middleware.
- **Client flags:** `src/web/config.js` surfaces toggles such as mock scraping and native CLI
  disablement to templates and command adapters.
- **Styling:** Lightweight CSS is embedded in templates; Playwright captures bespoke views
  under `docs/screenshots/*.png`.

HTTP responses map into React-free HTML templates that hydrate command adapters. Feature flags
include `web.nativeCli.enabled`, `scraping.useMocks`, and analytics export redaction toggles.

### Testing coverage

- **Services & HTTP:** `test/services-http.test.js`, `test/http-resilience.test.js`, and
  `test/fetch.test.js` validate retries, circuit breakers, and header shaping.
- **Scoring & pipeline:** `test/scoring.test.js`, `test/resume-pipeline.test.js`, and
  `test/resume.test.js` cover resume normalization. `test/shortlist.test.js` and
  `test/match.test.js` guard shortlist scoring.
- **Web server:** `test/web-server.test.js`, `test/web-server-integration.test.js`, and
  `test/web-config.test.js` cover core routing. `test/web-command-adapter.test.js`,
  `test/web-audits.test.js`, `test/web-health-checks.test.js`, and Playwright-driven
  `test/web-e2e.test.js` ensure commands and audits stay wired.
- **UX assets:** Screenshots live in
  `docs/screenshots/{overview,commands,applications,analytics,audits}.png` to document the
  current flows.

### Security references

- [`SECURITY.md`](https://github.com/futuroptimist/jobbot3000/blob/main/SECURITY.md) captures
  disclosure steps, secret handling, privacy stance, and the September 2025 threat model
  refresh.
- Operational guardrails live in `docs/polish/refactor-plan.md`, `web-operational-playbook.md`,
  and CI workflows under `.github/workflows/*` covering lint, Vitest, Playwright, and CodeQL.

## Refactors

### Module boundaries (Phase 1)

- Move existing `src/modules/*` into `src/modules/{auth,scraping,enrichment,scoring,notifications}`
  while preserving shims in `src/services/*` and `src/pipeline/*`.
- Publish an event-bus compatibility layer so CLI, web, and schedulers can consume modules
  incrementally.
- Feature flag: `modules.v2.enabled` gates the new export surface; shims emit deprecation warnings
  when off.

### Configuration manifest (Phase 2)

- Implement `src/shared/config/manifest.js` that validates `process.env`, enumerates required
  secrets, and emits a typed `Config` object.
- Provide `config.features` toggles for mock vs. real integrations, analytics redaction, and native
  CLI enablement.
- Roll out behind `config.manifest.enabled`; when disabled, the legacy env fallbacks stay active.
- Update web server, CLI bootstrap, and Vitest helpers to consume the manifest and surface missing
  secrets early.

### HTTP resilience (Phase 3)

- Extend `createHttpClient` to accept per-provider retry policies, circuit breaker resets, and
  injectable fetch doubles for tests.
- Promote host queue metrics and breaker states through the event bus for observability.
- Add Vitest suites covering timeout propagation, breaker reopen timings, and mock fetch fallbacks.
- Feature flag: `http.resilience.v2` toggles new behaviors while preserving current retry defaults
  when off.

## Docs & UX

- Publish a Mermaid journey map tracing `jobs:list` → scraping adapters → enrichment → scoring →
  notifications.
- Expand the Configuration Cookbook with manifest examples for local, staging, and self-hosted
  deployments, including feature-flag toggles and secret provisioning checklists.
- Document side-by-side deployment steps (npm scripts, Docker compose, self-hosted runner) so
  operators can harden rollouts.
- After polish ships, capture refreshed Playwright screenshots for job search, application review,
  and notification flows; store under `docs/screenshots/` with dated filenames.

## Security & Privacy

- Install request/response redaction middleware that masks user-provided fields before logging or
  export.
- Emit structured audit logs (JSON lines) for administrative commands, data exports, and config
  changes with retention controls documented in the operational runbook.
- Revisit the threat model by linking the new assessments, documenting residual risks, and aligning
  mitigation owners.
- Ensure secrets enumerated by the config manifest feed into `scripts/scan-secrets.py` and CI secret
  scanners.

## Migration Plan

1. Create `src/modules/` (already scaffolded) and `src/shared/`; move services while keeping
   legacy shims (`src/services/http.js`, `src/fetch.js`, resume pipeline entry) until all consumers
   switch to the manifest-aware modules.
2. Introduce the typed config manifest with a `CONFIG_MANIFEST_ENABLED` flag; document fallback env
   variables and provide sample `.env` migrations in the Configuration Cookbook.
3. Replace direct `fetch` usage with the resilient HTTP client. Instrument retries, rate limiting,
   and circuit breakers with metrics. Extend Vitest coverage before promoting the flag to default.
4. Update docs, flowcharts, and deployment guides to reflect module moves, manifest usage, redaction
   middleware, and audit logging. Archive legacy screenshots alongside refreshed captures.

## Delivery Timeline (targeting 3 sprints)

- **Sprint 1:** Module moves and manifest scaffold. Exit criteria — event bus wiring stable with the
  manifest flag still disabled by default.
- **Sprint 2:** HTTP resilience and security middleware. Exit criteria — retry flag live in
  staging and audit logs retained per policy.
- **Sprint 3:** Docs/UX polish and screenshot refresh. Exit criteria — cookbook published and new
  screenshots linked in README.
