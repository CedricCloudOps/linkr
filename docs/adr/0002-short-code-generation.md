# ADR 0002 — Short-code generation strategy

- Status: accepted
- Date: 2026-01-05

## Context
Every link needs a short, unique, URL-safe code. Two common approaches:

1. **Sequential id encoded in base62.** Guarantees uniqueness with no retries
   and yields the shortest codes, but leaks the total number of links and lets
   anyone enumerate every short URL by incrementing the code.
2. **Random base62 code with a uniqueness check.** No enumeration, at the cost
   of an occasional insert retry on collision.

## Decision
Generate a random 7-character base62 code (62^7 ≈ 3.5×10^12 values) using
`secrets.choice`, and rely on the unique constraint on `links.code`, retrying a
bounded number of times on collision. Custom aliases are supported and validated
against a reserved-words list.

## Consequences
- No enumeration of the link space; codes are not guessable.
- Collision probability is negligible at the expected scale; retries are rare.
- Codes do not encode ordering, so they cannot be used to infer creation time.
