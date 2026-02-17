# Repo C Environment Variables Setup (Leadscore)

## Where to Add Environment Variables

**Railway Dashboard → Your Project → Variables Tab**

Add these environment variables:

```bash
# Repo C (Key Vault Executor) Configuration
CIA_URL=https://rrzewykkwjdkkccwrjyf.supabase.co
CIA_ANON_KEY=your-supabase-anon-key-here
CIA_SERVICE_KEY=cia_service_xxxxx  # Generated service key from Repo C UI
KERNEL_ID=leadscore-kernel

# Repo B (Governance Hub) Configuration (optional - if using governance)
GOVERNANCE_HUB_URL=https://your-governance-hub.supabase.co
ACP_KERNEL_KEY=acp_kernel_xxxxx  # Generated kernel API key from Repo B
```

## Steps

1. **Go to Railway Dashboard**
   - https://railway.app
   - Select your `api-docs-template` project

2. **Navigate to Variables**
   - Click on your service
   - Go to "Variables" tab

3. **Add Variables**
   - Click "New Variable"
   - Add each variable one by one:
     - `CIA_URL` = `https://rrzewykkwjdkkccwrjyf.supabase.co`
     - `CIA_ANON_KEY` = (Get from Repo C Supabase dashboard → Settings → API → anon/public key)
     - `CIA_SERVICE_KEY` = (Generated from Repo C UI → Service Keys)
     - `KERNEL_ID` = `leadscore-kernel`
     - `GOVERNANCE_HUB_URL` = (Your Repo B URL, if using governance)
     - `ACP_KERNEL_KEY` = (Generated kernel API key from Repo B, if using governance)

4. **Redeploy**
   - Railway will automatically redeploy when you add variables
   - Or manually trigger a redeploy from the Deployments tab

## Getting the Values

### CIA_URL
Already set: `https://rrzewykkwjdkkccwrjyf.supabase.co`

### CIA_ANON_KEY
1. Go to Repo C Supabase project: https://supabase.com/dashboard/project/rrzewykkwjdkkccwrjyf
2. Settings → API
3. Copy the "anon" or "public" key

### CIA_SERVICE_KEY
1. Go to Repo C UI (or generate via script)
2. Create a new service key named "leadscore-service-key"
3. Copy the generated key (shown once)

### KERNEL_ID
Set to: `leadscore-kernel`

### GOVERNANCE_HUB_URL (Optional - if using Repo B)
1. Get your Repo B (Governance Hub) Supabase project URL
2. Format: `https://your-project-id.supabase.co`

### ACP_KERNEL_KEY (Optional - if using Repo B)
1. Generate a kernel API key (format: `acp_kernel_xxxxx`)
2. Register the kernel in Repo B via `/heartbeat` endpoint
3. Compute HMAC hash and store in Repo B `kernels` table
4. Use the raw key value here (not the hash)

## Next Steps

After adding these variables, you'll need to update the router to use the executor adapter. See `backend/control_plane/views.py` to add the executor.
