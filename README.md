# Gabriel

Gabriel is an open source "guardian angel" LLM aimed at helping individuals securely navigate the digital world. The project intends to provide actionable security advice, maintain personal knowledge about the user's environment (with their consent), and eventually offer local AI-assisted monitoring. Our guiding principle is to keep user data private and handle AI inference locally. When possible we rely on [token.place](https://github.com/futuroptimist/token.place) for encrypted inference, though a fully offline path using components like `llama-cpp-python` is also supported.

![License](https://img.shields.io/github/license/futuroptimist/gabriel)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

## Goals

- Offer community-first, dignity-focused security guidance.
- Integrate with token.place or fully local inference to avoid cloud exfiltration.
- Encourage collaboration with [token.place](https://github.com/futuroptimist/token.place) and [sigma](https://github.com/futuroptimist/sigma) as complementary projects.
- Provide a gentle on-ramp toward eventual real-world monitoring capabilities.

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

## Threat Model

See [docs/gabriel/THREAT_MODEL.md](docs/gabriel/THREAT_MODEL.md) for security assumptions and mitigations. In short, secrets should be stored outside of version control and logs should avoid PII. Additional risks related to the flywheel approach are captured in [docs/gabriel/FLYWHEEL_RISK_MODEL.md](docs/gabriel/FLYWHEEL_RISK_MODEL.md).

For recommendations on securing token.place relays and servers, see [docs/related/token_place/TOKEN_PLACE_IMPROVEMENTS.md](docs/related/token_place/TOKEN_PLACE_IMPROVEMENTS.md).

For additional checklists covering improvements to related projects, see [docs/IMPROVEMENT_CHECKLISTS.md](docs/IMPROVEMENT_CHECKLISTS.md).

## Roadmap

See [docs/gabriel/ROADMAP.md](docs/gabriel/ROADMAP.md) for a more detailed roadmap. Early milestones include:

1. Establishing repository guidelines and a base documentation structure.
2. Collecting security best practices for self-hosted services.
3. Prototyping local LLM inference through token.place.

## Contributing

We use `AGENTS.md` to outline repository-specific instructions for automated agents. Additional contributor guidelines live in [CONTRIBUTING.md](CONTRIBUTING.md). Please read them before opening pull requests.

## CI & Security

The repository includes a GitHub Actions workflow that runs `flake8` and `bandit` to catch style issues and common security mistakes. Dependabot is configured to monitor Python dependencies weekly.

## FAQ

We maintain an evolving list of questions for clarification in [docs/gabriel/FAQ.md](docs/gabriel/FAQ.md). Feel free to add your own or answer existing ones.
