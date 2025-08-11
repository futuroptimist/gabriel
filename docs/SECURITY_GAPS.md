# Common Security Gaps and Mitigations

This document summarizes typical areas where security gaps often appear and offers high-level strategies to mitigate them. Use it as a quick reference when assessing system security.

| Area | Potential Gap | Mitigation |
|------|---------------|------------|
| **Patch management** | Outdated OS or package versions with known CVEs | Establish automated patching and dependency tracking; run regular vulnerability scans. |
| **Network exposure** | Unnecessary open ports or services exposed to the internet | Apply least-privilege principles on firewalls/SGs; close unused ports; enable intrusion detection/prevention. |
| **Authentication & access** | Weak passwords or missing MFA; excessive privilege | Enforce strong password policy, MFA, and RBAC; audit and prune unused accounts. |
| **Data protection** | Sensitive data stored or transmitted without encryption | Encrypt data at rest (e.g., disk/db encryption) and in transit (TLS); rotate keys regularly. |
| **Logging & monitoring** | Insufficient or misconfigured logging; lack of alerting | Centralize logs, monitor anomalies, and define incident response workflows. |
| **Backup & recovery** | Missing or untested backups | Implement regular, versioned backups; verify restoration procedures. |
| **Third-party dependencies** | Unsigned/unknown software; unvetted scripts | Verify sources, use hash/signature checks, and run dependency security scans. |
| **Configuration management** | Ad-hoc changes not tracked or reviewed | Use configuration-as-code (e.g., Ansible, Terraform) with peer review and version control. |

If a detailed system overview becomes available, more targeted findings and mitigations can be added.
