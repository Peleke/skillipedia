---
id: error-boundary-pattern
type: pattern
claim: Wrap external API calls in error boundaries that log, retry with backoff, and degrade gracefully.
confidence: 0.85
domain: resilience
derivation: derived
tags: [error-handling, resilience, api]
category: resilience
source_concepts: [error-handling, api-integration, retry-logic]
provenance:
  source_type: skill_md
  source_id: api-resilience
  ingested_at: "2026-03-11T00:00:00Z"
generated_at: "2026-03-11T00:00:00Z"
---

## error-boundary-pattern

Wrap external API calls in error boundaries that log context, retry with exponential backoff, and degrade gracefully when retries are exhausted. Never let an external service failure crash the host process.

### Context

External services fail. Networks partition. Rate limits trigger. The question is not whether failures happen but how the system behaves when they do. Error boundaries isolate blast radius.

### Antipattern

Bare `try/except: pass` blocks that swallow errors silently. Infinite retry loops without backoff. Letting unhandled exceptions propagate to the top level.

### Rationale

Graceful degradation preserves partial functionality. Structured logging enables post-incident debugging. Backoff prevents thundering herds against recovering services.
