# Repo B Improvements for Better Integration

Based on integration experience with Repo A (Agent Starter Kit), here are recommended improvements for Repo B:

## 🔴 Critical Issues

### 1. Authorization Response Missing `policy_version`
**Issue:** The `/authorize` endpoint returns 200 with `decision: "allow"` but doesn't include `policy_version`, causing a KeyError in Repo A.

**Current Behavior:**
```json
{
  "decision": "allow",
  "decision_id": "abc123"
  // Missing: "policy_version"
}
```

**Recommendation:**
Always include `policy_version` in the response, even if it's just `"1.0.0"`:
```json
{
  "decision": "allow",
  "decision_id": "abc123",
  "policy_version": "1.0.0"  // Always include this
}
```

**Impact:** High - Currently causes 500 errors in Repo A

---

### 2. Heartbeat Endpoint Returns 404
**Issue:** The `/functions/v1/heartbeat` endpoint returns 404, suggesting it doesn't exist or the path is incorrect.

**Current Error:**
```
404 Client Error: Not Found for url: https://xxx.supabase.co/functions/v1/heartbeat
```

**Recommendation:**
- Ensure the heartbeat edge function is deployed
- Verify the path is `/functions/v1/heartbeat` (not `/api/heartbeat` or similar)
- Add to BACKEND-SETUP.md deployment list (as noted in code review)

**Impact:** Medium - Heartbeat is best-effort, but kernel registration fails silently

---

## 🟡 Consistency Improvements

### 3. Field Naming Consistency
**Issue:** Repo B accepts camelCase in requests (`kernelId`, `tenantId`) but may return mixed formats.

**Current State:**
- Request: Uses camelCase (`kernelId`, `tenantId`) ✅
- Response: May use snake_case (`policy_version`) or camelCase (`policyVersion`)

**Recommendation:**
Standardize on **camelCase** for all API fields (both request and response):
- Request: `kernelId`, `tenantId` ✅ (already correct)
- Response: `decisionId`, `policyVersion`, `approvalId`, `expiresAt`, `decisionTtlMs`

**Impact:** Low - Repo A handles both, but consistency is better

---

### 4. Required vs Optional Fields Documentation
**Issue:** It's unclear which fields are required vs optional in the authorization response.

**Recommendation:**
Document the response schema clearly:
- **Required:** `decision`, `decisionId`
- **Optional but recommended:** `policyVersion` (defaults to "1.0.0" if missing)
- **Optional:** `approvalId`, `reason`, `policyId`, `expiresAt`, `decisionTtlMs`

---

## 🟢 Nice-to-Have Improvements

### 5. Audit Endpoint Authentication
**Issue:** `/api/audit/ingest` expects Supabase auth token, not kernel API key.

**Recommendation:**
Support kernel API key authentication (HMAC-based) for audit endpoint, similar to `/authorize`.

**Impact:** Low - Currently fails silently (best-effort)

---

### 6. Error Response Format
**Issue:** When authorization fails, error messages could be more descriptive.

**Recommendation:**
Return structured error responses:
```json
{
  "error": "Missing required fields: kernelId, tenantId, action, request_hash",
  "code": "VALIDATION_ERROR",
  "missing_fields": ["kernelId", "tenantId"]
}
```

**Impact:** Low - Helps with debugging

---

## 📋 Summary Priority

1. **High Priority:**
   - ✅ Always include `policy_version` in authorization response
   - ✅ Fix heartbeat endpoint 404

2. **Medium Priority:**
   - ✅ Standardize field naming (camelCase)
   - ✅ Document required vs optional fields

3. **Low Priority:**
   - ✅ Support kernel auth for audit endpoint
   - ✅ Improve error response format

---

## 🔍 Testing Checklist for Repo B

After implementing these changes, verify:

- [ ] `/authorize` always returns `policy_version`
- [ ] `/heartbeat` returns 200 (not 404)
- [ ] All response fields use camelCase consistently
- [ ] Documentation clearly states required vs optional fields
- [ ] Error responses are structured and helpful
