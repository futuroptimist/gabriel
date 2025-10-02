# Gabriel

Gabriel is an open source "guardian angel" LLM aimed at helping individuals securely navigate the digital world. The project intends to provide actionable security advice, maintain personal knowledge about the user's environment (with their consent), and eventually offer local AI-assisted monitoring. Our guiding principle is to keep user data private and handle AI inference locally. When possible we rely on [token.place](https://github.com/futuroptimist/token.place) for encrypted inference, though a fully offline path using components like `llama-cpp-python` is also supported.

[![Lint & Format](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/ci.yml?label=lint%20%26%20format)](https://github.com/futuroptimist/gabriel/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/coverage.yml?label=tests)](https://github.com/futuroptimist/gabriel/actions/workflows/coverage.yml)
[![Coverage](https://raw.githubusercontent.com/futuroptimist/gabriel/main/coverage.svg)](https://codecov.io/gh/futuroptimist/gabriel)
[![Docs](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/docs.yml?label=docs&branch=main)](https://github.com/futuroptimist/gabriel/actions/workflows/docs.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/codeql.yml?label=codeql)](https://github.com/futuroptimist/gabriel/actions/workflows/codeql.yml)
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

Gabriel requires Python 3.10 or later. Clone the repository and run the bootstrap
script to provision a virtual environment, install dependencies, and configure
pre-commit hooks:

```bash
./scripts/setup.sh
```

Preview the actions without making changes via the `--dry-run` flag:

```bash
./scripts/setup.sh --dry-run
```

Activate the environment and run `pytest` with coverage enabled:

```bash
python -m pytest --cov=gabriel --cov-report=term-missing
```

Spell check documentation:

```bash
pyspelling -c .spellcheck.yaml
```

Common tasks are available via the `Makefile`:

```bash
make lint  # run pre-commit checks
make test  # run the test suite with coverage
```

Ruff powers the lightweight linting layer used in both pre-commit hooks and CI. Run it directly
when iterating on lint fixes:

```bash
ruff check .
```

Example usage of arithmetic helpers:

These helpers accept both integers and floats and return `decimal.Decimal` results for
improved precision.

```python
from decimal import Decimal

from gabriel import add, divide, floordiv, modulo, multiply, power, sqrt

result = add(2.5, 3.5)
print(result)  # 6.0
print(isinstance(result, Decimal))  # True
print(divide(multiply(add(2, 3), 4), 2))  # 10.0
print(power(2, 0.5))  # 1.4142135623730951
print(modulo(7, 3))  # 1
print(floordiv(7, 2))  # 3
print(sqrt(9))  # 3
```

The arithmetic helpers now live in `gabriel.arithmetic`, while secret management utilities
reside in `gabriel.secrets`. Importing from `gabriel` continues to expose both families for
backwards compatibility.

Run the helpers from the command line (available as `gabriel` or `gabriel-calc`):

```bash
gabriel-calc add 2 3
# 5
gabriel-calc divide 1 3
# 0.3333333333333333333333333333
```

Manage encrypted secrets via the same CLI:

```bash
gabriel secret store my-service alice --secret "super-secret-value"
gabriel secret get my-service alice
# Secret successfully retrieved. (Value not displayed for security reasons.)
gabriel secret delete my-service alice
```

If you omit `--secret`, the command reads from standard input or securely prompts
when attached to a TTY. The retrieval command intentionally avoids printing the
stored value so it cannot leak via logs; use ``python -c "from gabriel.utils import
get_secret; print(get_secret('my-service', 'alice'))"`` for programmatic access.

### Offline Usage

For fully local inference, see [OFFLINE.md](docs/gabriel/OFFLINE.md).

For storing secrets in the system keyring, see
[docs/gabriel/SECRET_STORAGE.md](docs/gabriel/SECRET_STORAGE.md).

### Docker builds

The repository ships with a `.dockerignore` file that trims the build context by excluding
documentation, tests, and other developer-only artifacts. This keeps local Docker builds fast
and reduces the chance of copying unintended files into the runtime image.

#### Build the image locally

Use the root `Dockerfile` to produce an image tagged `gabriel`. The build only needs the
repository checkout; dependencies are installed within the container.

```bash
docker build -t gabriel .
```

Pass `--build-arg PYTHON_VERSION=3.11` to experiment with alternate Python releases that remain
supported by the Docker base image.

#### Run Gabriel commands inside Docker

Invoke CLI helpers directly via `docker run`. The default entry point exposes the Python
interpreter, so provide the command you wish to execute.

```bash
docker run --rm -it gabriel gabriel-calc add 2 3
docker run --rm -it gabriel gabriel secret store my-service alice --secret my-value
```

Mount a host directory when commands need to read or persist data:

```bash
docker run --rm -it -v "$(pwd)/secrets:/app/secrets" \
  -e GABRIEL_SECRET_DIR=/app/secrets \
  gabriel gabriel secret store vault bob
```

Running in detached mode (`-d`) allows long-lived tasks such as scheduled scans. Combine with
`--env-file` to load configuration managed outside the container.

### Runbook & 3D Viewer

This repo now mirrors flywheel's development helpers. `runbook.yml` lists
typical tasks and `viewer/` hosts a basic `model-viewer` scene. The viewer bundles a
local copy of the `@google/model-viewer` library to avoid third-party requests,
and animations start only after pressing **Start Animation**. Launch
`make preview` to open the viewer locally.

## Tracked Repositories

The table below summarizes all repositories where we currently maintain
improvement tasks or security audits.
Last roster sync: 2025-09-29 05:02 UTC (per Futuroptimist).
improvement tasks or security audits. Following these links will jump to the
relevant documentation.

| Repository | Improvement Docs | Threat Model |
|------------|------------------|--------------|
| Gabriel (this repo) | [IMPROVEMENTS.md][gabriel-improve] | [THREAT_MODEL.md][gabriel-threat] |
| futuroptimist | [IMPROVEMENTS.md][futuroptimist-improve] | [THREAT_MODEL.md][futuroptimist-threat] |
| token.place | [IMPROVEMENTS.md][token-place-improve] | N/A |
| DSPACE | [IMPROVEMENTS.md][dspace-improve] | [THREAT_MODEL.md][dspace-threat] |
| flywheel | [IMPROVEMENTS.md][flywheel-improve] | [THREAT_MODEL.md][flywheel-threat] |
| f2clipboard | [IMPROVEMENTS.md][f2clipboard-improve] | [THREAT_MODEL.md][f2clipboard-threat] |
| axel | [IMPROVEMENTS.md][axel-improve] | [THREAT_MODEL.md][axel-threat] |
| sigma | [IMPROVEMENTS.md][sigma-improve] | [THREAT_MODEL.md][sigma-threat] |
| gitshelves | [IMPROVEMENTS.md][gitshelves-improve] | [THREAT_MODEL.md][gitshelves-threat] |
| wove | [IMPROVEMENTS.md][wove-improve] | [THREAT_MODEL.md][wove-threat] |
| sugarkube | [IMPROVEMENTS.md][sugarkube-improve] | [THREAT_MODEL.md][sugarkube-threat] |
| pr-reaper | [IMPROVEMENTS.md][pr-reaper-improve] | [THREAT_MODEL.md][pr-reaper-threat] |
| jobbot3000 | [IMPROVEMENTS.md][jobbot-improve] | [THREAT_MODEL.md][jobbot-threat] |
| danielsmith.io | [IMPROVEMENTS.md][danielsmith-io-improve] | [THREAT_MODEL.md][danielsmith-io-threat] |
| Nextcloud | [IMPROVEMENTS.md][nextcloud-improve] | N/A |
| PhotoPrism | [IMPROVEMENT_CHECKLISTS.md#photoprism][photoprism-improve] | N/A |
| VaultWarden | [IMPROVEMENT_CHECKLISTS.md#vaultwarden][vaultwarden-improve] | N/A |

[gabriel-improve]: docs/gabriel/IMPROVEMENTS.md
[gabriel-threat]: docs/gabriel/THREAT_MODEL.md
[futuroptimist-improve]: docs/related/futuroptimist/IMPROVEMENTS.md
[futuroptimist-threat]: docs/related/futuroptimist/THREAT_MODEL.md
[token-place-improve]: docs/related/token_place/IMPROVEMENTS.md
[dspace-improve]: docs/related/dspace/IMPROVEMENTS.md
[dspace-threat]: docs/related/dspace/THREAT_MODEL.md
[flywheel-improve]: docs/related/flywheel/IMPROVEMENTS.md
[flywheel-threat]: docs/related/flywheel/THREAT_MODEL.md
[f2clipboard-improve]: docs/related/f2clipboard/IMPROVEMENTS.md
[f2clipboard-threat]: docs/related/f2clipboard/THREAT_MODEL.md
[axel-improve]: docs/related/axel/IMPROVEMENTS.md
[axel-threat]: docs/related/axel/THREAT_MODEL.md
[sigma-improve]: docs/related/sigma/IMPROVEMENTS.md
[sigma-threat]: docs/related/sigma/THREAT_MODEL.md
[gitshelves-improve]: docs/related/gitshelves/IMPROVEMENTS.md
[gitshelves-threat]: docs/related/gitshelves/THREAT_MODEL.md
[wove-improve]: docs/related/wove/IMPROVEMENTS.md
[wove-threat]: docs/related/wove/THREAT_MODEL.md
[sugarkube-improve]: docs/related/sugarkube/IMPROVEMENTS.md
[sugarkube-threat]: docs/related/sugarkube/THREAT_MODEL.md
[pr-reaper-improve]: docs/related/pr-reaper/IMPROVEMENTS.md
[pr-reaper-threat]: docs/related/pr-reaper/THREAT_MODEL.md
[jobbot-improve]: docs/related/jobbot3000/IMPROVEMENTS.md
[jobbot-threat]: docs/related/jobbot3000/THREAT_MODEL.md
[danielsmith-io-improve]: docs/related/danielsmith_io/IMPROVEMENTS.md
[danielsmith-io-threat]: docs/related/danielsmith_io/THREAT_MODEL.md
[nextcloud-improve]: docs/related/nextcloud/IMPROVEMENTS.md
[photoprism-improve]: docs/IMPROVEMENT_CHECKLISTS.md#photoprism
[vaultwarden-improve]: docs/IMPROVEMENT_CHECKLISTS.md#vaultwarden

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
pre-commit hooks also run `detect-secrets`, `pip-audit`, and the `lychee` Markdown link checker to
catch secrets, vulnerable dependencies, and stale references.
Dependabot monitors Python dependencies weekly.

For vulnerability disclosure guidelines, see [SECURITY.md](SECURITY.md).

## FAQ

We maintain an evolving list of questions for clarification in [docs/gabriel/FAQ.md](docs/gabriel/FAQ.md). Feel free to add your own or answer existing ones.
