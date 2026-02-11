# Control Plane — ACP /manage endpoint

Adds a POST `/api/manage` endpoint conforming to the [agentic-control-plane-kit spec](https://github.com/The-Gig-Agency/agentic-control-plane-kit).

## Quick test

```bash
# Start Django (e.g. make run or python manage.py runserver)
curl -X POST http://localhost:8000/api/manage \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{"action": "meta.actions"}'
```

## Auth

Currently accepts any non-empty `X-API-Key` header (stub). Replace `_get_api_key` in `acp/router.py` with real API key lookup when ready.

## Conformance

Run from agentic-control-plane-kit:

```bash
ACP_BASE_URL=http://localhost:8000/api/manage ACP_API_KEY=test-key-123 npm run test:conformance
```
