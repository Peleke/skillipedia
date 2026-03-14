---
id: code-review-security-checks
type: skill
claim: Review code for SQL injection, command injection, path traversal, and hardcoded credentials before merge.
confidence: 0.95
domain: security
derivation: literal
tags: [security, code-review, owasp]
category: security
source_concepts: [code-review, vulnerability-detection]
provenance:
  source_type: skill_md
  source_id: code-review
  ingested_at: "2026-03-11T00:00:00Z"
generated_at: "2026-03-11T00:00:00Z"
---

## code-review-security-checks

Review code for SQL injection, command injection, path traversal, and hardcoded credentials before merge. Flag uses of `eval()` or `exec()` with external input. Verify no secrets are committed to source control.

### Context

Security review is the last line of defense before code reaches production. Automated scanners catch known patterns but miss logic-level vulnerabilities that only a human reviewer can identify.

### Antipattern

Rubber-stamping PRs without reading the diff. Approving code that passes CI without checking for security-sensitive patterns.

### Rationale

The cost of catching a vulnerability in code review is orders of magnitude lower than catching it in production. OWASP Top 10 vulnerabilities are the most common attack vectors and the easiest to prevent with review discipline.
