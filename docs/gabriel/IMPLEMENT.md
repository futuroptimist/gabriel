# Continuous Monitoring Design (Draft)

This design explores how Gabriel can evolve from heuristic link scanning toward a
privacy-preserving continuous monitoring assistant. It complements the existing roadmap
and provides concrete follow-on work items for future ``implement`` prompts.

## Objectives

1. **Respect privacy first.** All monitoring must run locally and store only anonymised metadata.
2. **Surface actionable insights.** Findings should include remediation steps or triage guidance.
3. **Stay modular.** Each capability should plug into the existing ingestion → analysis →
   notification pipeline without forcing a monolithic agent.
4. **Minimise operational toil.** Automations should come with health checks, alert fatigue
   guards, and well-documented escape hatches.

## Proposed Capabilities

### 1. Local Event Collector

- Build a lightweight daemon (or scheduled task) that ingests operating system security
  logs, browser download histories, and phishing submissions from email clients.
- Normalise events into a shared schema stored inside an encrypted SQLite database.
- Expose ingestion metrics (queue length, last successful poll) for the notification module.

### 2. LLM-Assisted Triage

- Fine-tune an on-device model (LLaMA or Mistral derivative) on labelled phishing and
  misconfiguration examples collected from Gabriel users.
- Use structured prompts that highlight context (user role, service criticality) while
  masking personal data.
- Add guardrails that require human confirmation before automatically applying
  suggested remediations.

### 3. Continuous Configuration Audits

- Extend ``gabriel.selfhosted`` with plug-ins for Syncthing, Nextcloud, and PhotoPrism
  based on the existing improvement checklists.
- Schedule recurring audits via ``cron`` or the host platform's task scheduler and emit
  findings to the notification layer when state drifts from hardened baselines.
- Record historical findings for trend analysis so users can see when posture improves or regresses.

### 4. Alerting & Runbooks

- Introduce a local webhook dispatcher that can post findings to Matrix rooms, Signal bots,
  or desktop notifications.
- Generate templated runbooks (Markdown + YAML) that summarise the remediation workflow for
  each alert type, referencing upstream documentation or vendor advisories.

## Roadmap

- **Alpha – Event collection:** Local collector prototype, encrypted storage layer, ingestion
  metrics.
- **Beta – LLM triage:** Prompt templates, evaluation harness, human-in-the-loop review
  tooling.
- **GA – Audit parity:** Service-specific plug-ins, scheduling integration, and posture trend
  reports.
- **Plus – Alert maturity:** Multi-channel notifications, runbook generator, and a health
  dashboard.

## Risks & Mitigations

- **Data Overreach:** Limit collection to opted-in directories and redact personal content
  before persistence.
- **Model Drift:** Retrain on curated datasets and add regression suites mirroring
  ``tests/test_phishing`` to catch degraded detections.
- **User Fatigue:** Batch low-severity findings and provide snooze controls in the
  CLI/notification UI.
- **Supply Chain:** Pin model artefacts and container images; verify signatures before promotion.

## Next Steps for Agents

1. Implement the event collector skeleton with opt-in configuration and tests for log parsing.
2. Draft prompt templates and evaluation fixtures for the triage model using anonymised samples.
3. Expand ``gabriel.selfhosted`` with at least one additional service audit following
   the VaultWarden pattern and build coverage-driven tests.
4. Prototype a CLI command that summarises outstanding findings, with options to export Markdown
   runbooks for the remediation queue.

