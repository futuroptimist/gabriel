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
- [ ] Add `delete_secret` helper to revoke stored credentials (`gabriel/utils.py`,
      `tests/test_utils.py`). *Aligns with flywheel best practices.*
- [ ] Integrate `mypy` into pre-commit for static type checks (`.pre-commit-config.yaml`).
      *Aligns with flywheel best practices.*
- [ ] Expand arithmetic helpers with `power` and `modulo` operations
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [ ] Add CLI entry points for arithmetic utilities (`pyproject.toml`,
      `gabriel/utils.py`).
- [ ] Test `divide` with negative numbers and floats for complete coverage
      (`gabriel/utils.py`, `tests/test_utils.py`).
