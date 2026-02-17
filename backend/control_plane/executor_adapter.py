"""
ExecutorAdapter - Interface for calling external services (Repo C)

This allows packs to delegate execution to external services while
maintaining governance through the kernel.
"""

import hashlib
import json
import os
import re
from typing import Any, Dict, Optional

import requests


class ExecutorResponse:
    """Response from executor adapter"""
    def __init__(self, data: Any, resource_ids: Optional[list] = None, 
                 resource_type: Optional[str] = None, count: Optional[int] = None):
        self.data = data
        self.resource_ids = resource_ids
        self.resource_type = resource_type
        self.count = count


class ExecutorAdapter:
    """Interface for executing actions via external services"""
    
    def execute(self, endpoint: str, params: Dict[str, Any], tenant_id: str,
                trace: Optional[Dict[str, str]] = None) -> ExecutorResponse:
        """
        Execute an action via external service
        
        Args:
            endpoint: Endpoint path (e.g., "/api/tenants/{tenantId}/shopify/products.create")
            params: Action parameters
            tenant_id: Tenant ID for the request
            trace: Optional trace information (kernel_id, policy_decision_id, actor_id)
        
        Returns:
            ExecutorResponse with data and metadata
        """
        raise NotImplementedError


class HttpExecutorAdapter(ExecutorAdapter):
    """HTTP implementation of ExecutorAdapter - Calls Repo C /api/execute endpoint"""
    
    def __init__(self, cia_url: str, cia_service_key: str, 
                 cia_anon_key: Optional[str] = None, kernel_id: Optional[str] = None):
        """
        Initialize HTTP executor adapter
        
        Args:
            cia_url: Repo C base URL (e.g., https://xxx.supabase.co)
            cia_service_key: CIA_SERVICE_KEY for authentication
            cia_anon_key: Supabase anon key (required for Supabase Edge Functions)
            kernel_id: Optional kernel ID for trace
        """
        self.cia_url = cia_url.rstrip('/')
        self.cia_service_key = cia_service_key
        self.cia_anon_key = cia_anon_key
        self.kernel_id = kernel_id
    
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
        if isinstance(obj, (str, int, float, bool)):
            return json.dumps(obj, sort_keys=True, separators=(',', ':'))
        if isinstance(obj, dict):
            # Sort keys and recursively canonicalize values
            sorted_items = sorted(obj.items())
            canonical_dict = {k: json.loads(self._canonical_json(v)) for k, v in sorted_items}
            return json.dumps(canonical_dict, sort_keys=True, separators=(',', ':'))
        if isinstance(obj, list):
            canonical_list = [json.loads(self._canonical_json(item)) for item in obj]
            return json.dumps(canonical_list, sort_keys=True, separators=(',', ':'))
        # Fallback to JSON stringify
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))
    
    def _hash_payload(self, payload: str) -> str:
        """Compute SHA-256 hash of payload"""
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    def execute(self, endpoint: str, params: Dict[str, Any], tenant_id: str,
                trace: Optional[Dict[str, str]] = None) -> ExecutorResponse:
        """
        Execute an action via Repo C
        
        Args:
            endpoint: Endpoint path (e.g., "/api/tenants/{tenantId}/shopify/products.create")
            params: Action parameters
            tenant_id: Tenant ID for the request
            trace: Optional trace information (kernel_id, policy_decision_id, actor_id)
        
        Returns:
            ExecutorResponse with data and metadata
        """
        # Extract integration and action from endpoint
        # e.g., "/api/tenants/{tenantId}/shopify/products.create" -> integration: "shopify", action: "products.create"
        match = re.search(r'/(shopify|ciq|leadscore)/(.+)$', endpoint)
        if not match:
            raise ValueError(f"Invalid endpoint format: {endpoint}. Expected pattern: /api/tenants/{{tenantId}}/{{integration}}/{{action}}")
        
        integration = match.group(1)
        action = match.group(2)
        
        # Create request hash (sanitized, canonical JSON)
        sanitized_params = self._sanitize(params)
        canonical_params = self._canonical_json(sanitized_params)
        request_hash = self._hash_payload(canonical_params)
        
        # Call Repo C /api/execute
        full_url = f"{self.cia_url}/functions/v1/execute"
        
        # Build headers - Supabase Edge Functions require apikey header
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.cia_service_key}',
        }
        
        # Add apikey header if provided (required for Supabase Edge Functions)
        if self.cia_anon_key:
            headers['apikey'] = self.cia_anon_key
        
        # Build request body
        body = {
            'tenant_id': tenant_id,
            'integration': integration,
            'action': f'{integration}.{action}',  # e.g., "shopify.products.create"
            'params': params,
            'request_hash': request_hash,
            'trace': {
                'kernel_id': trace.get('kernel_id') if trace else None or self.kernel_id or 'unknown',
                'policy_decision_id': trace.get('policy_decision_id') if trace else None,
                'actor_id': trace.get('actor_id') if trace else None,
            },
        }
        
        # Make request
        try:
            response = requests.post(full_url, headers=headers, json=body, timeout=30)
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error_message_redacted') or error_data.get('error') or error_msg
                except:
                    pass
            raise Exception(f"CIA executor failed: {error_msg}")
        
        # Transform Repo C response to ExecutorResponse format
        return ExecutorResponse(
            data=result.get('data'),
            resource_ids=result.get('result_meta', {}).get('ids_created') or 
                        ([result.get('result_meta', {}).get('resource_id')] 
                         if result.get('result_meta', {}).get('resource_id') else None),
            resource_type=result.get('result_meta', {}).get('resource_type'),
            count=result.get('result_meta', {}).get('count'),
        )
