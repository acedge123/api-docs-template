# Troubleshooting Environment Variables in Railway

## Issue: ACP_TENANT_ID Not Detected

If you're getting errors about `ACP_TENANT_ID` missing even though you've set it in Railway, check these:

### 1. Verify Variable is Set at Service Level

In Railway, environment variables can be set at:
- **Project level** (applies to all services)
- **Service level** (applies to specific service)

**Check:**
1. Go to Railway Dashboard → Your Project
2. Click on your **service** (not the project)
3. Go to **Variables** tab
4. Verify `ACP_TENANT_ID` is listed there

**If it's only at project level:**
- Copy it to the service level, OR
- Make sure your service inherits project variables

### 2. Redeploy After Setting Variables

Railway requires a redeploy for new environment variables to take effect.

**Steps:**
1. After setting `ACP_TENANT_ID`, trigger a redeploy:
   - Go to **Deployments** tab
   - Click **Redeploy** on the latest deployment
   - OR push a new commit to trigger auto-deploy

### 3. Check for Whitespace/Quotes

Environment variables in Railway should **not** have quotes around them.

**Wrong:**
```
ACP_TENANT_ID="be1b7614-60ad-4e77-8661-cb4fcba9b314"
```

**Correct:**
```
ACP_TENANT_ID=be1b7614-60ad-4e77-8661-cb4fcba9b314
```

### 4. Verify Variable Name

Check for typos:
- ✅ `ACP_TENANT_ID` (correct)
- ❌ `ACP_TENANTID` (missing underscore)
- ❌ `ACP_TENANT` (missing _ID)
- ❌ `ACPTENANT_ID` (missing underscore)

### 5. Check Railway Logs

After redeploying, check the logs for:
- `✅ Found tenant ID from env: ...` (success)
- `⚠️ WARNING: ACP_TENANT_ID and GOVERNANCE_TENANT_ID are not set` (failure)
- `⚠️ DEBUG: ACP_TENANT_ID not found. Available related env vars: ...` (shows what's available)

### 6. Verify UUID Format

The tenant ID must be a valid UUID format:
- ✅ `be1b7614-60ad-4e77-8661-cb4fcba9b314`
- ❌ `2` (not a UUID)
- ❌ `be1b7614-60ad-4e77-8661` (incomplete)

### 7. Test Locally

To verify the variable is accessible:

```bash
# In Railway, go to your service → Settings → Shell
# Or use Railway CLI
railway run python manage.py shell

# Then in Python shell:
import os
print(os.environ.get('ACP_TENANT_ID'))
```

### 8. Common Railway Issues

**Issue:** Variable set but not accessible
- **Solution:** Check if variable is in the correct service/environment

**Issue:** Variable works locally but not in Railway
- **Solution:** Railway might need a redeploy

**Issue:** Variable has value but validation fails
- **Solution:** Check for whitespace, quotes, or invalid UUID format

## Quick Checklist

- [ ] Variable is set at **service level** (not just project level)
- [ ] Variable name is exactly `ACP_TENANT_ID` (no typos)
- [ ] Variable value is a valid UUID (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
- [ ] No quotes around the value
- [ ] Service has been **redeployed** after setting the variable
- [ ] Check Railway logs for debug messages

## Getting the Tenant UUID

1. Go to Repo B (Governance Hub) UI
2. Navigate to **Organizations**
3. Open your organization's detail drawer
4. Find your tenant (e.g., "leadscore" or "ciq automations")
5. Copy the tenant UUID (format: `be1b7614-60ad-4e77-8661-cb4fcba9b314`)

## Still Not Working?

1. Check Railway logs for the debug messages we added
2. Verify the variable appears in the logs: `Available related env vars: [...]`
3. Try using the legacy name: `GOVERNANCE_TENANT_ID` (for backward compatibility)
4. Contact support with:
   - Railway service name
   - Screenshot of Variables tab
   - Logs showing the error
