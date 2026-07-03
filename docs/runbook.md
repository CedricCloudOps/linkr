# Runbook

On-call reference for `linkr`. Every paging alert links here by anchor.

## Dashboards and access
- Grafana: dashboard `linkr - service overview` (uid `linkr-overview`).
- Logs: `kubectl -n linkr logs deploy/linkr` (JSON on stdout, shipped to the log backend).
- Metrics: Prometheus, job `linkr`.

## Quick triage
```bash
kubectl -n linkr get pods
kubectl -n linkr rollout status deployment/linkr
kubectl -n linkr logs deploy/linkr --tail=200
kubectl -n linkr describe hpa linkr
```

## error-budget-burn
Alert: `LinkrErrorBudgetFastBurn` / `LinkrErrorBudgetSlowBurn` — the 5xx ratio is
consuming the error budget faster than allowed.

1. Confirm scope on the dashboard (all pods vs one; specific endpoint).
2. Check recent changes: `kubectl -n linkr rollout history deployment/linkr`.
3. If a deploy correlates, roll back:
   `kubectl -n linkr rollout undo deployment/linkr`.
4. Check dependencies: PostgreSQL (RDS) and Redis (ElastiCache) health, and
   `SELECT 1` via `/readyz`.
5. If the budget is exhausted, freeze feature deploys per the error-budget policy
   in `observability/slo.md` until it recovers.

## redirect-latency
Alert: `LinkrRedirectLatencyHigh` — redirect P99 above 50 ms.

1. Inspect cache hit ratio on the dashboard. A drop points to Redis.
2. Verify Redis reachability and CPU/evictions in ElastiCache.
3. If Redis is degraded, redirects still resolve from PostgreSQL; scale pods
   (`kubectl -n linkr scale deployment/linkr --replicas=N`) and check RDS load.
4. Confirm HPA is scaling and nodes have capacity.

## instance-down
Alert: `LinkrInstanceDown` — a target is unreachable.

1. `kubectl -n linkr get pods -o wide`; look for CrashLoopBackOff or evictions.
2. `kubectl -n linkr describe pod <pod>` and check recent logs.
3. If node-related, cordon/drain the node and let the scheduler reschedule.

## Rollback
```bash
kubectl -n linkr rollout undo deployment/linkr
kubectl -n linkr rollout status deployment/linkr
```
Images are immutable and tagged by version and commit SHA, so rollbacks are
deterministic.

## Database migrations
Migrations run as a job before the app starts (`alembic upgrade head`). To revert
the last migration: `alembic downgrade -1` from a maintenance pod. Prefer
forward-fixing over destructive downgrades in production.
