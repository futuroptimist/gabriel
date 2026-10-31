# GitHub Copilot Instructions for Gabriel

This repository contains **Gabriel**, a local-first security companion offering actionable security advice, phishing detection, and hardening guidance for self-hosted services.

## Core Principles

- **Privacy First**: Prioritize user privacy and security. Avoid analytics or network calls unless explicitly discussed.
- **Local Inference**: Support both local LLM inference (via llama-cpp-python) and encrypted relay through token.place.
- **Minimal Dependencies**: Use lightweight Python 3.10+ dependencies. Document all new dependencies in `requirements.txt`.

## Development Guidelines

### Language and Version

- Python 3.10 or later is required (CI tests both 3.10 and 3.11)
- All code must be compatible with Python 3.10+
- Use type hints for function signatures

### Code Style

- Follow PEP8 style guidelines
- Use meaningful variable and function names
- Include docstrings for all public functions, classes, and modules (follow PEP257 conventions)
- Line length: 100 characters (configured in black and ruff)
- Use `black` for code formatting
- Use `ruff` for linting (configured in `pyproject.toml`)
- Import sorting with `isort` (black profile)

### Testing Requirements

- All code changes must include tests
- Target: 100% test coverage (pytest enforces this)
- Write tests using `pytest`
- Tests should be minimal and focused
- Run tests before committing:

  ```bash
  pytest --cov=gabriel --cov-report=term-missing
  ```

- Use `hypothesis` for property-based testing where appropriate
- Never remove or modify existing tests unless fixing broken functionality

### Security Practices

- Run `bandit` to catch security issues before committing
- Use `detect-secrets` to prevent credential leakage
- Run `semgrep` with local rules in `config/semgrep/rules.yaml`
- All security-sensitive operations should be reviewed carefully
- Secrets management uses system keyring (see `gabriel.common` module)
- Validate all user inputs, especially for LLM prompts (use `sanitize_prompt`)

### Documentation

- Update `README.md` for any user-facing changes
- Update documentation in `docs/` for architectural or design changes
- Keep docstrings up-to-date with code changes
- Add new questions to `docs/gabriel/FAQ.md` rather than removing existing ones
- All documentation must pass spell checking (`pyspelling`)
- Use Markdown link checker (`lychee`) to validate links

### Pre-commit Hooks

- Run `pre-commit run --all-files` before committing
- Pre-commit hooks include:
  - `flake8` and `pydocstyle` for style
  - `bandit` for security
  - `detect-secrets` and `trufflehog` for credential scanning
  - `ruff` for linting
  - `black` and `prettier` for formatting
  - `mypy` for type checking
  - `pymarkdown` for markdown linting
  - `eslint` for JavaScript (viewer code)

### Commit Messages

- Follow [Conventional Commits](https://www.conventionalcommits.org/) specification
- Format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`
- CI validates commit messages with `commitlint`

## Project Structure

### Module Organization (Four-Module Architecture)

The project is organized into four main modules:

1. **Ingestion** (`gabriel/ingestion/`) - Data collection and normalization
2. **Analysis** (`gabriel/analysis/`) - Security analysis, phishing detection, policy validation
3. **Notification** (`gabriel/notify/`) - Alerts and encrypted delivery
4. **User Interface** (`gabriel/ui/`) - CLI and viewer surfaces

### Key Modules

- `gabriel/common/` - Shared primitives (cryptography, persistence, LLM adapters)
- `gabriel/security/` - Security-focused utilities (egress control, token analysis)
- `gabriel/selfhosted/` - Audit helpers for self-hosted services (VaultWarden, Docker, Syncthing, Nextcloud, PhotoPrism)
- `gabriel/arithmetic.py` - Decimal-based arithmetic helpers
- `gabriel/knowledge.py` - Personal knowledge store for security notes

### Backward Compatibility

- Compatibility shims exist in root module (`gabriel/phishing.py`, `gabriel/policy.py`, etc.)
- Maintain these shims when moving code to new locations
- Don't break existing imports without coordination

## Common Tasks

### Adding New Dependencies

1. Add to `requirements.txt`
2. Document why the dependency is needed
3. Prefer lightweight, well-maintained packages
4. Avoid dependencies that make network calls unless essential

### Adding New Features

1. Start with tests (TDD approach preferred)
2. Implement minimal changes to pass tests
3. Update relevant documentation
4. Run full test suite and pre-commit hooks
5. Update `README.md` with usage examples if user-facing

### Fixing Bugs

1. Add a failing test that reproduces the bug
2. Fix the bug with minimal changes
3. Verify the test passes
4. Run full test suite to ensure no regressions

### Security Audits

- New audit helpers should follow the pattern in `gabriel/selfhosted/`
- Return findings only (empty list for hardened configurations)
- Include severity, message, and remediation guidance
- See existing auditors (VaultWarden, Docker, Syncthing, etc.) as examples

## Specific Guidelines

### Phishing Detection

- Add heuristics to `gabriel/analysis/phishing.py`
- Each heuristic should have a clear severity level (low, medium, high, critical)
- Include remediation guidance in findings
- Test with both malicious and benign URLs

### LLM Prompts

- Always sanitize user-provided prompts with `sanitize_prompt`
- Strip HTML, Markdown images, and zero-width characters
- Never expose raw prompt text in logs
- Consider OWASP LLM01-LLM10 vulnerabilities

### Knowledge Store

- Store security notes locally (no cloud sync without consent)
- Use Markdown format for notes
- Support tagging and keyword search
- Keep indexes ephemeral (rebuild from source files)

### Vector Embeddings

- Enforce repository-scoped API key prefixes
- Maximum TTL: 7 days (`MAX_VECTOR_TTL`)
- Include task IDs for cleanup
- Use `SecureVectorStore` class for access control

## Testing

### Test Organization

- Tests live in `tests/` directory
- Mirror source structure (e.g., `tests/security/` for `gabriel/security/`)
- Name test files `test_*.py`
- Use descriptive test function names: `test_<functionality>_<expected_behavior>`

### Coverage Requirements

- 100% coverage required (CI enforces this)
- No uncovered lines allowed without good reason
- Use `# pragma: no cover` sparingly and only when justified
- Coverage reports generated in XML for CI integration

### Test Best Practices

- Use fixtures for common setup
- Mock external dependencies (network, filesystem where appropriate)
- Test edge cases and error conditions
- Use parameterized tests for multiple similar cases
- Keep tests focused and independent

## Pull Request Guidelines

1. Reference relevant issues in PR description
2. Include screenshots for UI changes
3. Complete the PR template checklist
4. Address prompt-injection review checklist (OWASP LLM01-LLM10)
5. Keep PRs focused on a single concern
6. Include citations for security-related changes
7. Ensure all CI checks pass

## Resources

- [AGENTS.md](../AGENTS.md) - Repository-specific automation rules
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [README.md](../README.md) - Project overview and usage
- [docs/gabriel/THREAT_MODEL.md](../docs/gabriel/THREAT_MODEL.md) - Security threat model
- [docs/gabriel/ROADMAP.md](../docs/gabriel/ROADMAP.md) - Project roadmap
- [docs/gabriel/FAQ.md](../docs/gabriel/FAQ.md) - Frequently asked questions

## CI/CD

- GitHub Actions workflows in `.github/workflows/`
- Workflows: `ci.yml`, `coverage.yml`, `docs.yml`, `security.yml`, `codeql.yml`
- Security scans run weekly on Mondays at 06:00 UTC
- Dependabot monitors Python deps, Actions, and Docker images weekly
- Release notes auto-drafted via `release-drafter`

## Common Pitfalls to Avoid

- Don't add analytics or telemetry without explicit discussion
- Don't make network calls to untrusted destinations
- Don't store secrets in code (use keyring integration)
- Don't lower test coverage
- Don't break backward compatibility without coordination
- Don't skip security scans (bandit, semgrep, detect-secrets)
- Don't commit without running pre-commit hooks
- Don't modify `.github/agents/` directory (reserved for agent configurations)

## Quick Reference Commands

```bash
# Setup environment
./scripts/setup.sh

# Run tests
pytest --cov=gabriel --cov-report=term-missing

# Lint and format
pre-commit run --all-files

# Spell check
pyspelling -c .spellcheck.yaml

# Build docs
mkdocs serve

# Validate policy
./scripts/validate_policy.py path/to/llm_policy.yaml

# Common make targets
make lint   # run pre-commit checks
make test   # run test suite with coverage
make spell  # run spell checker
make links  # scan documentation links
make docs   # build static site
```
