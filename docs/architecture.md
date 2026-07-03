# Architecture

## Context
`linkr` turns long URLs into short codes and records click analytics. Two
workloads share one service:

- **Redirect** (`GET /{code}`) — high read volume, latency-sensitive.
- **Management API** (`/api/v1/links`) — create, inspect, delete links.

## Components

```
            ┌─────────────┐        ┌──────────────┐
 client ───▶│   Ingress   │───────▶│  linkr pods  │──┐
            │  (nginx)    │        │  (FastAPI)   │  │ cache lookup
            └─────────────┘        └──────┬───────┘  ▼
                                          │      ┌─────────┐
                                          │      │  Redis  │  (hot path)
                                          │      └─────────┘
                                          ▼
                                    ┌───────────┐
                                    │ PostgreSQL│  (source of truth)
                                    └───────────┘
```

Prometheus scrapes `/metrics` on each pod; Grafana renders SLIs.

## Request flows

### Create link — `POST /api/v1/links`
1. Validate the payload (`url` must be a valid HTTP(S) URL).
2. Allocate a code: use the requested alias, or generate a random base62 code
   and retry on the unique constraint.
3. Persist the row in PostgreSQL and return the short URL.

### Redirect — `GET /{code}` (hot path)
1. Look up `code` in Redis (`code -> "{id}|{target}"`).
2. On a miss, read the active link from PostgreSQL and populate the cache.
3. Record the click (best-effort; see ADR 0005) and return `302` to the target.

## Data model

`links`
| column | type | notes |
|--------|------|-------|
| id | int | primary key |
| code | varchar(16) | unique, indexed |
| target_url | varchar(2048) | |
| is_active | bool | soft delete |
| created_at | timestamptz | |

`clicks`
| column | type | notes |
|--------|------|-------|
| id | int | primary key |
| link_id | int | FK → links.id (cascade), indexed |
| ts | timestamptz | indexed |
| referrer | varchar(2048) | nullable |
| user_agent | varchar(512) | nullable |

## Scaling and availability
- Stateless pods behind a `Deployment`; horizontal scaling via HPA on CPU.
- Redis absorbs the redirect read load, keeping PostgreSQL for writes and misses.
- `PodDisruptionBudget` keeps at least one replica during voluntary disruptions.
- RollingUpdate with `maxUnavailable: 0` gives zero-downtime deploys.

## Failure modes
| Failure | Behaviour |
|---------|-----------|
| Redis down | Redirects fall back to PostgreSQL (higher latency, still correct). |
| PostgreSQL down | `/readyz` fails, pod removed from rotation; writes and cache misses error. |
| Click write fails | Redirect still succeeds; the click is dropped (best-effort analytics). |

## Known trade-offs
See the ADRs in [`docs/adr`](adr/) for the reasoning behind short-code
generation, datastore choice, the AWS/EKS runtime, and best-effort analytics.
