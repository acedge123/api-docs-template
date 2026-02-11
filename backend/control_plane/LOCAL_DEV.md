# Local dev: Control Plane (/api/manage)

This repo currently uses **psycopg2** in the `requirements/*` files, which may require local build tooling on macOS.

If you hit errors like:
- `pg_config executable not found`
- `ld: library 'ssl' not found`

…use the steps below.

## 1) Ensure Postgres dev tools are installed (pg_config)

```bash
brew install postgresql@16
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
which pg_config
pg_config --version
```

## 2) Ensure OpenSSL headers/libs are discoverable

```bash
brew install openssl@3
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
```

## 3) Use a venv and always run pip via python

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements/local.txt
```

## 4) Smoke test the endpoint

Run Django and call `meta.actions`:

```bash
cd backend
python manage.py runserver

curl -sS -X POST http://127.0.0.1:8000/api/manage \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: test-key-123' \
  -d '{"action":"meta.actions"}'
```
