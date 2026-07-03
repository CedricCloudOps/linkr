# Local development

## Requirements
- Python 3.11 or 3.12
- Docker (for the full stack with PostgreSQL and Redis)

## Option A — Python only (SQLite, in-memory cache)
Fastest inner loop. No external services required.
```bash
make install
source .venv/bin/activate
make run            # http://localhost:8000  (docs at /docs)
```

Exercise the API:
```bash
curl -s -X POST localhost:8000/api/v1/links \
  -H 'content-type: application/json' \
  -d '{"url":"https://example.com/some/very/long/path"}'

# follow a redirect and see the 302
curl -si localhost:8000/<code> | head -n 1

# analytics
curl -s localhost:8000/api/v1/links/<code>/stats
```

## Option B — Full stack (PostgreSQL + Redis)
Mirrors production wiring; runs migrations first.
```bash
make up             # docker compose: postgres, redis, migrate, app
make down           # tear down (removes volumes)
```

## Quality gates (run before pushing)
```bash
make lint           # ruff
make security       # bandit + pip-audit
make test           # pytest
```

## Configuration
All settings are environment variables prefixed with `LINKR_` (see
`.env.example`). With no `LINKR_REDIS_URL`, the service uses an in-process cache;
with no PostgreSQL URL it defaults to a local SQLite file.
