# Suggested Improvements for Gabriel

This document lists potential enhancements uncovered during a self-audit of the Gabriel codebase.

## Checklist

- [ ] Implement `flake8` and `bandit` in CI to catch style and security issues.
- [x] Expand unit tests beyond the simple `add` function.
- [ ] Provide examples of encrypted secret storage using `keyring`.
- [ ] Document how to run Gabriel completely offline with local models.
- [x] Harden pre-commit hooks to prevent accidental secret leaks.
