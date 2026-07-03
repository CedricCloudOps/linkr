# Contributing

## Workflow
1. Branch from `main` (`feature/...`, `fix/...`).
2. Make the change with tests.
3. Run the quality gates locally: `make lint security test`.
4. Open a pull request. CI must be green before merge.

## Commit messages
Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `refactor:`,
`chore:`. Reference the relevant issue where applicable.

## Code style
- `ruff` enforces linting and import ordering (`make lint`).
- Keep functions small and the service layer free of framework types.
- New behaviour requires tests; keep coverage from regressing.

## Database changes
Model changes require an Alembic migration:
```bash
alembic revision --autogenerate -m "describe change"
```
Review the generated migration and verify `upgrade`/`downgrade` both work.
