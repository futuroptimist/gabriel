---
tags:
  - risk:leakage
  - policy:mitigation
  - owner:security
---

# Overview

Large Language Model (LLM) data leakage is the unintended disclosure of sensitive information
through direct or indirect interactions with the model, including prompt handling, tool execution,
and logging workflows. Key reference frameworks include the NIST AI Risk Management Framework,
the OWASP Top 10 for LLM Applications (2025), and emerging research such as indirect
prompt-injection studies from OpenAI.

# Risk Taxonomy

| Category | Description | Likelihood | Impact | Example |
| --- | --- | --- | --- | --- |
| Prompt Echo | Leaks hidden prompts or secrets. | High | High | "Ignore prior" prompt |
| Training Data | Recalls stored PII or proprietary data. | Medium | High | PII recall test |
| Indirect Injection | Untrusted input overrides goals. | High | High | HTML/Base64 payload |
| Tool Exfiltration | Over-scoped actions leak via APIs. | Medium | High | OAuth scope abuse |
| Pipeline Poisoning | Malicious data taints RAG/training. | Medium | High | "Canary string" trigger |
| Logging & Analytics | Telemetry keeps raw secrets. | High | High | Raw prompt storage |
| Human Factors | People tricked into sharing secrets. | Medium to High | High | Fake escalation request |

# Mitigation Matrix

| Vector | Key Mitigations |
| --- | --- |
| Prompt Echo | Secret redaction, prompt segmentation, output filters |
| Training Data | Privacy-preserving evaluations, provenance tracking |
| Injection | Input sanitization, allow-listed schemas, prompt shields |
| Tools | RBAC, scoped tokens, audit logging |
| Pipeline | Signed datasets, canary detection, retraining hygiene |
| Logging | Field encryption, TTL rotation, redacted transcripts |
| Human Factors | Runbooks, training, approval workflows |

# Gabriel Tagging Schema

```yaml
risk_tags:
  - channel: [prompt_echo, rag_injection, plugin_oauth, tool_chain, logging, training_poison, supply_chain]
  - likelihood: [low, med, high]
  - impact: [low, med, high]
  - mitigations:
      - DLP_in_out
      - allowlist_tools
      - prompt_shield
      - sandbox_browser
      - pii_mask_logs
      - RBAC_prompts
      - SBOM_verify
  - status: [planned, enforced, monitored]
  - tests: [redteam_suite_id, canary_ids]
```

# Default Controls

1. DLP input/output enforcement
2. Prompt shield & injection classifier
3. Tool least-privilege with confirmations
4. Secure logging (scrub + short TTL)
5. Red team pack with multilingual & encoded injections
6. Supply-chain verification (hash-pin, SBOM)

# Red Team Scenarios

- Hidden instructions in PDFs/HTML
- Base64/ROT13 encoding tricks
- Multilingual bait
- OAuth over-scoped requests
- "Summarize and send" exfiltration payloads

# References

- OWASP LLM Top 10 (2025)
- NIST AI RMF
- Anthropic Prompt-Injection Report
- OpenAI Indirect Injection Study
