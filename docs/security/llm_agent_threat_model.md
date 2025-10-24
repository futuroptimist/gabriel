# LLM Agent Threat Model

## Overview

This document consolidates LLM-agent security practices for Gabriel and sibling Futuroptimist
projects. It aligns with OWASP LLM01–LLM10 and maps controls to the NIST AI RMF functions
(Govern, Map, Measure, Manage). The goal is to enable consistent, auditable guardrails for
agentic coding workflows, regardless of deployment environment.

## Attack Surfaces

### Attack Surface: Prompt Injection & Data Poisoning

- **Direct prompt injection** via task instructions, PR descriptions, issue comments, or README
  snippets (OWASP LLM01, LLM02).
- **Indirect prompt injection** through linked URLs, dependency manifests, generated binaries,
  or build logs that the agent ingests (OWASP LLM04).
- **Hidden payloads** embedded in Markdown (HTML comments, zero-width characters) or repo files
  that instruct the agent to override policies (OWASP LLM06).
- **Embedding/data poisoning** where malicious vectors in shared stores contaminate retrievals
  across repos, leading to instruction drift (OWASP LLM07).
- **Cross-repo contamination** when embeddings or caches from one project leak into another,
  causing policy conflicts or disclosure of private context (NIST AI RMF – Manage).

### Attack Surface: Permission & Token Boundaries

- **Over-scoped PATs or OAuth tokens** allow attackers to escalate from read to destructive
  operations (OWASP LLM08).
- **Credential reuse** across repos increases blast radius if a single token is compromised.
- **Unbounded agent runtimes** permit long-lived access beyond the intended task window.

### Attack Surface: Memory Hygiene & Sandboxing

- **Persistent vector stores** retain sensitive prompts or secrets beyond task completion.
- **Shared scratch directories** can expose secrets between concurrent agent sessions.
- **Unscanned artifacts** in memory tiers allow exfiltration of credentials or proprietary data.

### Attack Surface: Tool & Function-Call Safety

- **Unvalidated tool invocations** (shell, git, HTTP) can be abused for lateral movement or data
  exfiltration (OWASP LLM03).
- **Dynamic code execution** without allow-listing permits arbitrary payloads to run.
- **Network egress** to untrusted domains enables C2 channels or data leakage.

### Attack Surface: CI/CD & Repo Hardening

- **Unchecked PRs** allow malicious plans to merge without human review (OWASP LLM05).
- **CI secrets** exposed to agent-generated pipelines can be exfiltrated via logs.
- **Unvetted dependencies** may introduce supply-chain attacks that influence the agent.

### Attack Surface: Cross-Repo Reuse Risks

- **Policy drift** when downstream repos fail to ingest updated security profiles.
- **Misconfiguration** of automation (e.g., `flywheel` templates) leads to inconsistent guardrails.

## Mitigation Strategies

### Mitigation: Prompt Injection & Data Poisoning

- Enforce a **prompt sanitization pipeline**: strip HTML, collapse whitespace, reject `ignore`
  directives unless explicitly allow-listed.
- Maintain **immutable system prompts** stored in signed config files.
- Adopt **retrieval isolation**: per-repo embeddings stored in ephemeral indices with TTLs.
- Run **content provenance checks** (e.g., checksum verified docs) before ingestion.
- Apply **prompt-injection linting** to PRs and docs referencing agent workflows
  via the `gabriel.prompt_lint` pre-commit hook.

### Mitigation: Permission & Token Boundaries

- Issue **least-privilege PAT scopes** (`repo:status`, `pull_request:write`) per repository.
- Implement a **two-phase flow**: agents propose changes via draft PRs, humans review/merge.
- Use **time-boxed credentials** (GitHub fine-grained tokens with expiry ≤24h).
- Automate **credential rotation and revocation** via secret broker APIs on task completion.

### Mitigation: Memory Hygiene & Sandboxing

- Provision **ephemeral containers** per task with isolated filesystems and auto-destroy timers.
- Tier memory:
  1. **Immutable reference docs** (read-only, versioned).
  2. **Quarantined crawl outputs** subjected to entropy and signature scanning.
  3. **Secrets broker** delivering short-lived tokens via IPC, never disk.
- Schedule **automated entropy scans** (`ripsecrets`, `detect-secrets`) followed by secure purge.

### Mitigation: Tool & Function-Call Safety

- Maintain an **allow-listed command registry** (YAML) that maps tasks → permitted tools.
- Enforce **tool-call validators** that check arguments against regex policies and rate limits.
- Route outbound HTTP via an **allow-listed fetch proxy** with domain verification and logging.
- Require **human approval** for escalation requests (e.g., installing new packages).

### Mitigation: CI/CD & Repo Hardening

- Enable **secret scanning** (GitHub Advanced Security, Trufflehog) and fail builds on hits.
- Run **dependency audits** (`pip-audit`, `npm audit`) and security linters (CodeQL, Semgrep).
- Require **signed Plan.md** files in PRs documenting intent, linked to execution logs.
- [x] Add **prompt-injection linter** jobs that flag suspicious Markdown or instructions
      using `python -m gabriel.prompt_lint`.
- Configure **branch protection** enforcing reviews, status checks, and signed commits.

### Mitigation: Cross-Repo Reuse

- Publish **versioned security baselines** consumable via `flywheel update --save-dev`.
- Provide **policy modules** (`security/llm_policy.yaml`) that repos import verbatim.
- Document **override hooks** so repos can extend defaults without weakening controls.

## Implementation Guidelines

### Prompt & Retrieval Controls Checklist

- [ ] System prompts stored in `config/prompts/system.md` signed with SLSA provenance.
- [x] Sanitizer strips HTML, markdown images, and zero-width characters before execution
      (`gabriel.ingestion.text.sanitize_prompt`).
- [ ] Embedding writes require repo-specific API keys and TTL ≤7 days.
- [x] PR templates include a "Prompt Injection Review" checklist referencing
      OWASP LLM01–LLM10 (`.github/PULL_REQUEST_TEMPLATE.md`).

### Credential Management Checklist

- [ ] PAT scopes limited to `contents:read`, `pull_requests:write`, `codespaces:secrets` when needed.
- [ ] Token broker issues per-task credentials with automatic revocation webhooks.
- [ ] Audit log reviewed weekly for expired-but-active tokens (NIST AI RMF – Measure).

### Sandboxing & Storage Checklist

- [ ] Tasks execute in disposable containers (`docker run --rm`).
- [x] Scratch space mounted under `/tmp/$TASK_ID` and wiped post-run
      (`gabriel.common.scratch.ScratchSpace`).
- [ ] Vector stores tagged with task metadata; purge job runs hourly.

### Tooling Policy Snippet

```yaml
commands:
  allow:
    - git status
    - git diff --stat
    - npm run lint
  deny:
    - curl http://*
    - python -c "import os; os.system('sh')"
validators:
  shell:
    arguments_regex: "^(git|npm|pytest)"
```

### CI/CD Hardening Checklist

- [x] `.github/workflows/security.yml` runs CodeQL, Semgrep, dependency scans weekly.
- [ ] `Plan.md` signed with cosign; workflow verifies signature before merge.
- [x] Prompt-injection linter executes on `docs/**` and `prompts/**` changes.
- [ ] Branch protection requires two approvals for security-sensitive directories.

## Monitoring & Response

- Implement **centralized logging** for agent sessions, tool invocations, and credential issuance.
- Configure **anomaly detection** on token usage (spikes, geographic anomalies) mapped to NIST
  AI RMF Measure/Manage.
- Establish **alert thresholds** for:
  - Unexpected outbound domains.
  - Repeated validator denials.
  - High-entropy strings in logs (potential secrets).
- Maintain an **incident playbook** detailing containment, eradication, and recovery steps.
- Conduct **post-incident reviews** referencing OWASP LLM10 (Model Theft) and update policies.

## Cross-Repo Templates

- Host a **`security/` template package** in `flywheel` providing:
  - `llm_agent_threat_model.md` reference.
  - `llm_policy.yaml` allow-list defaults.
  - GitHub Actions workflows (`security.yml`, `plan-signature.yml`).
- Distribute via `flywheel update --save-dev --policy llm-security@v1` to sync downstream repos.
- Offer **configuration parameters**:
  - `repo_name`, `sensitivity_level`, `allowed_domains`, `token_ttl_hours`.
  - Hooks for custom tools (`extra_allow_commands`).
- Provide **verification scripts** (`scripts/validate_policy.py`) to ensure local overrides conform. Gabriel now ships a
  reference implementation that validates command allow-lists, deny-lists, and validator settings.
- Maintain **changelog and version manifest** so downstream users can track updates and
  automatically open PRs when new security fixes release.
