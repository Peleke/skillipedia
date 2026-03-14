---
id: test-fidelity-over-coverage
type: learning
claim: Prioritize test fidelity (does the test prove what it claims?) over coverage percentage.
confidence: 0.78
domain: testing
derivation: derived
tags: [testing, quality, verification]
category: testing
source_concepts: [test-design, verification, quality-assurance]
provenance:
  source_type: skill_md
  source_id: test-philosophy
  ingested_at: "2026-03-11T00:00:00Z"
generated_at: "2026-03-11T00:00:00Z"
---

## test-fidelity-over-coverage

Prioritize test fidelity over coverage percentage. A test that exercises real code paths and makes meaningful assertions is worth more than ten tests that assert `true == true` to inflate coverage metrics.

### Context

Coverage metrics create perverse incentives. Teams optimize for the number rather than the quality of assertions. 100% coverage with weak assertions gives false confidence.

### Antipattern

Writing tests that call functions but never assert on meaningful output. Testing implementation details instead of behavior. Mocking so aggressively that the test only exercises the mock.

### Rationale

Test fidelity is the probability that a passing test suite means the system works correctly. High coverage with low fidelity is worse than moderate coverage with high fidelity because it creates false confidence.
