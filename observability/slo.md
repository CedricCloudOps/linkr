# Service Level Objectives

## Service overview
`linkr` serves two request classes with different criticality:

- **Redirect** (`GET /{code}`) — user-facing hot path. Availability and latency
  are business-critical.
- **Management API** (`/api/v1/links`) — internal/authenticated. Lower traffic.

## SLIs

| SLI | Definition (Prometheus) |
|-----|-------------------------|
| Availability | `1 - (sum(rate(linkr_http_requests_total{status=~"5.."}[w])) / sum(rate(linkr_http_requests_total[w])))` |
| Redirect latency | `histogram_quantile(0.99, sum(rate(linkr_http_request_duration_seconds_bucket{path="/{code}"}[5m])) by (le))` |

## SLOs (28-day rolling window)

| Objective | Target |
|-----------|--------|
| Availability | 99.9% (error budget: 0.1% ≈ 40 min/28 days) |
| Redirect latency P99 | < 50 ms |
| Redirect latency P50 | < 10 ms |

## Error budget policy
- Budget is measured over a 28-day rolling window.
- **Fast burn** (14.4x) pages on-call; **slow burn** (6x) opens a ticket.
  Both are defined in `prometheus/rules/slo-alerts.yml`.
- If the monthly error budget is exhausted, feature deploys to production are
  frozen until the budget recovers; only reliability fixes are shipped.

## Reporting
Grafana dashboard `observability/grafana/dashboards/linkr.json` renders the
current SLIs, remaining error budget and burn rate.
