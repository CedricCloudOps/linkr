# ADR 0001 — Record architecture decisions

- Status: accepted
- Date: 2026-01-05

## Context
Design choices need a durable, reviewable trail so that future contributors
understand why the system is built the way it is.

## Decision
Use lightweight Architecture Decision Records (Nygard format) stored in
`docs/adr`. One file per decision, numbered sequentially, never rewritten once
accepted — superseded decisions get a new ADR that references the old one.

## Consequences
- Decisions are versioned with the code and reviewed via pull requests.
- The cost is small and paid at decision time, not months later during handover.
