# ADR 0005 — Best-effort click analytics

- Status: accepted
- Date: 2026-01-05

## Context
Every redirect records a click. Making analytics durable on the hot path (a
synchronous, transactional insert that must succeed) couples redirect
availability to the analytics write path and adds latency.

## Decision
Recording a click is **best-effort**: the redirect returns `302` even if the
click insert fails. A failed insert is rolled back and dropped rather than
surfaced to the user.

## Consequences
- Redirect availability is decoupled from analytics durability.
- A small fraction of clicks may be lost during database pressure; acceptable for
  aggregate analytics.
- Future work: move click recording off the request path to a queue (e.g.
  Kinesis/SQS) with a consumer that batches inserts. Tracked as a roadmap item.
