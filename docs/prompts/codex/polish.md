---
title: 'Polish Four-Module Architecture'
evergreen: true
one_click: true
---

Copy the prompt you need.

## Prompt

```text
SYSTEM:
You are an automated contributor working on the futuroptimist/gabriel repository.

PURPOSE:
Polish the codebase so it cleanly reflects the four-module architecture while
preserving security controls and contributor ergonomics.

SNAPSHOT:
- Core heuristics now live in `gabriel/analysis/` (`phishing.py`, `policy.py`,
  `recommendations.py`) with compatibility shims left in place for
  downstream callers. Remaining top-level modules include `arithmetic.py`,
  `knowledge.py`, `prompt_lint.py`, `security/`, `secrets.py`, `selfhosted.py`,
  `text.py`, `tokenplace.py`, `utils.py`, and `viewer.py`.
- Python targets: `pyproject.toml` declares `requires-python >= 3.10`; CI runs on
  Python 3.10 and 3.11.
- CI gates: `ci.yml` (lint + tests), `coverage.yml`, `codeql.yml`, `docs.yml`,
  `docker.yml`, and `spellcheck.yml` run on pull requests.
- Coverage floor: pytest is configured with `--cov-fail-under=100`.

REFACTORS:
- Enforce the four-module boundary by reshaping the package tree into
  `gabriel/ingestion`, `gabriel/analysis`, `gabriel/notify`, and `gabriel/ui`.
  * Move scrapers, prompt sanitizers, and knowledge ingest helpers into
    `gabriel/ingestion`.
  * Consolidate phishing heuristics, risk scoring, classifiers, and policy logic
    within `gabriel/analysis`.
  * Relocate token.place relay code, alert delivery, and persistence adapters to
    `gabriel/notify`.
  * House CLI entry points, the viewer, and ergonomic shims inside `gabriel/ui`.
  * Provide compatibility re-exports in `gabriel/__init__.py` while downstream
    callers migrate.
- Extract shared services into `gabriel/common` with typed interfaces.
  * Define protocols for cryptography (e.g., `KeyManager`, `EnvelopeEncryptor`),
    persistence (`SecretStore`, `KnowledgeRepository`), and LLM adapters
    (`InferenceClient`).
  * The default secret store now lives in `gabriel/common/secret_store.py` and
    re-exports compatibility shims through `gabriel/secrets.py`.
  * Move cross-cutting helpers from `gabriel/secrets.py`, `gabriel/tokenplace.py`,
    `gabriel/security/`, and similar modules into the new package. Document that
    feature modules depend on `common`, not on each other.
  * Publish factory functions and registries that keep runtime swaps ergonomic
    and mypy-friendly.
- Author `docs/gabriel/SECRET_BOUNDARY.md` to explain how local inference differs
  from token.place relaying, which privacy toggles exist, and which modules are
  permitted to handle secrets.

TESTING:
- Maintain 100% statement and branch coverage after every move.
- Add contract tests for phishing heuristics and URL classifiers when migrating
  into `gabriel/analysis` to ensure detections remain stable.
- Introduce fuzz/property tests for text sanitizers (e.g., `gabriel.ingestion.text.
  sanitize_prompt`) to cover HTML/Markdown edge cases and zero-width characters.
- Extend integration tests that straddle notification boundaries so local secret
  storage vs. token.place relay paths remain explicit and opt-in.

DX & DOCS:
- Ensure the CLI targets `make lint`, `make test`, `make spell`, and `make links`
  stay wired to the correct tooling and document them in the README.
- Maintain a README "Map of the repo" that mirrors the four-module layout and
  links to the threat model.
- Update the developer runbook and prompt catalog whenever interfaces or module
  boundaries shift, including `gabriel/common` abstractions and the secrets
  boundary doc.

ORTHOGONALITY RUBRIC:
- Boundary drift: Stop feature work if code bypasses `gabriel/common` to reach
  another module directly.
- Coverage regression: Restore 100% coverage or fix failing contract/fuzz tests
  before adding new features.
- Secrets ambiguity: If changes touch token.place or local secret handling
  without updating `docs/gabriel/SECRET_BOUNDARY.md`, finish the polish work
  first.
- DX mismatch: Realign docs and Makefile targets whenever they fall out of sync
  with the code tree.

EXECUTION:
1. Audit the current layout against the refactor goals and secrets boundary
   expectations.
2. Ship one cohesive polish slice (module relocation, interface extraction, or
   secrets documentation) at a time.
3. Add or update the tests listed above alongside the code changes.
4. Refresh the README, secrets boundary doc, and prompt catalog so contributors
   have accurate guidance.
5. Run `make lint`, `make test`, `make spell`, and `make links` before opening a
   pull request.

OUTPUT:
Summarize the polish task, list tests executed, and note any follow-up polish
work that remains.
```

## Upgrade Prompt

```text
SYSTEM:
You are reviewing the "Prompt" section in docs/prompts/codex/polish.md for the
futuroptimist/gabriel repository.

PURPOSE:
Keep the polish prompt current with the repository's four-module architecture
and security posture.

GUIDANCE:
- Compare the prompt against the latest code layout, CI configuration, and docs.
- Tighten language for clarity without dropping required constraints, tests, or
  DX guidance.
- Flag stale details and supply replacements backed by repository evidence.
- Preserve the orthogonality rubric so it continues to signal when polish work
  should preempt new features.

REQUEST:
1. List concrete improvements the primary prompt needs (structure, data
   freshness, tone, missing steps).
2. Provide an updated prompt block that incorporates those improvements while
   remaining copy-paste ready for Codex.
3. Record follow-up tasks that need manual confirmation or extra repository
   changes.

OUTPUT:
Return a concise changelog that summarizes the recommended edits and includes
the revised prompt block.
```
