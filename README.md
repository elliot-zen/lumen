# lumen

Monorepo for the Lumen learning-note pipeline.

## Layout

- `apps/api`: FastAPI service and worker entrypoints
- `apps/web`: frontend app placeholder
- `packages/domain`: shared domain types and dedupe rules
- `packages/notes-platform`: notes platform adapter contract
- `deployment`: local middleware and environment wiring

## Local middleware

Start Postgres:

```bash
docker compose -f deployment/docker-compose.yaml up -d
```

## Run tests

```bash
uv run pytest -q
```

## API and worker

Run the API:

```bash
uv run python scripts/run_api.py
```

Run the worker:

```bash
uv run python scripts/run_worker.py
```

## Environment

Common environment variables:

```bash
export LUMEN_DATABASE_URL=postgresql+psycopg://lumen:lumen@localhost:5432/lumen
export LUMEN_OBSIDIAN_CLI_COMMAND="$HOME/.local/bin/obsidian"
export LUMEN_OBSIDIAN_VAULT_NAME="moon"
```

Optional summarizer configuration:

```bash
export LUMEN_SUMMARIZER_BASE_URL="https://61.160.97.222:15001/k-llm/v1"
export LUMEN_SUMMARIZER_API_KEY="..."
export LUMEN_SUMMARIZER_MODEL="Qwen3.6-35B-A3B"
export LUMEN_SUMMARIZER_VERIFY_SSL="false"
```

## Obsidian smoke test

With the Obsidian desktop app running:

```bash
uv run python scripts/obsidian_smoke.py
```
