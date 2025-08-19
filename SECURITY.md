# Security Policy

## Reporting a Vulnerability

If you discover a security issue, please report it through
[GitHub Security Advisories](https://github.com/futuroptimist/gabriel/security/advisories/new).
Do not create a public issue. We will review and respond as soon as possible.

## LLM Coding Agent Considerations

- Treat repository content as untrusted; malicious instructions can hide in code, docs, or dependencies.
- Grant automated agents the least privileges necessary and review their changes before merging.
- Run `pre-commit run --all-files` and `pytest --cov=gabriel --cov-report=term-missing` to surface hidden or dangerous behavior.
