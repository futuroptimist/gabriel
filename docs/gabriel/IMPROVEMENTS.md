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
- [x] Integrate `mypy` into pre-commit for static type checks (`.pre-commit-config.yaml`).
      *Aligns with flywheel best practices.*
- [x] Expand arithmetic helpers with `power` and `modulo` operations
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [x] Add CLI entry points for arithmetic utilities (`pyproject.toml`,
      `gabriel/utils.py`).
- [x] Test `divide` with negative numbers and floats for complete coverage
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [x] Integrate `pip-audit` into pre-commit to detect vulnerable dependencies
      (`.pre-commit-config.yaml`). *Aligns with flywheel best practices.*
- [x] Align Black's `line-length` with repo standard of 100 chars (`pyproject.toml`).
- [x] Support float inputs in arithmetic helpers (`gabriel/utils.py`, `tests/test_utils.py`).
- [x] Add CLI entry points for secret management (`pyproject.toml`, `gabriel/utils.py`).
- [x] Implement `floordiv` helper with test coverage (`gabriel/utils.py`,
      `tests/test_utils.py`).
- [x] Integrate `ruff` linter into pre-commit and CI (`.pre-commit-config.yaml`,
      `.github/workflows/ci.yml`). *Aligns with flywheel best practices.*
- [x] Prototype phishing detection heuristics for suspicious links
      (`gabriel/phishing.py`, `tests/test_phishing.py`).
- [x] Provide a recommendation engine that prioritizes audit findings
      (`gabriel/recommendations.py`, `tests/test_recommendations.py`, `README.md`).
- [x] Add CodeQL workflow for static application security testing
      (`.github/workflows/codeql.yml`). *Aligns with flywheel best practices.*
- [x] Create `SECURITY.md` with vulnerability disclosure guidelines
      (`SECURITY.md`). *Aligns with flywheel best practices.*
- [x] Implement `sqrt` helper with test coverage (`gabriel/utils.py`,
      `tests/test_utils.py`).
- [x] Add `lint` and `test` targets to `Makefile` for developer convenience
      (`Makefile`).
- [x] Provide GitHub issue templates for bugs and features
      (`.github/ISSUE_TEMPLATE/bug_report.yml`,
      `.github/ISSUE_TEMPLATE/feature_request.yml`).
- [x] Expand Dependabot to monitor GitHub Actions updates (`.github/dependabot.yml`).
      *Aligns with flywheel best practices.*
- [x] Add Release Drafter configuration for automated changelog
      (`.github/release-drafter.yml`, `.github/workflows/release-drafter.yml`).
      *Aligns with flywheel best practices.*
- [x] Add `isort` to pre-commit for consistent import ordering
      (`.pre-commit-config.yaml`, `pyproject.toml`).
- [x] Add Python version matrix in CI to test against 3.10 and 3.11
      (`.github/workflows/coverage.yml`, `.github/workflows/ci.yml`).
      *Aligns with flywheel best practices.*
- [x] Create setup script referenced in `runbook.yml` for developer onboarding
      (`runbook.yml`, `scripts/setup.sh`).
- [x] Scan for zero-width characters and hidden text via pre-commit hook
      (`.pre-commit-config.yaml`, `docs/gabriel/THREAT_MODEL.md`, `gabriel/ingestion/text.py`).
      *Aligns with flywheel best practices.*
- [x] Add Jest unit tests for the WebGL viewer (`viewer/viewer.js`, `viewer/__tests__/viewer.test.js`).
- [x] Enforce minimum test coverage in CI using `--cov-fail-under`
      (`pyproject.toml`, `.github/workflows/coverage.yml`).
      *Aligns with flywheel best practices.*
- [x] Add markdown link checker to pre-commit and CI to prevent stale references
      (`.pre-commit-config.yaml`, `.github/workflows/docs.yml`).
      *Aligns with flywheel best practices.*
- [x] Add ESLint to pre-commit for viewer JavaScript
      (`viewer/viewer.js`, `.pre-commit-config.yaml`, `.eslintrc.json`).
      *Aligns with flywheel best practices.*
- [x] Document Docker build and run instructions for local development
      (`docker/Dockerfile`, `README.md`).
- [x] Implement environment variable fallback when `keyring` is unavailable
      (`gabriel/utils.py`, `tests/test_utils.py`). *Aligns with flywheel best practices.*
- [x] Use `decimal.Decimal` in arithmetic helpers to improve precision
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [x] Enable multi-architecture Docker builds for `amd64` and `arm64`
      (`.github/workflows/docker.yml`). *Aligns with flywheel best practices.*
- [x] Run `pre-commit` hooks in CI to ensure local and CI checks match
      (`.github/workflows/ci.yml`, `.pre-commit-config.yaml`). *Aligns with flywheel best practices.*
- [x] Remove duplicate `pip-audit` entries to streamline pre-commit config
      (`.pre-commit-config.yaml`).
- [x] Add `CODEOWNERS` for clear code ownership (`.github/CODEOWNERS`).
      *Aligns with flywheel best practices.*
- [x] Integrate `flake8-docstrings` into pre-commit for docstring style checks
      (`.pre-commit-config.yaml`, `.flake8`). *Aligns with flywheel best practices.*
- [ ] Test on Linux, macOS, and Windows in CI
      (`.github/workflows/coverage.yml`, `.github/workflows/ci.yml`).
- [ ] Add markdown linting to pre-commit for doc style consistency
      (`.pre-commit-config.yaml`, `docs/**`).
      *Aligns with flywheel best practices.*
- [x] Enforce docstring conventions using `pydocstyle` or similar
      (`.pre-commit-config.yaml`, `gabriel/utils.py`).
      *Aligns with flywheel best practices.*
- [x] Cache Python dependencies in CI workflows to improve build times
      (`.github/workflows/ci.yml`, `.github/workflows/coverage.yml`,
      `.github/workflows/docs.yml`).
      *Aligns with flywheel best practices.*
- [ ] Scan Docker images for vulnerabilities during builds
      (`.github/workflows/docker.yml`). *Aligns with flywheel best practices.*
- [x] Format viewer assets with Prettier via pre-commit
      (`viewer/viewer.js`, `.pre-commit-config.yaml`).
- [x] Add pull request template to standardize contributions (`.github/PULL_REQUEST_TEMPLATE.md`).
      *Aligns with flywheel best practices.*
- [ ] Generate API docs with Sphinx and publish under `docs/`
      (`gabriel/utils.py`, `docs/`). *Aligns with flywheel best practices.*
- [ ] Scan Docker images for vulnerabilities in CI using `trivy`
      (`docker/Dockerfile`, `.github/workflows/docker.yml`). *Aligns with flywheel best practices.*
- [x] Define project metadata in `pyproject.toml` for packaging and distribution (`pyproject.toml`,
      `gabriel/__about__.py`). *Aligns with flywheel best practices.*
- [ ] Cache dependencies in GitHub Actions to speed up CI
      (`.github/workflows/ci.yml`, `.github/workflows/coverage.yml`).
- [x] Add Markdown linting to pre-commit and CI (`.pre-commit-config.yaml`, `.github/workflows/docs.yml`).
- [x] Integrate `trufflehog` secret scanning into pre-commit and CI
      (`.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `tests/test_trufflehog_hook.py`).
      *Aligns with flywheel best practices.*
- [x] Add property-based tests using `hypothesis` for arithmetic and secret helpers
      (`tests/test_utils.py`, `requirements.txt`, `gabriel/utils.py`).
      *Aligns with flywheel best practices.*
- [ ] Generate API documentation with `mkdocs` and publish to GitHub Pages
      (`docs/`, `pyproject.toml`, `.github/workflows/docs.yml`).
      *Aligns with flywheel best practices.*
- [ ] Expand Dependabot to monitor Docker base image updates
      (`.github/dependabot.yml`, `docker/Dockerfile`).
      *Aligns with flywheel best practices.*
- [x] Document usage and setup steps for the WebGL viewer
      (`README.md`, `docs/gabriel/VIEWER.md`, `Makefile`).
      *Aligns with flywheel best practices.*
- [ ] Integrate `commitlint` to enforce Conventional Commits
      (`.pre-commit-config.yaml`, `.github/workflows/ci.yml`).
      *Aligns with flywheel best practices.*
- [x] Add `.editorconfig` for consistent editor formatting
      (`.editorconfig`). *Aligns with flywheel best practices.*
- [x] Create `.dockerignore` to reduce Docker build context
      (`.dockerignore`, `docker/Dockerfile`). *Aligns with flywheel best practices.*
- [x] Split arithmetic and secret helpers into dedicated modules
      (`gabriel/utils.py`, `tests/test_utils.py`).
- [x] Add PhotoPrism audit helper covering HTTPS, storage, backups, and plugins
      (`gabriel/selfhosted.py`, `tests/test_selfhosted.py`).
- [ ] Integrate `semgrep` static analysis into pre-commit and CI
      (`.pre-commit-config.yaml`, `.github/workflows/ci.yml`).
      *Aligns with flywheel best practices.*
