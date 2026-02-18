"""
Usage endpoint for checking API usage and limits
"""

import json
import os
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.authtoken.models import Token

from control_plane.control_plane_adapter import HttpControlPlaneAdapter

User = get_user_model()


@csrf_exempt
@require_http_methods(["GET"])
def get_usage(request):
    """
    GET /api/usage
    
    Get usage statistics for the authenticated tenant.
    
    Requires X-API-Key header for authentication.
    
    Optional query parameters:
    - period_start: ISO timestamp (defaults to start of current month)
    - period_end: ISO timestamp (defaults to now)
    
    Returns:
    {
        "ok": true,
        "tenant_uuid": "be1b7614-60ad-4e77-8661-cb4fcba9b314",
        "tier": "free",
        "calls_used": 45,
        "calls_limit": 100,
        "calls_remaining": 55,
        "period_start": "2026-02-01T00:00:00Z",
        "period_end": "2026-02-17T21:00:00Z"
    }
    """
    # Authenticate via API key
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if not api_key or not api_key.strip():
        return JsonResponse(
            {"ok": False, "error": "Missing or invalid X-API-Key", "code": "INVALID_API_KEY"},
            status=401,
        )
    
    try:
        token = Token.objects.select_related("user").get(key=api_key.strip())
        user = token.user
    except Token.DoesNotExist:
        return JsonResponse(
            {"ok": False, "error": "Invalid API key", "code": "INVALID_API_KEY"},
            status=401,
        )
    
    # Get tenant UUID from environment or user profile
    # For now, we'll need to get it from environment variable
    # In production, you might store tenant_uuid in a UserProfile model
    tenant_uuid = os.environ.get('ACP_TENANT_ID') or os.environ.get('GOVERNANCE_TENANT_ID')
    
    if not tenant_uuid:
        return JsonResponse(
            {
                "ok": False,
                "error": "Tenant UUID not configured. Set ACP_TENANT_ID environment variable.",
                "code": "CONFIGURATION_ERROR",
            },
            status=500,
        )
    
    # Get period from query parameters or use defaults
    period_start = request.GET.get('period_start')
    period_end = request.GET.get('period_end')
    
    # Initialize control plane adapter
    governance_url = os.environ.get('ACP_BASE_URL') or os.environ.get('GOVERNANCE_HUB_URL')
    kernel_api_key = os.environ.get('ACP_KERNEL_KEY')
    
    if not governance_url or not kernel_api_key:
        return JsonResponse(
            {
                "ok": False,
                "error": "Usage service not configured. ACP_BASE_URL and ACP_KERNEL_KEY must be set.",
                "code": "CONFIGURATION_ERROR",
            },
            status=500,
        )
    
    control_plane = HttpControlPlaneAdapter(
        platform_url=governance_url,
        kernel_api_key=kernel_api_key,
    )
    
    # Query usage from Repo B
    try:
        usage = control_plane.get_usage(
            tenant_id=tenant_uuid,
            period_start=period_start,
            period_end=period_end,
        )
        
        return JsonResponse({
            "ok": True,
            "tenant_uuid": usage.tenant_id,
            "tier": usage.tier,
            "calls_used": usage.calls_used,
            "calls_limit": usage.calls_limit,
            "calls_remaining": usage.calls_remaining,
            "period_start": usage.period_start,
            "period_end": usage.period_end,
        })
    except Exception as e:
        return JsonResponse(
            {
                "ok": False,
                "error": f"Failed to retrieve usage: {str(e)}",
                "code": "USAGE_QUERY_ERROR",
            },
            status=500,
        )
