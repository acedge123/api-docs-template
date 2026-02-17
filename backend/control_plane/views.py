"""
ACP /manage endpoint view
"""

import json
import os

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
from control_plane.repo_b_audit_adapter import RepoBAuditAdapter
from control_plane.executor_adapter import HttpExecutorAdapter
from control_plane.control_plane_adapter import HttpControlPlaneAdapter
from control_plane.packs import leadscoring_pack

# Initialize router once
_router = None
_control_plane = None


def _send_heartbeat():
    """Send heartbeat to Repo B on startup"""
    global _control_plane
    if _control_plane:
        kernel_id = os.environ.get('KERNEL_ID', 'leadscore-kernel')
        result = _control_plane.heartbeat(
            kernel_id=kernel_id,
            version='1.0.0',
            packs=['leadscoring'],
            env=os.environ.get('ENVIRONMENT', 'production')
        )
        if result.get('ok'):
            print(f"✅ Kernel registered with Repo B: {kernel_id}")
        else:
            print(f"⚠️ Heartbeat failed: {result.get('error')}")


def _get_router():
    global _router, _control_plane
    if _router is None:
        # Create executor adapter (Repo C) if configured
        executor = None
        cia_url = os.environ.get('CIA_URL')
        cia_service_key = os.environ.get('CIA_SERVICE_KEY')
        if cia_url and cia_service_key:
            executor = HttpExecutorAdapter(
                cia_url=cia_url,
                cia_service_key=cia_service_key,
                cia_anon_key=os.environ.get('CIA_ANON_KEY'),
                kernel_id=os.environ.get('KERNEL_ID', 'leadscore-kernel'),
            )
        
        # Create control plane adapter (Repo B) if configured
        governance_url = os.environ.get('GOVERNANCE_HUB_URL')
        kernel_api_key = os.environ.get('ACP_KERNEL_KEY')
        if governance_url and kernel_api_key:
            _control_plane = HttpControlPlaneAdapter(
                platform_url=governance_url,
                kernel_api_key=kernel_api_key,
            )
            # Send heartbeat on startup
            try:
                _send_heartbeat()
            except Exception as e:
                print(f"⚠️ Heartbeat error (non-fatal): {e}")
        
        # Create bindings with kernel_id and governance tenant UUID
        # governanceTenantId is the UUID registered in Repo B during onboarding
        bindings = {
            'kernelId': os.environ.get('KERNEL_ID', 'leadscore-kernel'),
            'integration': 'leadscore',
            'governanceTenantId': os.environ.get('GOVERNANCE_TENANT_ID'),  # Tenant UUID from Repo B
        }
        
        # Create audit adapter (send to Repo B if configured, otherwise stub)
        governance_url = os.environ.get('GOVERNANCE_HUB_URL')
        kernel_api_key = os.environ.get('ACP_KERNEL_KEY')
        if governance_url and kernel_api_key:
            audit_adapter = RepoBAuditAdapter(
                governance_url=governance_url,
                kernel_id=bindings['kernelId'],
                kernel_api_key=kernel_api_key
            )
        else:
            audit_adapter = StubAuditAdapter()
        
        _router = create_manage_router(
            audit_adapter=audit_adapter,
            idempotency_adapter=StubIdempotencyAdapter(),
            rate_limit_adapter=StubRateLimitAdapter(),
            ceilings_adapter=StubCeilingsAdapter(),
            bindings=bindings,
            packs=[leadscoring_pack],
            executor=executor,  # Pass executor if available
            control_plane=_control_plane,  # Pass control plane if available
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

    try:
        router = _get_router()
        response = router(body, meta)
    except Exception as e:
        # Log the exception for debugging
        import traceback
        print(f"❌ Error in manage_endpoint: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse(
            {
                "ok": False,
                "error": f"Internal server error: {str(e)}",
                "code": "INTERNAL_ERROR",
            },
            status=500,
        )

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
