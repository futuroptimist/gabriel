# Pull Request Checklist

## Summary

- _What problem does this change solve?_
- _Why is this the right solution?_
- _Any relevant links or references?_

## Testing

- [ ] `pre-commit run --all-files`
- [ ] `pytest --cov=gabriel --cov-report=term-missing`
- [ ] Other (specify): __________________________

## Prompt Injection Review (OWASP LLM01–LLM10)

_Confirm mitigations or explain why the item is not applicable. Link to docs when possible._

- [ ] LLM01 – Prompt Injection & Data Exfiltration mitigations documented
- [ ] LLM02 – Insecure Output Handling sanitized or rejected
- [ ] LLM03 – Training Data Poisoning countermeasures addressed
- [ ] LLM04 – Model Denial of Service risks handled
- [ ] LLM05 – Supply Chain vulnerabilities evaluated
- [ ] LLM06 – Sensitive Information Disclosure prevented
- [ ] LLM07 – Insecure Plugin Design safeguards verified
- [ ] LLM08 – Excessive Agency / Authorization scopes reviewed
- [ ] LLM09 – Overreliance on LLM output mitigated with human review
- [ ] LLM10 – Model Theft detection and protections considered

## Additional Notes

- _Anything else reviewers should know?_
