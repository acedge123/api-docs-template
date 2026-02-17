"""
Test action to verify Repo C integration

Add this to your leadscoring pack to test the executor adapter.
"""

from control_plane.acp.types import ActionDef


def handle_test_repo_c(params, ctx):
    """
    Test action that calls Repo C via executor adapter
    
    This verifies:
    - Executor adapter is configured
    - Repo C authentication works
    - End-to-end execution flow
    """
    executor = ctx.get('executor')
    if not executor:
        raise ValueError("Executor not configured. Check CIA_URL and CIA_SERVICE_KEY environment variables.")
    
    tenant_id = ctx['tenant_id']
    bindings = ctx.get('bindings', {})
    kernel_id = bindings.get('kernelId', 'leadscore-kernel')
    
    # Test: Call Repo C to list CIQ publishers
    # This requires:
    # 1. Tenant configured in Repo C tenant_integrations table
    # 2. CIQ secret in Supabase Vault
    # 3. Action allowlisted in Repo C
    
    try:
        result = executor.execute(
            endpoint=f"/api/tenants/{tenant_id}/ciq/publishers.list",
            params={},
            tenant_id=tenant_id,
            trace={
                'kernel_id': kernel_id,
                'actor_id': ctx.get('api_key_id'),
            }
        )
        
        return {
            "data": {
                "message": "Successfully called Repo C",
                "repo_c_status": "success",
                "repo_c_response": result.data,
                "resource_type": result.resource_type,
                "count": result.count,
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": f"Repo C call failed: {str(e)}",
            "code": "REPO_C_ERROR",
        }


# Add this to your leadscoring pack:
TEST_REPO_C_ACTION = ActionDef(
    name="test.repo_c.ciq.publishers.list",
    scope="manage.read",
    description="Test action to verify Repo C (Key Vault Executor) integration. Requires tenant configured in Repo C.",
    params_schema={"type": "object", "properties": {}},
    supports_dry_run=False,
)
