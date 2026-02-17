# Security Fix: Authorization Check Bypass

## Issue Found

**Date**: 2026-02-17  
**Severity**: CRITICAL  
**Status**: FIXED

## Problem

When an agent called `domain.leadscoring.questions.upsert_bulk` to add a question, the action was **allowed without authorization** even though:
1. Governance Hub (Repo B) was configured
2. The action has scope `"manage.domain"` (a write action)
3. Authorization should have been checked

## Root Cause

In `backend/control_plane/acp/router.py`, the authorization check had a bug:

```python
# OLD CODE (BUGGY):
if control_plane and not dry_run and required_scope in ("manage.domain", "manage.write"):
    # Check if this is a write action (create, update, delete, cancel)
    is_write_action = any(keyword in action.lower() for keyword in ['create', 'update', 'delete', 'cancel'])
    
    if is_write_action:  # ❌ This was False for "upsert_bulk"!
        # Authorization check...
```

**The bug**: The code checked for keywords `'create', 'update', 'delete', 'cancel'` in the action name, but `"upsert_bulk"` doesn't contain any of these, so `is_write_action` was `False`, and authorization was **skipped entirely**.

## Why This Happened

The action `domain.leadscoring.questions.upsert_bulk`:
- Has scope `"manage.domain"` (which is a write scope)
- But the action name contains `"upsert"`, not `"create"` or `"update"`
- So the keyword check failed, and authorization was bypassed

## The Fix

**Changed logic**: Since we're already checking that `required_scope in ("manage.domain", "manage.write")`, we know this IS a write action. The scope is authoritative - no need to check action name keywords.

```python
# NEW CODE (FIXED):
if control_plane and not dry_run and required_scope in ("manage.domain", "manage.write"):
    # Since we're already inside the scope check, this IS a write action
    # No need to check action name keywords - scope is authoritative
    try:
        # Authorization check...
```

**Result**: Now ALL actions with scope `"manage.domain"` or `"manage.write"` are properly authorized, regardless of action name.

## What Should Have Happened

1. Agent calls `domain.leadscoring.questions.upsert_bulk`
2. Router checks scope: `"manage.domain"` ✅ (write action)
3. Router calls Governance Hub `/authorize` endpoint
4. Governance Hub returns 401 (auth failed - HMAC issue)
5. Router catches exception and **fails closed** (denies action)
6. Question is NOT created

## What Actually Happened

1. Agent calls `domain.leadscoring.questions.upsert_bulk`
2. Router checks scope: `"manage.domain"` ✅
3. Router checks action name keywords: `"upsert"` not in list ❌
4. `is_write_action = False`
5. Authorization check **skipped entirely**
6. Question was created without authorization ❌

## Impact

- **Security**: Write actions were allowed without authorization check
- **Compliance**: Governance policies were not enforced
- **Audit**: No authorization decision logged

## Verification

After fix:
1. All actions with scope `"manage.domain"` or `"manage.write"` will be authorized
2. If Governance Hub is unreachable or returns error, action will be denied (fail-closed)
3. Authorization decisions will be logged in audit events

## Next Steps

1. ✅ Fix applied to `router.py`
2. ⏳ Deploy fix to production
3. ⏳ Test with Governance Hub HMAC auth fixed
4. ⏳ Verify authorization is working end-to-end
5. ⏳ Monitor audit logs to confirm authorization checks are happening

## Related Issues

- Governance Hub edge functions need HMAC kernel authentication (being fixed separately)
- Heartbeat endpoint needs to be deployed (404 error)
