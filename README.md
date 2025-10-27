# Gabriel

Gabriel is an open source "guardian angel" LLM aimed at helping individuals securely navigate the digital world. The project intends to provide actionable security advice, maintain personal knowledge about the user's environment (with their consent), and eventually offer local AI-assisted monitoring. Our guiding principle is to keep user data private and handle AI inference locally. When possible we rely on [token.place](https://github.com/futuroptimist/token.place) for encrypted inference, though a fully offline path using components like `llama-cpp-python` is also supported.

[![Lint & Format](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/ci.yml?label=lint%20%26%20format)](https://github.com/futuroptimist/gabriel/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/coverage.yml?label=tests)](https://github.com/futuroptimist/gabriel/actions/workflows/coverage.yml)
[![Coverage](https://raw.githubusercontent.com/futuroptimist/gabriel/main/coverage.svg)](https://codecov.io/gh/futuroptimist/gabriel)
[![Docs](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/docs.yml?label=docs&branch=main)](https://github.com/futuroptimist/gabriel/actions/workflows/docs.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/codeql.yml?label=codeql)](https://github.com/futuroptimist/gabriel/actions/workflows/codeql.yml)
[![Security scans](https://img.shields.io/github/actions/workflow/status/futuroptimist/gabriel/.github/workflows/security.yml?label=security%20scans)](https://github.com/futuroptimist/gabriel/actions/workflows/security.yml)
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

This modular structure keeps responsibilities clear and allows future extensions like phishing detection or network monitoring. The new phishing heuristics below provide an early look at that roadmap item.

## Map of the repo

Gabriel is migrating toward a four-module layout.
The table below highlights the current hotspots and where they will land as we
complete the work outlined in the [Polish Four-Module Architecture
prompt](docs/prompts/codex/polish.md).

| Path | Current focus | Target module |
| --- | --- | --- |
| `gabriel/ingestion/text.py` (via `gabriel/text.py` shim), `gabriel/knowledge.py` | Scrape, normalize, and store local evidence | Ingestion |
| `gabriel/analysis/` (`phishing.py`, `policy.py`, `recommendations.py`), `gabriel/security/` | Heuristics, classifiers, and risk scoring | Analysis |
| `gabriel/common/` | Cryptography, persistence, and inference adapters | Common services |
| `gabriel/secrets.py`, `gabriel/notify/tokenplace.py` | Alerts, encrypted delivery, and relay hooks | Notification |
| `viewer/`, `gabriel/ui/` (CLI + viewer), `gabriel/utils.py` | CLI and viewer surfaces | UI |

The `gabriel/analysis/` package now aggregates phishing heuristics, policy validation, and
recommendation scoring behind typed interfaces. Compatibility shims in `gabriel/phishing.py`,
`gabriel/policy.py`, and `gabriel/recommendations.py` keep downstream imports working while we
transition callers to the new paths. The `gabriel/ui/` package owns the CLI and viewer helpers, and
`gabriel/utils.py` provides backwards-compatible imports for existing callers. Shared primitives
(cryptography, persistence, LLM adapters) continue to consolidate under `gabriel/common` as we carve
the boundaries. For a deeper security breakdown, review the
[docs/gabriel/THREAT_MODEL.md](docs/gabriel/THREAT_MODEL.md). The
[docs/gabriel/SECRET_BOUNDARY.md](docs/gabriel/SECRET_BOUNDARY.md) document captures how
credentials flow between local inference and token.place relaying.

## Getting Started

Gabriel requires Python 3.10 or later. Continuous integration pipelines exercise
both Python 3.10 and 3.11 to keep compatibility tight. Clone the repository and
run the bootstrap script to provision a virtual environment, install
dependencies, and configure pre-commit hooks:

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

Run the WebGL viewer unit tests to exercise DOM interactions under Jest:

```bash
npm ci
npm run test:ci
```

Pytest is configured to fail the run if coverage dips below 100%, keeping the suite honest as
the codebase grows.

Spell check documentation:

```bash
pyspelling -c .spellcheck.yaml
```

Scan for hidden zero-width characters:

```bash
python -m gabriel.ingestion.text README.md
# `python -m gabriel.text README.md` remains available for compatibility.
```

Build and preview the MkDocs documentation site locally:

```bash
pip install -r requirements.txt
mkdocs serve
```

Generate the Sphinx API documentation to view the autodoc pages locally (install the required
extras with `pip install -r requirements.txt` or `pip install "gabriel[docs]"`):

```bash
python scripts/build_sphinx_docs.py --output docs/_build/sphinx
open docs/_build/sphinx/index.html  # macOS example; use xdg-open/start on Linux/Windows
```

After running `mkdocs build`, copy the rendered HTML into the MkDocs site output so the pages
publish alongside the rest of the documentation:

```bash
python scripts/build_sphinx_docs.py --output docs/_build/sphinx --site-dir site/sphinx --skip-build
```

The rendered site is also published to GitHub Pages at
futuroptimist.github.io/gabriel after every merge to `main`.

Validate policy guardrails before committing updates to `llm_policy.yaml` or downstream
overrides:

```bash
./scripts/validate_policy.py path/to/llm_policy.yaml
```

Common tasks are available via the `Makefile`:

```bash
make lint   # run pre-commit checks
make test   # run the test suite with coverage
make spell  # run the spell checker
make links  # scan documentation links with lychee
make docs   # build the static MkDocs site
```

### Commit message conventions

Gabriel enforces [Conventional Commits](https://www.conventionalcommits.org/)
using `commitlint`. The commit message hook installs automatically when you run
`./scripts/setup.sh`, and CI runs `npm run lint:commits` to validate the branch
history. You can invoke the same check locally before pushing changes:

```bash
npm run lint:commits
```

Continuous integration also runs `pre-commit run --all-files` to mirror local hook behavior
and catch formatting or security regressions before merge. Dependency installation is
cached across the CI matrix so lint, test, and docs pipelines reuse previously resolved
packages, significantly reducing run time on repeat builds.

Semgrep scans run alongside these hooks using the local rule bundle in
[`config/semgrep/rules.yaml`](config/semgrep/rules.yaml) to flag risky subprocess usage in
Python code before it lands in the repository.

Ruff powers the lightweight linting layer used in both pre-commit hooks and CI. Run it directly
when iterating on lint fixes:

```bash
ruff check .
```

Docstring conventions are enforced via ``flake8`` with the ``flake8-docstrings`` plugin and
validated separately with ``pydocstyle``. Run ``flake8`` or ``pydocstyle`` locally (both are wired
into pre-commit) to surface style issues early in development.

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

The arithmetic helpers now live in `gabriel.arithmetic`, while secret management interfaces
reside in `gabriel.common`. Importing from `gabriel` continues to expose both families for
backwards compatibility via the compatibility layer in `gabriel.secrets`.

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

### Crawl Git repositories for commit metadata

Gabriel now bundles a `crawl` helper that collects recent commit metadata across
local repositories. Supply one or more repository paths (defaults to the current
directory) and optionally redact author email addresses:

```bash
gabriel crawl ../token.place ../sigma --limit 5 --redact-emails
```

The command prints JSON containing each repository's absolute path, commit
hashes, authors, ISO-8601 timestamps, and commit subjects. Use `--output` to
write the same payload to disk, and prefer read-only credentials when scanning
remote mirrors.

### Create ephemeral scratch space

Security-sensitive tasks often need isolated scratch directories that disappear
once work completes. Gabriel now includes a dedicated context manager that
provisions directories under the system temporary path (for example `/tmp`) and
wipes them automatically:

```python
from gabriel import ScratchSpace

with ScratchSpace(task_id="scan-42") as workspace:
    temp_file = workspace / "artifact.txt"
    temp_file.write_text("temporary data", encoding="utf-8")
# Directory and contents removed on exit.
```

Use the optional `base_dir` argument when a different temporary root is
required, such as during integration tests or containerised runs.

### Package metadata

Gabriel exposes standard package metadata so downstream tooling can introspect
versioning and project details without parsing `pyproject.toml` directly:

```python
import gabriel

print(gabriel.__version__)
print(gabriel.__summary__)
```

### Detect suspicious links

Gabriel now ships with lightweight phishing detection heuristics for pasted text or
email bodies. Supply known brand domains to catch close lookalikes.

```python
from gabriel import analyze_text_for_phishing

message = "Click https://accounts.examp1e.com to verify your details."
findings = analyze_text_for_phishing(message, known_domains=["example.com"])
for finding in findings:
    print(f"{finding.indicator}: {finding.message} ({finding.severity})")
```

The helper inspects each HTTP(S) link for punycode, suspicious top-level domains,
embedded credentials, plaintext HTTP, IP-based hosts, lookalikes of the supplied
domains, known URL shorteners that mask the final destination, unusual port usage,
suspicious executable or archive downloads, redirect parameters that jump to
external hosts, domains that nest trusted brands inside attacker-controlled
registrable domains, references to trusted domains buried in paths or query strings,
and base64-like tokens that often indicate obfuscated redirects or payloads.
Combine it with Gabriel's secret helpers to build secure intake
pipelines for inbound phishing reports.

### Assess network exposure

Network monitoring is another roadmap goal. Gabriel now includes a lightweight
`gabriel.analysis.network.analyze_network_services` helper that reviews service
bindings for risky exposures before they ship to production:

```python
from gabriel import NetworkService, analyze_network_services

services = [
    NetworkService(name="Admin Dashboard", port=3000, exposure="internet", authenticated=False),
    NetworkService(name="Status Page", port=8080, exposure="internet", encrypted=False),
]

for finding in analyze_network_services(services):
    print(f"[{finding.severity}] {finding.service}: {finding.message}")
```

The analyzer highlights unauthenticated dashboards, unencrypted HTTP listeners,
wildcard bindings on localhost-only services, database ports exposed to the
internet, and UDP amplification targets that should stay rate-limited or
disabled. Pair these findings with your existing firewall policies to confirm
that sensitive services stay behind trusted networks.

### Sanitize prompts before execution

Use `gabriel.ingestion.text.sanitize_prompt` to strip risky markup from prompts gathered from
untrusted sources. The helper removes HTML tags (including script/style blocks),
Markdown image embeddings, and zero-width characters before passing text to language
models. This blocks common prompt-injection tricks that smuggle hostile payloads in
alt text or invisible characters.

```python
from gabriel import sanitize_prompt

raw = """<p>Summarize the notes below.</p>![leak](https://evil.test/spy.png)"""
safe = sanitize_prompt(raw)
print(safe)
# Summarize the notes below.
```

### Organize security notes into a knowledge store

Phase 2 of the roadmap introduces a personal knowledge manager that keeps security
notes searchable and local. Use the new `gabriel.knowledge` helpers to index Markdown
files or structured snippets and run lightweight keyword searches:

```python
from pathlib import Path

from gabriel import KnowledgeStore

store = KnowledgeStore.from_paths(Path("security-notes").glob("*.md"))
for result in store.search("vaultwarden admin token", required_tags=["passwords"]):
    print(result.note.title, "→", result.snippet)
```

Each result includes the originating note, matched terms, and a contextual snippet so
you can jump directly to the relevant remediation guidance when triaging incidents.

### Enforce repository-scoped vector store access

The agent threat model calls for repository-scoped API keys and short-lived embeddings
so credential exposure windows stay tight. Use `gabriel.SecureVectorStore` to store
embeddings with enforced prefixes, task tagging, and a maximum seven-day TTL:

```python
from datetime import datetime, timedelta, timezone

from gabriel import MAX_VECTOR_TTL, SecureVectorStore

store = SecureVectorStore("gabriel")
record = store.write_embedding(
    [0.12, 0.34, 0.56],
    api_key_id="gabriel:threat-retriever",
    task_id="audit-2025-02-12",
    ttl=timedelta(days=3),
    metadata={"task": "threat-report"},
)
print(record.task_id)
print(record.expires_at - datetime.now(tz=timezone.utc) <= MAX_VECTOR_TTL)

# Purge embeddings older than one hour regardless of TTL to emulate the hourly cleanup job.
store.purge_stale(timedelta(hours=1))
```

The helper rejects API keys that are not prefixed with the repository name, enforces
TTL values of seven days or less, and exposes `purge_stale()` so hourly cleanup jobs
can remove embeddings older than their task rotation window.

### Generate prioritized recommendations

Phase 2 of the roadmap calls for richer guidance that blends audit data with personal
notes. Use :func:`gabriel.analysis.generate_recommendations` to turn audit
findings into a prioritized action plan tuned to your risk tolerance:

```python
from gabriel import (
    KnowledgeStore,
    RiskTolerance,
    VaultWardenConfig,
    audit_vaultwarden,
    generate_recommendations,
)

config = VaultWardenConfig(
    https_enabled=False,
    certificate_trusted=False,
    encryption_key="weak",  # pragma: allowlist secret
    backup_enabled=True,
    backup_frequency_hours=48,
    last_restore_verification_days=90,
    admin_interface_enabled=True,
    admin_allowed_networks=("0.0.0.0/0",),
)

store = KnowledgeStore.from_paths(["docs/IMPROVEMENT_CHECKLISTS.md"])
recommendations = generate_recommendations(
    findings=audit_vaultwarden(config),
    knowledge_notes=store.notes,
    focus_tags=("vaultwarden",),
    risk_tolerance=RiskTolerance.LOW,
)

for rec in recommendations:
    print(f"{rec.severity.upper()} • {rec.summary}")
    for action in rec.remediation:
        print("  -", action)
```

Recommendations include the originating slug, a blended rationale, and every
unique remediation captured during the audits. Adjust ``risk_tolerance`` to filter
noise when you are comfortable accepting more operational risk, or supply
``focus_tags`` to boost topics that demand immediate attention.

### Audit VaultWarden deployments

Phase 1 of the roadmap calls for tailored advice for self-hosted services such as
VaultWarden. Use `gabriel.selfhosted.audit_vaultwarden` to surface misconfigurations
based on the [VaultWarden improvement checklist](docs/IMPROVEMENT_CHECKLISTS.md#vaultwarden).

```python
from gabriel import VaultWardenConfig, audit_vaultwarden

config = VaultWardenConfig(
    https_enabled=True,
    certificate_trusted=False,  # using a self-signed cert in this example
    encryption_key="CorrectHorseBatteryStaple123!CorrectHorseBatteryStaple",
    backup_enabled=True,
    backup_frequency_hours=24,
    last_restore_verification_days=45,
    admin_interface_enabled=True,
    admin_allowed_networks=("192.168.10.0/24",),
)

for finding in audit_vaultwarden(config):
    print(f"{finding.severity.upper()} — {finding.message}")
    print(f"Fix: {finding.remediation}\n")
```

The helper only reports actionable findings so hardened deployments return an empty list.

### Audit Docker daemon hardening

The Docker improvement checklist highlights three controls that frequently slip through
reviews: running the daemon in [rootless mode](https://docs.docker.com/engine/security/rootless/),
requiring [Docker Content Trust](https://docs.docker.com/engine/security/trust/), and enabling
[user namespace remapping](https://docs.docker.com/engine/security/userns-remap/) so container
root users map to non-root UIDs on the host. Use
`gabriel.selfhosted.audit_docker_daemon` to flag missing safeguards:

```python
from gabriel import DockerDaemonConfig, audit_docker_daemon

config = DockerDaemonConfig(
    rootless_enabled=False,
    content_trust_required=False,
    userns_remap_enabled=False,
)

for finding in audit_docker_daemon(config):
    print(f"{finding.severity.upper()} — {finding.message}")
    print(f"Fix: {finding.remediation}\n")
```

The helper mirrors Gabriel's Docker checklist and keeps feedback focused on actionable
changes. Hardened daemons with rootless mode, signature enforcement, and user namespace remapping
return an empty list of findings.

### Audit Syncthing deployments

Syncthing operators can use `gabriel.selfhosted.audit_syncthing` to identify risky defaults such
as plaintext dashboards, public discovery, or unknown device IDs.

```python
from gabriel import SyncthingConfig, audit_syncthing

config = SyncthingConfig(
    https_enabled=False,
    global_discovery_enabled=True,
    relays_enabled=True,
    connected_device_ids=("ABC123", "DEF456"),
    trusted_device_ids=("ABC123",),
)

for finding in audit_syncthing(config):
    print(f"{finding.severity.upper()} — {finding.message}")
    print(f"Fix: {finding.remediation}\n")
```

Hardened clusters with HTTPS in front of the GUI, local-only discovery, and trusted device allow
lists will return an empty list, mirroring VaultWarden behavior.

### Audit Nextcloud deployments

Nextcloud administrators can call `gabriel.selfhosted.audit_nextcloud` to evaluate
hardening tasks such as enforcing HTTPS, MFA, and backup verification as outlined in the
[Nextcloud improvement checklist](docs/related/nextcloud/IMPROVEMENTS.md).

```python
from gabriel import NextcloudConfig, audit_nextcloud

config = NextcloudConfig(
    https_enabled=True,
    certificate_trusted=True,
    mfa_enforced=True,
    updates_current=False,  # pending security updates
    backups_enabled=True,
    last_backup_verification_days=45,
    admin_allowed_networks=("10.10.0.0/16",),
    log_monitoring_enabled=False,
)

for finding in audit_nextcloud(config):
    print(f"{finding.severity.upper()} — {finding.message}")
    print(f"Fix: {finding.remediation}\n")
```

Hardened deployments with trusted certificates, timely updates, enforced MFA, tested backups,
restricted admin networks, and log monitoring return an empty list.

### Audit PhotoPrism deployments

PhotoPrism curates personal photo libraries, so losing data or exposing galleries publicly can
be painful. `gabriel.selfhosted.audit_photoprism` evaluates HTTPS coverage, admin credential
strength, backup posture, and plugin hygiene based on the
[PhotoPrism checklist](docs/IMPROVEMENT_CHECKLISTS.md#photoprism).

```python
from gabriel import PhotoPrismConfig, audit_photoprism

config = PhotoPrismConfig(
    https_enabled=True,
    certificate_trusted=False,
    admin_password="short",  # needs rotation  # pragma: allowlist secret
    library_outside_container=False,
    storage_permissions_hardened=False,
    backups_enabled=True,
    backup_frequency_days=7,
    backups_offsite=False,
    third_party_plugins_enabled=True,
    plugins_reviewed=False,
)

for finding in audit_photoprism(config):
    print(f"{finding.severity.upper()} — {finding.message}")
    print(f"Fix: {finding.remediation}\n")
```

When PhotoPrism runs behind trusted TLS, stores originals outside the container with tight
permissions, replicates backups off-host, and reviews each plugin, the helper returns an empty
list just like the other auditors.

### Request encrypted inference through token.place

Phase 1 also calls for encrypted local inference. `TokenPlaceClient` provides a thin wrapper around
the token.place relay API so you can relay prompts without wiring up HTTP plumbing manually.

```python
from gabriel import TokenPlaceClient

client = TokenPlaceClient("https://relay.local", api_key="tp_test_123")

completion = client.infer(
    "Summarize the latest firewall alerts.",
    model="llama3-70b",  # optional override when multiple models are exposed
    metadata={"source": "gabriel-demo"},
)

print(completion.text)
```

`check_health()` performs a lightweight `GET /v1/health` probe so you can verify connectivity
before submitting a prompt. The helper never sends telemetry beyond the configured relay URL,
keeping Gabriel's privacy posture intact.

### Choose inference mode from the CLI

Use the unified `gabriel infer` command to switch between offline completions powered by
`llama.cpp` and encrypted relay requests. When `GABRIEL_MODEL_PATH` points to a local GGUF model,
Gabriel defaults to local inference and generates responses without network access:

```bash
gabriel infer --model-path ~/models/llama3.gguf "Summarize the latest CVE bulletin"
```

Pass `--mode relay` to override the default and route prompts through token.place instead. Supply
the relay URL, API key, and optional metadata in a single invocation:

```bash
gabriel infer --mode relay \
  --relay-url https://relay.local \
  --api-key tp_test_123 \
  --model llama3-70b \
  --metadata '{"source": "gabriel-demo"}' \
  "Draft weekend hardening tasks"
```

The CLI surfaces sampling controls like `--temperature`, `--top-p`, and `--max-tokens` so scripted
workflows can tune output without touching Python APIs.

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

The GitHub Actions workflow publishes a multi-architecture image for
`linux/amd64` and `linux/arm64`, so `docker pull ghcr.io/futuroptimist/gabriel:latest`
works on modern Intel/AMD and Apple Silicon hosts without additional flags. To
test other architectures locally, pass the desired platform to Buildx:

```bash
docker buildx build --platform linux/arm64 -t gabriel:arm64 .
```

Every publish run now performs a `trivy` vulnerability scan against the freshly
built `linux/amd64` image before pushing the multi-architecture manifest. Builds
fail when high or critical issues surface, keeping the public image aligned with
our hardening guidance.

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
and animations start only after pressing **Start Animation**. Use the bundled CLI to
serve the assets locally:

```bash
gabriel viewer --port 9000
```

Passing `--no-browser` skips automatically launching the system browser. See
[`docs/gabriel/VIEWER.md`](docs/gabriel/VIEWER.md) for additional automation tips.
The `make preview` target runs the same helper with default settings. Viewer scripts
are linted with ESLint via pre-commit; run `npx eslint viewer/viewer.js` when iterating
on WebGL logic. Prettier also formats the HTML and JavaScript sources; apply fixes with
`npx prettier --write viewer/index.html viewer/viewer.js` before committing changes.

## Tracked Repositories

The table below summarizes all repositories where we currently maintain
improvement tasks or security audits.
Last roster sync: 2025-10-18 23:02 UTC (per Futuroptimist). Status icons mirror the upstream README.
Following these links will jump to the relevant documentation.

| Repository | Status | Improvement Docs | Threat Model |
|------------|--------|------------------|--------------|
| Gabriel (this repo) | ✅ | [IMPROVEMENTS.md][gabriel-improve] | [THREAT_MODEL.md][gabriel-threat] |
| futuroptimist | ✅ | [IMPROVEMENTS.md][futuroptimist-improve] | [THREAT_MODEL.md][futuroptimist-threat] |
| token.place | ✅ | [IMPROVEMENTS.md][token-place-improve] | N/A |
| DSPACE | ✅ | [IMPROVEMENTS.md][dspace-improve] | [THREAT_MODEL.md][dspace-threat] |
| flywheel | ✅ | [IMPROVEMENTS.md][flywheel-improve] | [THREAT_MODEL.md][flywheel-threat] |
| f2clipboard | ✅ | [IMPROVEMENTS.md][f2clipboard-improve] | [THREAT_MODEL.md][f2clipboard-threat] |
| axel | ✅ | [IMPROVEMENTS.md][axel-improve] | [THREAT_MODEL.md][axel-threat] |
| sigma | ✅ | [IMPROVEMENTS.md][sigma-improve] | [THREAT_MODEL.md][sigma-threat] |
| gitshelves | ✅ | [IMPROVEMENTS.md][gitshelves-improve] | [THREAT_MODEL.md][gitshelves-threat] |
| wove | ✅ | [IMPROVEMENTS.md][wove-improve] | [THREAT_MODEL.md][wove-threat] |
| sugarkube | ❌ | [IMPROVEMENTS.md][sugarkube-improve] | [THREAT_MODEL.md][sugarkube-threat] |
| pr-reaper | ✅ | [IMPROVEMENTS.md][pr-reaper-improve] | [THREAT_MODEL.md][pr-reaper-threat] |
| jobbot3000 | ✅ | [IMPROVEMENTS.md][jobbot-improve] | [THREAT_MODEL.md][jobbot-threat] |
| danielsmith.io | ✅ | [IMPROVEMENTS.md][danielsmith-io-improve] | [THREAT_MODEL.md][danielsmith-io-threat] |
| Nextcloud | – | [IMPROVEMENTS.md][nextcloud-improve] | N/A |
| PhotoPrism | – | [IMPROVEMENT_CHECKLISTS.md#photoprism][photoprism-improve] | N/A |
| VaultWarden | – | [IMPROVEMENT_CHECKLISTS.md#vaultwarden][vaultwarden-improve] | N/A |

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

The repository includes GitHub Actions workflows for linting, testing, documentation, and recurring security sweeps.
`flake8` and `bandit` catch style issues and common security mistakes, while coverage results are
uploaded to [Codecov](https://codecov.io/) and the latest coverage badge is committed to
[coverage.svg](coverage.svg) after tests run. Coverage builds now exercise Linux, macOS, and Windows
runners to surface platform-specific issues before they reach `main`.
pre-commit hooks also run `detect-secrets`, `trufflehog`, `pip-audit`, the `lychee` Markdown link
checker, `pymarkdown`, and the custom `gabriel.prompt_lint` scanner to catch secrets, vulnerable
dependencies, stale references, style regressions, and prompt-injection red flags in Markdown
content.
The scheduled [`security.yml`](.github/workflows/security.yml) workflow re-runs CodeQL, Semgrep,
and dependency audits every Monday at 06:00 UTC so regressions surface even during quieter weeks.
Dependabot monitors Python dependencies, GitHub Actions workflows, and Docker base image updates weekly.

## Release management

Release notes are drafted automatically via the
[`release-drafter` action](.github/workflows/release-drafter.yml) using the
configuration in [.github/release-drafter.yml](.github/release-drafter.yml).
Merges to `main` update the draft and categorize entries by labels such as
`feature`, `fix`, `docs`, and `security`. Tag a release from GitHub's UI to
publish the curated notes without additional manual formatting.

For vulnerability disclosure guidelines, see [SECURITY.md](SECURITY.md).

## FAQ

We maintain an evolving list of questions for clarification in [docs/gabriel/FAQ.md](docs/gabriel/FAQ.md). Feel free to add your own or answer existing ones.
