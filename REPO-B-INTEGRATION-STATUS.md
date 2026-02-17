# Repo B Integration Status

## ✅ What's Implemented

### 1. Control Plane Adapter (`control_plane_adapter.py`)
- ✅ `HttpControlPlaneAdapter` - Calls Repo B `/authorize` endpoint
- ✅ `heartbeat()` method - Sends heartbeat to Repo B on startup
- ✅ Authorization request/response handling

### 2. Router Updates (`acp/router.py`)
- ✅ Authorization check before write actions (create, update, delete)
- ✅ Calls Repo B `/authorize` for write actions
- ✅ Handles `allow`, `deny`, `require_approval` decisions
- ✅ Fail-closed if Repo B unreachable (for write actions)
- ✅ Passes `policy_decision_id` to audit logs

### 3. Audit Adapter (`repo_b_audit_adapter.py`)
- ✅ `RepoBAuditAdapter` - Sends audit events to Repo B `/api/audit/ingest`
- ✅ Formats events to match Repo B's `AuditEvent` interface
- ✅ Best-effort (doesn't block requests if it fails)

### 4. Views Updates (`views.py`)
- ✅ Initializes control plane adapter from env vars
- ✅ Sends heartbeat on startup
- ✅ Passes control plane to router
- ✅ Uses Repo B audit adapter if configured

## 🔄 Flow for Your Test

When agent adds a question to leadscore:

```
1. Agent → Repo A (/api/manage)
   ↓
2. Repo A validates API key (local)
   ↓
3. Repo A checks if action is write action (create/update/delete)
   ↓
4. [If write] Repo A → Repo B /authorize
   - Sends: kernel_id, tenant_id, actor, action, request_hash
   ↓
5. Repo B evaluates policies → { decision: 'allow' | 'deny' | 'require_approval' }
   ↓
6. [If allowed] Repo A executes handler (Django model save)
   ↓
7. Repo A → Repo B /api/audit/ingest
   - Sends: event with policy_decision_id, status, result_meta
   ↓
8. Repo B stores audit log
   ↓
9. Repo A returns response to agent
```

## ⚠️ Known Issues

### 1. Repo B Audit Authentication
The `/api/audit/ingest` endpoint currently expects Supabase auth token, not kernel API key. You may need to:
- Update Repo B's `audit-ingest` endpoint to accept kernel API keys, OR
- Use a different authentication method

**Workaround:** The audit adapter will try to send with kernel API key. If Repo B rejects it, events will fail silently (best-effort).

### 2. Kernel ID in Audit Events
Repo B's audit service currently uses `event.actor.id` for `kernel_id`, which is incorrect. It should extract `kernel_id` from the authenticated kernel context.

**Impact:** Audit events may have wrong `kernel_id` in Repo B database.

### 3. Organization ID
Repo B's audit-ingest extracts `organization_id` from user metadata. For kernels, you may need to:
- Include `organization_id` in the audit event, OR
- Update Repo B to extract it from kernel authentication

## 🧪 Testing Checklist

### Prerequisites
- [ ] `GOVERNANCE_HUB_URL` set in Railway
- [ ] `ACP_KERNEL_KEY` set in Railway
- [ ] Kernel registered in Repo B (via heartbeat or manual SQL)
- [ ] Policy created in Repo B (optional - default is allow)

### Test Steps

1. **Check Heartbeat on Startup**
   - Deploy to Railway
   - Check logs for: `✅ Kernel registered with Repo B: leadscore-kernel`
   - OR check Repo B `kernels` table for your kernel

2. **Test Write Action (Add Question)**
   ```bash
   curl -X POST https://YOUR_RAILWAY_DOMAIN/api/manage \
     -H "X-API-Key: YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "action": "domain.leadscoring.models.create",
       "params": {"question_id": 1, "weight": 1.0}
     }'
   ```

3. **Verify in Repo B**
   - Check `audit_logs` table in Repo B
   - Should see event with:
     - `kernel_id` = "leadscore-kernel"
     - `action` = "domain.leadscoring.models.create"
     - `status` = "success"
     - `policy_decision_id` = (if authorization was checked)

## 📝 Notes

- **Heartbeat** is sent on Django app startup (when router is first created)
- **Authorization** only happens for write actions (create, update, delete)
- **Audit logging** is best-effort (won't block requests if Repo B is down)
- **Read actions** (list, get) don't call Repo B (faster, no governance needed)

## 🔧 If Things Don't Work

1. **Heartbeat fails:**
   - Check `GOVERNANCE_HUB_URL` and `ACP_KERNEL_KEY` are set
   - Check kernel is registered in Repo B `kernels` table
   - Check Repo B `/heartbeat` endpoint is accessible

2. **Authorization fails:**
   - Check Repo B `/authorize` endpoint is accessible
   - Check kernel API key is valid
   - Check policies in Repo B allow the action

3. **Audit events not appearing:**
   - Check Repo B `/api/audit/ingest` endpoint accepts kernel API keys
   - Check Railway logs for audit errors (they're silent by design)
   - Verify event format matches Repo B's expected schema
