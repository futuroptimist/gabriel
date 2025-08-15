# Suggested Improvements for Gabriel

This document lists potential enhancements uncovered during a self-audit of the Gabriel codebase.

## Checklist

- [x] Implement `flake8` and `bandit` in CI to catch style and security issues.
- [x] Expand unit tests beyond the simple `add` function.
- [x] Add unit tests for negative numbers in arithmetic helpers.
- [x] Provide examples of encrypted secret storage using `keyring` ([SECRET_STORAGE.md](SECRET_STORAGE.md)).
- [x] Document how to run Gabriel completely offline with local models. See [OFFLINE.md](OFFLINE.md).
- [x] Harden pre-commit hooks to prevent accidental secret leaks.
- [x] Add `multiply` helper with test coverage.
- [x] Add `delete_secret` helper to remove stored secrets.
- [ ] Integrate `mypy` into pre-commit for static type checks (`.pre-commit-config.yaml`).
      *Aligns with flywheel best practices.*
- [x] Expand arithmetic helpers with `power` and `modulo` operations
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [ ] Add CLI entry points for arithmetic utilities (`pyproject.toml`,
      `gabriel/utils.py`).
- [x] Test `divide` with negative numbers and floats for complete coverage
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [ ] Integrate `pip-audit` into pre-commit to detect vulnerable dependencies
      (`.pre-commit-config.yaml`). *Aligns with flywheel best practices.*
- [x] Align Black's `line-length` with repo standard of 100 chars (`pyproject.toml`).
- [ ] Support float inputs in arithmetic helpers (`gabriel/utils.py`, `tests/test_utils.py`).
- [ ] Add CLI entry points for secret management (`pyproject.toml`, `gabriel/utils.py`).
- [x] Implement `floordiv` helper with test coverage (`gabriel/utils.py`,
      `tests/test_utils.py`).
- [ ] Integrate `ruff` linter into pre-commit and CI (`.pre-commit-config.yaml`,
      `.github/workflows/ci.yml`). *Aligns with flywheel best practices.*
- [ ] Add CodeQL workflow for static application security testing
      (`.github/workflows/codeql.yml`). *Aligns with flywheel best practices.*
- [ ] Create `SECURITY.md` with vulnerability disclosure guidelines
      (`SECURITY.md`). *Aligns with flywheel best practices.*
- [x] Implement `sqrt` helper with test coverage (`gabriel/utils.py`,
      `tests/test_utils.py`).
- [ ] Add `lint` and `test` targets to `Makefile` for developer convenience
      (`Makefile`).
- [ ] Provide GitHub issue templates for bugs and features
      (`.github/ISSUE_TEMPLATE/bug_report.yml`,
      `.github/ISSUE_TEMPLATE/feature_request.yml`).
- [ ] Expand Dependabot to monitor GitHub Actions updates (`.github/dependabot.yml`).
      *Aligns with flywheel best practices.*
- [ ] Add Release Drafter configuration for automated changelog
      (`.github/release-drafter.yml`). *Aligns with flywheel best practices.*
- [ ] Add `isort` to pre-commit for consistent import ordering
      (`.pre-commit-config.yaml`, `pyproject.toml`).
- [ ] Add Python version matrix in CI to test against 3.10 and 3.11
      (`.github/workflows/coverage.yml`, `.github/workflows/ci.yml`).
      *Aligns with flywheel best practices.*
- [ ] Create setup script referenced in `runbook.yml` for developer onboarding
      (`runbook.yml`, `scripts/setup.sh`).
