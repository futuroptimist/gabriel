# Gabriel

Gabriel is an open source "guardian angel" LLM aimed at helping individuals securely navigate the digital world. The project intends to provide actionable security advice, maintain personal knowledge about the user's environment (with their consent), and eventually offer local AI-assisted monitoring. Our guiding principle is to keep user data private and handle AI inference locally. When possible we rely on [token.place](https://github.com/futuroptimist/token.place) for encrypted inference, though a fully offline path using components like `llama-cpp-python` is also supported.

[![Lint & Format](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/ci.yml?label=lint%20%26%20format)](https://github.com/futuroptimist/gabriel/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/coverage.yml?label=tests)](https://github.com/futuroptimist/gabriel/actions/workflows/coverage.yml)
[![Coverage](https://raw.githubusercontent.com/futuroptimist/gabriel/main/coverage.svg)](https://codecov.io/gh/futuroptimist/gabriel)
[![Docs](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/docs.yml?label=docs&branch=main)](https://github.com/futuroptimist/gabriel/actions/workflows/docs.yml)
[![License](https://img.shields.io/github/license/futuroptimist/gabriel)](LICENSE)

## Goals

- Offer community-first, dignity-focused security guidance.
- Integrate with token.place or fully local inference to avoid cloud exfiltration.
- Encourage collaboration with [token.place](https://github.com/futuroptimist/token.place) and [sigma](https://github.com/futuroptimist/sigma) as complementary projects.
- Provide a gentle on-ramp toward eventual real-world monitoring capabilities.

For a philosophical look at these goals through the lens of the "Sword of Damocles" parable, see [SWORD_OF_DAMOCLES.md](docs/gabriel/SWORD_OF_DAMOCLES.md).

## Architecture Overview

The project is organized into four tentative modules:

1. **Ingestion** – scripts or agents that collect user-consented data.
2. **Analysis** – LLM-based logic for assessing security posture.
3. **Notification** – optional alerts or recommendations sent to the user.
4. **User Interface** – CLI or lightweight UI for interacting with Gabriel.

This modular structure keeps responsibilities clear and allows future extensions like phishing detection or network monitoring.

## Getting Started

Gabriel requires Python 3.10 or later. Clone the repository and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
pre-commit install
```

Run `pytest` with coverage enabled:

```bash
python -m pytest --cov=gabriel --cov-report=term-missing
```

Common tasks are available via the `Makefile`:

```bash
make lint  # run pre-commit checks
make test  # run the test suite with coverage
```

Example usage of arithmetic helpers:

These helpers accept both integers and floats.

```python
from gabriel import add, multiply, divide, power, modulo, floordiv
print(add(2.5, 3.5))  # 6.0
print(divide(multiply(add(2, 3), 4), 2))  # 10.0
print(power(2, 3))  # 8
print(modulo(7, 3))  # 1
print(floordiv(7, 2))  # 3
print(sqrt(9))  # 3.0
```

### Offline Usage

For fully local inference, see [OFFLINE.md](docs/gabriel/OFFLINE.md).

For storing secrets in the system keyring, see
[docs/gabriel/SECRET_STORAGE.md](docs/gabriel/SECRET_STORAGE.md).

### Runbook & 3D Viewer

This repo now mirrors flywheel's development helpers. `runbook.yml` lists
typical tasks and `viewer/` hosts a basic `model-viewer` scene. The viewer bundles a
local copy of the `@google/model-viewer` library to avoid third-party requests,
and animations start only after pressing **Start Animation**. Launch
`make preview` to open the viewer locally.

## Tracked Repositories

The table below summarizes all repositories where we currently maintain
improvement tasks or security audits. Following these links will jump to the
relevant documentation.

| Repository | Improvement Docs | Threat Model |
|------------|-----------------|--------------|
| Gabriel (this repo) | [IMPROVEMENTS.md](docs/gabriel/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/gabriel/THREAT_MODEL.md) |
| token.place | [IMPROVEMENTS.md](docs/related/token_place/IMPROVEMENTS.md) | N/A |
| DSPACE | [IMPROVEMENTS.md](docs/related/dspace/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/dspace/THREAT_MODEL.md) |
| flywheel | [IMPROVEMENTS.md](docs/related/flywheel/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/flywheel/THREAT_MODEL.md) |
| f2clipboard | [IMPROVEMENTS.md](docs/related/f2clipboard/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/f2clipboard/THREAT_MODEL.md) |
| axel | [IMPROVEMENTS.md](docs/related/axel/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/axel/THREAT_MODEL.md) |
| sigma | [IMPROVEMENTS.md](docs/related/sigma/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/sigma/THREAT_MODEL.md) |
| gitshelves | [IMPROVEMENTS.md](docs/related/gitshelves/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/gitshelves/THREAT_MODEL.md) |
| wove | [IMPROVEMENTS.md](docs/related/wove/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/wove/THREAT_MODEL.md) |
| sugarkube | [IMPROVEMENTS.md](docs/related/sugarkube/IMPROVEMENTS.md) | [THREAT_MODEL.md](docs/related/sugarkube/THREAT_MODEL.md) |
| Nextcloud | [IMPROVEMENTS.md](docs/related/nextcloud/IMPROVEMENTS.md) | N/A |
| PhotoPrism | [IMPROVEMENT_CHECKLISTS.md#photoprism](docs/IMPROVEMENT_CHECKLISTS.md#photoprism) | N/A |
| VaultWarden | [IMPROVEMENT_CHECKLISTS.md#vaultwarden](docs/IMPROVEMENT_CHECKLISTS.md#vaultwarden) | N/A |

## Roadmap

See [docs/gabriel/ROADMAP.md](docs/gabriel/ROADMAP.md) for a more detailed roadmap. Early milestones include:

1. Establishing repository guidelines and a base documentation structure.
2. Collecting security best practices for self-hosted services.
3. Prototyping local LLM inference through token.place.

## Contributing

We use `AGENTS.md` to outline repository-specific instructions for automated agents. Additional contributor guidelines live in [CONTRIBUTING.md](CONTRIBUTING.md). Please read them before opening pull requests.

## CI & Security

The repository includes GitHub Actions workflows for linting, testing, and documentation.
`flake8` and `bandit` catch style issues and common security mistakes, while coverage results are
uploaded to [Codecov](https://codecov.io/) and the latest coverage badge is committed to
[coverage.svg](coverage.svg) after tests run.
Pre-commit hooks also run `detect-secrets` to prevent accidental credential leaks.
Dependabot monitors Python dependencies weekly.

## FAQ

We maintain an evolving list of questions for clarification in [docs/gabriel/FAQ.md](docs/gabriel/FAQ.md). Feel free to add your own or answer existing ones.
