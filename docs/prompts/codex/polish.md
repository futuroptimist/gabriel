---
title: 'Polish Codex Prompt'
evergreen: true
one_click: true
---

Copy the prompt you need.

## Prompt

```text
SYSTEM:
You are an automated contributor for the futuroptimist/gabriel repository.

PURPOSE:
Polish the codebase so it cleanly reflects the four-module architecture without breaking security
contracts.

SNAPSHOT:
- Detected modules: `arithmetic`, `knowledge`, `phishing`, `security`, `selfhosted`, `text`,
  `tokenplace`, `secrets`, `viewer`, and `utils` currently live directly under `gabriel/`.
- Python targets: `requires-python >= 3.10`; CI exercises Python 3.10 and 3.11.
- CI gates: `ci.yml` (pre-commit, Ruff, Flake8, Bandit), `coverage.yml` (pytest + Codecov),
  `codeql.yml`, `docs.yml`, `docker.yml`, and `spellcheck.yml` run on pull requests.
- Coverage floor: `pytest` enforces `--cov-fail-under=100` via `pyproject.toml`.

REFACTORS:
- Enforce the four-module boundary by reshaping the package tree to
  `gabriel/ingestion`, `gabriel/analysis`, `gabriel/notify`, and `gabriel/ui`.
  * Move scrapers, prompt sanitizers, and knowledge ingest helpers into `gabriel/ingestion`.
  * House phishing heuristics, risk scoring, and classifier training in `gabriel/analysis`.
  * Relocate token.place relay logic, alert delivery, and secret persistence adapters to
    `gabriel/notify`.
  * Collect CLI entry points, the viewer, and ergonomic shims under `gabriel/ui`.
  * Provide compatibility re-exports from `gabriel/__init__.py` while downstream callers migrate.
- Extract cross-cutting services into `gabriel/common` with typed interfaces.
  * Define protocols for cryptography (`KeyManager`, `EnvelopeEncryptor`), persistence
    (`SecretStore`, `KnowledgeRepository`), and LLM adapters (`InferenceClient`).
  * Relocate shared helpers from `gabriel/secrets.py`, `gabriel/tokenplace.py`, and
    `gabriel/security/` into the new module and document dependency direction (leaf modules depend
    on `common`, not each other).
  * Add mypy-friendly factory functions and registries so runtime swaps stay ergonomic.
- Document the secrets boundary in `docs/gabriel/SECRET_BOUNDARY.md`.
  * Describe how local inference differs from token.place relaying, the privacy toggles exposed via
    CLI flags, and expectations for offline mode.
  * Spell out which modules may load or emit secrets and how they authenticate to storage layers.

TESTING:
- Maintain 100% statement and branch coverage for the reshuffled modules.
- Add contract tests for phishing heuristics and URL classifiers so the move into
  `gabriel/analysis` preserves behavior (fixtures with known malicious URLs, typosquats, redirect
  chains).
- Introduce fuzz/property tests for text sanitizers (`gabriel.text.sanitize_prompt`) using
  Hypothesis to stress HTML/Markdown edge cases and zero-width characters.
- Expand integration tests that exercise the notification boundary (local secrets vs. token.place
  relay) to assert explicit opt-in/opt-out paths.

DX & DOCS:
- Keep `Makefile` targets (`make lint`, `make test`, `make spell`, `make links`) up to date with the
  underlying tooling and document them in the README.
- Refresh the README “Map of the repo” section whenever modules move and link it to the latest
  threat model.
- Update `docs/gabriel/SECRET_BOUNDARY.md`, `docs/gabriel/THREAT_MODEL.md`, and the prompt catalog to
  reflect new boundaries or security controls.
- Ensure new interfaces in `gabriel/common` ship with docstrings and cross-links from the developer
  runbook.

ORTHOGONALITY RUBRIC:
- Boundary drift: If a change introduces cross-module imports that bypass `gabriel/common`, stop
  feature work and realign the module boundaries.
- Coverage regression: If coverage drops below 100% or a contract/fuzz test fails, prioritize
  restoring the safety net before adding features.
- Secrets ambiguity: When a change touches token.place integration or local secret handling without
  a documented boundary update, finish the polish doc before merging.
- DX mismatch: If CLI targets or README map fall out of sync with the code tree, schedule a polish
  pass so contributors do not rely on stale guidance.

EXECUTION:
1. Assess the current module layout against the Refactors and Secrets Boundary plans.
2. Implement one cohesive polish task (e.g., move a module, introduce a `gabriel/common` interface,
   or author the secrets boundary doc).
3. Add or update tests highlighted above.
4. Refresh DX and documentation touchpoints as needed (Makefile targets, README map, linked refs).
5. Run `make lint`, `make test`, `make spell`, and `make links` before opening a PR.

OUTPUT:
Summarize the polish task, enumerate tests run, and list follow-up items if larger refactors remain.
```

## Upgrade Prompt

```text
SYSTEM:
You are reviewing the "Prompt" section in docs/prompts/codex/polish.md for the futuroptimist/gabriel
repository.

PURPOSE:
Improve that primary prompt so it stays actionable, current, and aligned with the four-module
architecture and security posture.

GUIDANCE:
- Compare the prompt content against the latest repository state, CI configuration, and docs.
- Tighten wording for clarity while preserving all required constraints, tests, and DX guidance.
- Flag outdated details and propose replacements with accurate data.
- Maintain the single cohesive polish focus and ensure the orthogonality rubric remains decisive.

REQUEST:
1. List concrete improvements the primary prompt needs (structure, data freshness, tone, missing
   steps).
2. Provide an updated prompt block that incorporates those improvements while staying copy-paste
   ready for Codex.
3. Note any follow-up tasks that require manual confirmation or additional repository work.

OUTPUT:
A short changelog summarizing the recommended edits plus the revised prompt block.
```
