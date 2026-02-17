# End-to-End Test Plan: Repo A → Repo B → Repo C

## Current State

- ✅ **Repo A (leadscore)**: Python router with executor adapter support
- ✅ **Repo B (governance-hub)**: Policy authority (optional for now)
- ✅ **Repo C (key-vault-executor)**: Key vault + executor
- ⚠️ **Leadscoring pack**: Uses Django models directly (doesn't use Repo C)

## Test Strategy

### Phase 1: Test Repo A Alone (No Repo C/B)
**Purpose:** Verify basic Repo A functionality

```bash
# Test meta actions
curl -X POST https://YOUR_RAILWAY_DOMAIN.railway.app/api/manage \
  -H "X-API-Key: YOUR_DRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "meta.actions"}'

# Test leadscoring action (uses Django, not Repo C)
curl -X POST https://YOUR_RAILWAY_DOMAIN.railway.app/api/manage \
  -H "X-API-Key: YOUR_DRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "domain.leadscoring.models.list"}'
```

**Expected:** Both should work (no Repo C/B involved)

---

### Phase 2: Test Repo A → Repo C (No Repo B)
**Purpose:** Verify executor adapter works

**Option A: Use existing CIQ action (if tenant configured)**

If you have a tenant configured in Repo C with CIQ integration:

```bash
curl -X POST https://YOUR_RAILWAY_DOMAIN.railway.app/api/manage \
  -H "X-API-Key: YOUR_DRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "test.ciq.publishers.list",
    "params": {}
  }'
```

**Option B: Add a test action to leadscoring pack**

Add this to `backend/control_plane/packs.py`:

```python
def handle_test_repo_c(params, ctx):
    """Test action that calls Repo C"""
    executor = ctx.get('executor')
    if not executor:
        raise ValueError("Executor not configured")
    
    tenant_id = ctx['tenant_id']
    
    # Call Repo C via executor
    result = executor.execute(
        endpoint=f"/api/tenants/{tenant_id}/ciq/publishers.list",
        params={},
        tenant_id=tenant_id,
        trace={
            'kernel_id': ctx.get('bindings', {}).get('kernelId', 'leadscore-kernel'),
            'actor_id': ctx.get('api_key_id'),
        }
    )
    
    return {
        "data": {
            "message": "Successfully called Repo C",
            "repo_c_response": result.data,
            "resource_type": result.resource_type,
        }
    }

# Add to actions list:
ActionDef(
    name="test.repo_c.ciq.publishers.list",
    scope="manage.read",
    description="Test action to verify Repo C integration",
    params_schema={"type": "object", "properties": {}},
    supports_dry_run=False,
),

# Add to handlers:
"test.repo_c.ciq.publishers.list": handle_test_repo_c,
```

**Prerequisites:**
1. Tenant configured in Repo C `tenant_integrations` table
2. CIQ secret configured in Supabase Vault
3. Service key generated and in Railway env vars

---

### Phase 3: Test Repo A → Repo B → Repo C (Full Flow)
**Purpose:** Verify governance + execution flow

**Steps:**
1. Register kernel in Repo B via `/heartbeat`
2. Create a policy in Repo B (optional - default is allow)
3. Call a write action that triggers authorization

**Test:**
```bash
# This would need a write action that:
# 1. Calls Repo B /authorize
# 2. If allowed, calls Repo C /execute
# 3. Returns result

curl -X POST https://YOUR_RAILWAY_DOMAIN.railway.app/api/manage \
  -H "X-API-Key: YOUR_DRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "test.repo_c.ciq.campaigns.create",
    "params": {"name": "Test Campaign"}
  }'
```

**Prerequisites:**
1. All Phase 2 prerequisites
2. Repo B configured (`GOVERNANCE_HUB_URL`, `ACP_KERNEL_KEY`)
3. Kernel registered in Repo B
4. Control plane adapter implemented in Python (not done yet)

---

## Recommended Approach

### Quick Test (5 minutes)
**Just test Repo A works:**
- Run Phase 1 tests
- Verify existing leadscoring actions work
- This confirms Repo A infrastructure is solid

### Full Integration Test (30 minutes)
**Test Repo A → Repo C:**
1. Add test action to leadscoring pack (see Phase 2, Option B)
2. Configure tenant in Repo C
3. Test the action
4. Verify it calls Repo C successfully

### Complete Flow Test (1 hour)
**Test Repo A → Repo B → Repo C:**
1. Implement control plane adapter for Python
2. Register kernel in Repo B
3. Test write action with governance

---

## What I Recommend

**Start with Phase 1** - Just have your agent try the existing leadscoring actions. This will:
- ✅ Verify Repo A is working
- ✅ Confirm environment variables are set correctly
- ✅ Test the basic infrastructure

**Then add Phase 2** - Add a simple test action that calls Repo C to verify:
- ✅ Executor adapter works
- ✅ Repo C authentication works
- ✅ End-to-end execution flow

**Phase 3 can wait** - Full governance flow requires implementing the control plane adapter in Python, which is more complex.

---

## Quick Test Script

Save this as `test-repo-a.sh`:

```bash
#!/bin/bash

RAILWAY_DOMAIN="your-railway-domain.railway.app"
API_KEY="your-drf-token"

echo "Testing Repo A - Meta Actions..."
curl -X POST "https://${RAILWAY_DOMAIN}/api/manage" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action": "meta.actions"}' | jq .

echo -e "\n\nTesting Repo A - Leadscoring List..."
curl -X POST "https://${RAILWAY_DOMAIN}/api/manage" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"action": "domain.leadscoring.models.list"}' | jq .
```

Run: `chmod +x test-repo-a.sh && ./test-repo-a.sh`
