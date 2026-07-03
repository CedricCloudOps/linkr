# ADR 0003 — PostgreSQL as source of truth, Redis for the hot path

- Status: accepted
- Date: 2026-01-05

## Context
The redirect path is read-heavy and latency-sensitive (SLO: P99 < 50 ms).
Links and click history must be durable and queryable.

## Decision
- **PostgreSQL** is the source of truth for links and clicks. It gives
  transactional integrity, a unique constraint for code allocation, and SQL for
  analytics.
- **Redis** caches `code -> target` for redirects with a TTL. On a cache miss the
  service reads PostgreSQL and repopulates Redis.

The service degrades gracefully: if Redis is unavailable, redirects still resolve
from PostgreSQL at higher latency.

## Consequences
- The hot path avoids a database round-trip on cache hits.
- Cache invalidation is handled on delete; TTL bounds staleness otherwise.
- Two stateful dependencies to operate; both are managed services in AWS
  (RDS and ElastiCache).
