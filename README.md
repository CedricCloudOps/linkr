# linkr

URL shortening and click-analytics service. A small, production-shaped
microservice that demonstrates an end-to-end delivery chain: application code,
tests, containerization, CI/CD with security scanning, Kubernetes deployment,
AWS infrastructure as code, and observability with SLOs.

[![CI](https://github.com/CedricCloudOps/linkr/actions/workflows/ci.yml/badge.svg)](https://github.com/CedricCloudOps/linkr/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## What it does
- Create short links, with optional custom aliases.
- Redirect `GET /{code}` to the target URL, served from a Redis cache.
- Record and expose per-link click analytics.

## Service level objectives
- Availability: **99.9%** (28-day rolling window).
- Redirect latency: **P99 < 50 ms**.

See [`observability/slo.md`](observability/slo.md) for SLI definitions and the
error-budget policy.

## Architecture
```
client ──▶ nginx Ingress ──▶ linkr (FastAPI) ──▶ Redis  (redirect hot path)
                                     └─────────▶ PostgreSQL (source of truth)
                              /metrics ──▶ Prometheus ──▶ Grafana
```
Details and trade-offs: [`docs/architecture.md`](docs/architecture.md) and the
[ADRs](docs/adr).

## Tech stack
| Area | Choice |
|------|--------|
| API | FastAPI, Pydantic v2, Gunicorn/Uvicorn |
| Data | PostgreSQL (SQLAlchemy 2.0, Alembic), Redis |
| Container | Multi-stage Docker image, non-root, read-only rootfs |
| CI/CD | GitHub Actions, Trivy scan, SBOM (SPDX) |
| Runtime | Kubernetes (Kustomize base + overlays), HPA, PDB, NetworkPolicy |
| Infra | Terraform: VPC, EKS, RDS, ElastiCache, ECR |
| Observability | Prometheus, Grafana, multi-window burn-rate alerts |

## API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/links` | Create a link (`{"url": "...", "custom_alias": "..."}`) |
| GET | `/api/v1/links/{code}` | Link metadata and total clicks |
| GET | `/api/v1/links/{code}/stats?days=7` | Click analytics by day |
| DELETE | `/api/v1/links/{code}` | Deactivate a link |
| GET | `/{code}` | Redirect (302) to the target |
| GET | `/healthz`, `/readyz` | Liveness and readiness probes |
| GET | `/metrics` | Prometheus metrics |

Interactive OpenAPI docs are served at `/docs`.

## Quickstart

Python only (SQLite, in-process cache):
```bash
make install
source .venv/bin/activate
make run          # http://localhost:8000/docs
```

Full stack (PostgreSQL + Redis + migrations) via Docker:
```bash
make up           # docker compose
```

Example:
```bash
curl -s -X POST localhost:8000/api/v1/links \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com/a/very/long/path"}'
```

More detail: [`docs/local-development.md`](docs/local-development.md).

## Quality gates
```bash
make lint         # ruff
make security     # bandit + pip-audit
make test         # pytest (unit tests + coverage)
```
CI additionally runs the test suite on Python 3.11 and 3.12, applies and reverts
migrations against PostgreSQL, builds the image and scans it with Trivy.

## Deployment
`main` deploys to staging automatically; a `v*` tag deploys to production behind
a manual approval and cuts a GitHub Release with an SBOM. See
[`docs/deployment.md`](docs/deployment.md) and
[`infra/terraform/README.md`](infra/terraform/README.md).

## Repository layout
```
src/linkr/            application (routers, service layer, models, cache, metrics)
tests/                unit tests
migrations/           Alembic migrations
deploy/kubernetes/    Kustomize base + staging/production overlays
infra/terraform/      AWS infrastructure (VPC, EKS, RDS, ElastiCache, ECR)
observability/        Prometheus rules, Grafana dashboard, SLO definitions
docs/                 architecture, ADRs, runbook, guides
.github/workflows/    CI and release/deploy pipelines
```

## Documentation
- [Architecture](docs/architecture.md)
- [Architecture Decision Records](docs/adr)
- [Runbook](docs/runbook.md)
- [Local development](docs/local-development.md)
- [Deployment](docs/deployment.md)
- [SLOs](observability/slo.md)

## License
[MIT](LICENSE).
