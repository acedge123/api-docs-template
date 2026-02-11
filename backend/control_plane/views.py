"""
ACP /manage endpoint view
"""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from control_plane.acp.router import create_manage_router
from control_plane.adapters import (
    StubAuditAdapter,
    StubCeilingsAdapter,
    StubIdempotencyAdapter,
    StubRateLimitAdapter,
)
from control_plane.packs import leadscoring_pack

# Initialize router once
_router = None


def _get_router():
    global _router
    if _router is None:
        _router = create_manage_router(
            audit_adapter=StubAuditAdapter(),
            idempotency_adapter=StubIdempotencyAdapter(),
            rate_limit_adapter=StubRateLimitAdapter(),
            ceilings_adapter=StubCeilingsAdapter(),
            bindings={},
            packs=[leadscoring_pack],
        )
    return _router


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


@csrf_exempt
@require_http_methods(["POST"])
def manage_endpoint(request):
    """POST /api/manage — ACP control plane."""
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse(
            {"ok": False, "error": "Invalid JSON", "code": "VALIDATION_ERROR"},
            status=400,
        )

    meta = {
        "request": request,
        "ip_address": get_client_ip(request),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
    }

    router = _get_router()
    response = router(body, meta)

    status = 200
    if not response.get("ok"):
        code = response.get("code", "INTERNAL_ERROR")
        if code == "INVALID_API_KEY":
            status = 401
        elif code in ("SCOPE_DENIED", "CEILING_EXCEEDED"):
            status = 403
        elif code == "NOT_FOUND":
            status = 404
        elif code == "RATE_LIMITED":
            status = 429
        elif code == "VALIDATION_ERROR":
            status = 400
        else:
            status = 500

    return JsonResponse(response, status=status)
