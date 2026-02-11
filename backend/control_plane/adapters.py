"""
Stub adapters for ACP — replace with real implementations
"""


class StubAuditAdapter:
    def log(self, entry):
        pass  # TODO: persist to AuditLog model


class StubIdempotencyAdapter:
    def __init__(self):
        self._cache = {}

    def get_replay(self, tenant_id, action, idempotency_key):
        key = f"{tenant_id}:{action}:{idempotency_key}"
        return self._cache.get(key)

    def store_replay(self, tenant_id, action, idempotency_key, response):
        key = f"{tenant_id}:{action}:{idempotency_key}"
        self._cache[key] = response


class StubRateLimitAdapter:
    def check(self, api_key_id, action, limit):
        return {"allowed": True, "limit": limit, "remaining": limit - 1}


class StubCeilingsAdapter:
    def check(self, action, params, tenant_id):
        pass  # No ceilings enforced by default
