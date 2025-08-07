# Suggested Improvements for Gabriel

This document lists potential enhancements uncovered during a self-audit of the Gabriel codebase.

## Checklist

- [x] Implement `flake8` and `bandit` in CI to catch style and security issues.
- [x] Expand unit tests beyond the simple `add` function.
- [x] Add unit tests for negative numbers in arithmetic helpers.
- [x] Provide examples of encrypted secret storage using `keyring` ([SECRET_STORAGE.md](SECRET_STORAGE.md)).
- [x] Document how to run Gabriel completely offline with local models. See [OFFLINE.md](OFFLINE.md).
- [x] Harden pre-commit hooks to prevent accidental secret leaks.
