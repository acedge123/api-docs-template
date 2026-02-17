"""
Audit adapter that sends events to Repo B (Governance Hub)

This replaces the StubAuditAdapter to send audit events to Repo B's /api/audit/ingest endpoint.
"""

import json
import os
import uuid
from typing import Any, Dict, Optional

import requests


class RepoBAuditAdapter:
    """Audit adapter that sends events to Repo B"""
    
    def __init__(self, governance_url: Optional[str] = None, kernel_id: Optional[str] = None,
                 kernel_api_key: Optional[str] = None):
        """
        Initialize audit adapter
        
        Args:
            governance_url: Repo B base URL (optional, will use env var if not provided)
            kernel_id: Kernel ID (optional, will use env var if not provided)
            kernel_api_key: Kernel API key for authentication (optional, will use env var if not provided)
        """
        # Support both ACP_BASE_URL (new standard) and GOVERNANCE_HUB_URL (legacy)
        self.governance_url = (governance_url or os.environ.get('ACP_BASE_URL') or os.environ.get('GOVERNANCE_HUB_URL', '')).rstrip('/')
        self.kernel_id = kernel_id or os.environ.get('KERNEL_ID', 'leadscore-kernel')
        self.kernel_api_key = kernel_api_key or os.environ.get('ACP_KERNEL_KEY')
        self.integration = 'leadscore'
    
    def _sanitize(self, obj: Any) -> Any:
        """Remove sensitive fields from object"""
        if isinstance(obj, dict):
            sensitive_keys = {'authorization', 'cookie', 'x-api-key', 'token', 
                            'access_token', 'refresh_token', 'client_secret', 
                            'api_key', 'password', 'secret'}
            return {
                k: '[REDACTED]' if k.lower() in sensitive_keys else self._sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [self._sanitize(item) for item in obj]
        else:
            return obj
    
    def _canonical_json(self, obj: Any) -> str:
        """Convert object to canonical JSON string (deterministic)"""
        if obj is None:
            return 'null'
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))
    
    def _hash_payload(self, payload: str) -> str:
        """Compute SHA-256 hash of payload"""
        import hashlib
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    def log(self, entry: Dict) -> None:
        """
        Send audit event to Repo B
        
        This is best-effort - failures should not block the main request
        """
        if not self.governance_url:
            # If Repo B not configured, silently skip (like stub)
            return
        
        # Validate tenant_id is a UUID before sending to Repo B
        tenant_id = entry.get('tenant_id') or entry.get('tenantId')  # Support both snake_case and camelCase
        if not tenant_id or tenant_id == '':
            # Empty string or None - don't send to Repo B (would cause UUID validation error)
            print(f"⚠️ Audit skipped: tenant_id is empty or not provided. Set ACP_TENANT_ID to the tenant UUID from Repo B.")
            return
        
        # Strip whitespace
        tenant_id = str(tenant_id).strip()
        
        if tenant_id:
            try:
                # Try to parse as UUID to validate format
                uuid.UUID(tenant_id)
            except (ValueError, TypeError):
                # Not a valid UUID - don't send to Repo B (would cause database error)
                print(f"⚠️ Audit skipped: tenant_id '{tenant_id}' is not a valid UUID. Set ACP_TENANT_ID to the tenant UUID from Repo B.")
                return
        
        try:
            # Extract pack from action name (e.g., "domain.leadscoring.models.create" -> "leadscoring")
            action = entry.get('action', '')
            pack = 'leadscoring' if 'leadscoring' in action else 'meta' if action.startswith('meta.') else 'unknown'
            
            # Create request hash if params available
            request_hash = None
            if 'params' in entry:
                sanitized = self._sanitize(entry['params'])
                canonical = self._canonical_json(sanitized)
                request_hash = self._hash_payload(canonical)
            
            # Build audit event in Repo B format (matches AuditEvent interface)
            import time
            start_time = entry.get('start_time')  # If we track request start time
            latency_ms = None
            if start_time:
                latency_ms = int((time.time() - start_time) * 1000)
            
            audit_event = {
                'event_id': str(uuid.uuid4()),
                'schema_version': 1,
                'ts': int(time.time() * 1000),  # Unix timestamp in milliseconds
                'tenant_id': tenant_id,  # Use validated UUID (already validated above)
                'integration': self.integration,
                'pack': pack,
                'action': action,
                'actor': {
                    'type': entry.get('actor_type', 'api_key'),
                    'id': entry.get('actor_id', 'unknown'),
                    # Note: api_key_id not in Repo B schema, only type and id
                },
                'request_hash': request_hash or '',
                'status': 'success' if entry.get('result') == 'success' else 
                         'error' if entry.get('result') == 'error' else 
                         'denied' if entry.get('result') == 'denied' else 'unknown',
            }
            
            # Add optional fields only if they have values
            if latency_ms is not None:
                audit_event['latency_ms'] = latency_ms
            
            if entry.get('policy_decision_id'):
                audit_event['policy_decision_id'] = entry.get('policy_decision_id')
            
            # Send to Repo B (async, best-effort)
            url = f"{self.governance_url}/functions/v1/audit-ingest"
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Add kernel API key if available (Repo B may need to accept this)
            if self.kernel_api_key:
                headers['Authorization'] = f'Bearer {self.kernel_api_key}'
            
            # Fire and forget - don't wait for response
            try:
                requests.post(url, headers=headers, json=audit_event, timeout=2)
            except:
                # Silently fail - audit is best-effort
                pass
                
        except Exception as e:
            # Log error but don't raise - audit should never block requests
            print(f"Audit logging error (non-fatal): {e}")
