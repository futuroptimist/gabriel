---
title: 'Implement Mentioned Feature Prompt'
slug: 'codex-implement'
---

# Implement Mentioned Feature Prompt

> **Note:** This prompt previously circulated as the "Implement Requested Feature Prompt."
> The content remains unchanged; only the file name has been updated.

Type: evergreen · One-click: yes

Use this prompt to bring one of Gabriel's described-but-missing capabilities to life.

```text
SYSTEM:
You are an autonomous dev agent working on the `gabriel` repository.
Honor the root AGENTS.md, README.md, and docs/prompts/codex guidance.
Keep the project healthy by running `pre-commit run --all-files` and
`pytest --cov=gabriel --cov-report=term-missing` before opening a PR.

USER:
1. Scan the codebase and docs for TODOs, "future work", or similar notes that mention
   functionality that has not been implemented yet.
2. Build a list of at least three candidate features, then use a reproducible random
   selection (e.g., `python - <<'PY'` with `random.seed()`)
   to choose one feature to implement.
3. Implement the selected feature with production-quality Python, tests, and docs.
   Update adjacent modules or configs to keep the system coherent.
4. Add or update automated tests that fail before the change and pass after.
5. Update any relevant documentation (README, docs/, runbook) to reflect the new behavior.
6. Run the required checks above and any feature-specific scripts.
7. Summarize the change, list tests executed, and note any follow-up work.

OUTPUT:
Return JSON with `summary`, `tests`, `follow_up`, and `random_seed` fields, then
include the diff in a fenced block.
```

## Usage notes

- Prefer small, deployable slices that keep the trunk green.
- Keep line length ≤ 100 characters and follow PEP 8 style.
- Add docstrings when implementing complex logic or new modules.
- Update docs/gabriel/FAQ.md when introducing new recurring questions.

## Upgrade Prompt

Type: evergreen

Use this prompt to refine the Implement Mentioned Feature prompt.

```text
SYSTEM:
You are an automated contributor for the `gabriel` repository.
Follow AGENTS.md and README.md conventions.
Ensure `pre-commit run --all-files` and `pytest --cov=gabriel --cov-report=term-missing`
pass before committing.

USER:
1. Review this prompt for accuracy and clarity.
2. Update instructions, links, or formatting to match current repository practices.
3. Verify examples and command references remain valid.
4. Update related prompt indexes (e.g., docs/prompts/codex/README.md) if the summary changes.
5. Run the required checks above.

OUTPUT:
A pull request with the improved prompt doc and passing checks.
```
