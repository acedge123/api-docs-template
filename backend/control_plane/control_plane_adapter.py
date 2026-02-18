"""
ControlPlaneAdapter - Interface for calling Governance Hub (Repo B)

This adapter allows kernels to consult the platform for authoritative
authorization decisions.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


class AuthorizationRequest:
    """Request for authorization decision"""
    def __init__(self, kernel_id: str, tenant_id: str, actor: Dict[str, Any],
                 action: str, request_hash: str, params_summary: Optional[Dict] = None):
        self.kernel_id = kernel_id
        self.tenant_id = tenant_id
        self.actor = actor
        self.action = action
        self.request_hash = request_hash
        self.params_summary = params_summary
    
    def to_dict(self) -> Dict:
        """Convert to dict with camelCase field names for Repo B API"""
        return {
            'kernelId': self.kernel_id,  # Repo B expects camelCase
            'tenantId': self.tenant_id,  # Repo B expects camelCase
            'actor': self.actor,
            'action': self.action,
            'request_hash': self.request_hash,
            'params_summary': self.params_summary,
        }


class AuthorizationResponse:
    """Response from authorization decision"""
    def __init__(self, decision_id: str, decision: str, policy_version: str,
                 approval_id: Optional[str] = None, reason: Optional[str] = None,
                 policy_id: Optional[str] = None, expires_at: Optional[int] = None,
                 decision_ttl_ms: Optional[int] = None):
        self.decision_id = decision_id
        self.decision = decision  # 'allow' | 'deny' | 'require_approval'
        self.policy_version = policy_version
        self.approval_id = approval_id
        self.reason = reason
        self.policy_id = policy_id
        self.expires_at = expires_at
        self.decision_ttl_ms = decision_ttl_ms


@dataclass
class UsageResponse:
    """Response from usage query"""
    tenant_id: str
    tier: str  # 'free' | 'paid'
    calls_used: int
    calls_limit: int  # 100 for free tier, unlimited (or high number) for paid
    period_start: str  # ISO timestamp
    period_end: str  # ISO timestamp
    calls_remaining: Optional[int] = None  # Calculated: calls_limit - calls_used
    
    def __post_init__(self):
        if self.calls_remaining is None:
            self.calls_remaining = max(0, self.calls_limit - self.calls_used)


class UpgradeRequiredError(Exception):
    """Raised when free tier limit is reached and upgrade is required"""
    def __init__(self, message: str, usage: UsageResponse, upgrade_url: str):
        self.message = message
        self.usage = usage
        self.upgrade_url = upgrade_url
        super().__init__(self.message)


class ControlPlaneAdapter:
    """Interface for requesting authorization from Governance Hub"""
    
    def authorize(self, request: AuthorizationRequest) -> AuthorizationResponse:
        """
        Request authorization decision from Governance Hub
        
        CRITICAL: This is on the hot path - must be fast (<50ms ideally)
        """
        raise NotImplementedError
    
    def get_usage(self, tenant_id: str, period_start: Optional[str] = None, 
                  period_end: Optional[str] = None) -> UsageResponse:
        """
        Get usage statistics for a tenant
        
        Args:
            tenant_id: Tenant UUID
            period_start: Start of period (ISO timestamp, defaults to start of current month)
            period_end: End of period (ISO timestamp, defaults to now)
        
        Returns:
            UsageResponse with tier, calls_used, calls_limit, etc.
        """
        raise NotImplementedError


class HttpControlPlaneAdapter(ControlPlaneAdapter):
    """HTTP implementation - Calls Governance Hub /authorize endpoint"""
    
    def __init__(self, platform_url: str, kernel_api_key: str):
        """
        Initialize control plane adapter
        
        Args:
            platform_url: Repo B base URL (e.g., https://xxx.supabase.co)
            kernel_api_key: Kernel API key for authentication
        """
        self.platform_url = platform_url.rstrip('/')
        self.kernel_api_key = kernel_api_key
    
    def authorize(self, request: AuthorizationRequest) -> AuthorizationResponse:
        """
        Request authorization decision from Repo B
        
        Args:
            request: AuthorizationRequest with kernel_id, tenant_id, actor, action, etc.
        
        Returns:
            AuthorizationResponse with decision
        """
        url = f"{self.platform_url}/functions/v1/authorize"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.kernel_api_key}',
        }
        
        try:
            print(f"[AUTH] POST {url} with kernel_id={request.kernel_id}, action={request.action}")
            response = requests.post(url, headers=headers, json=request.to_dict(), timeout=5)
            print(f"[AUTH] Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            # Handle both {data: {...}} and direct response formats
            data = result.get('data', result)
            decision = data.get('decision', 'unknown')
            print(f"[AUTH] Authorization successful: {decision}")
            
            # Log response structure for debugging if needed
            if 'policy_version' not in data and 'policyVersion' not in data:
                print(f"[AUTH] Warning: policy_version missing in response. Response keys: {list(data.keys())}")
            
            # Extract fields with defaults for optional ones
            # decision_id and decision are required, others are optional
            decision_id = data.get('decision_id') or data.get('decisionId', 'unknown')
            decision = data.get('decision', 'allow')  # Default to allow if missing
            policy_version = data.get('policy_version') or data.get('policyVersion', '1.0.0')  # Default version
            
            return AuthorizationResponse(
                decision_id=decision_id,
                decision=decision,
                policy_version=policy_version,
                approval_id=data.get('approval_id') or data.get('approvalId'),
                reason=data.get('reason'),
                policy_id=data.get('policy_id') or data.get('policyId'),
                expires_at=data.get('expires_at') or data.get('expiresAt'),
                decision_ttl_ms=data.get('decision_ttl_ms') or data.get('decisionTtlMs'),
            )
        except requests.exceptions.RequestException as e:
            # If platform is unreachable, fail-closed (deny)
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
                print(f"[AUTH] Authorization request failed with status {status_code}")
                if status_code >= 500:
                    raise Exception(f"Platform unreachable: {status_code}")
            
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error') or error_msg
                    print(f"[AUTH] Error response: {error_msg}")
                except:
                    pass
            raise Exception(f"Authorization failed: {error_msg}")
    
    def heartbeat(self, kernel_id: str, version: str, packs: list, env: str = 'production') -> Dict:
        """
        Send heartbeat to Repo B for kernel registration
        
        Args:
            kernel_id: Kernel identifier
            version: Kernel version
            packs: List of pack names
            env: Environment (production, staging, etc.)
        
        Returns:
            Response dict with ok, kernelRegistered, policyVersion
        """
        url = f"{self.platform_url}/functions/v1/heartbeat"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.kernel_api_key}',
        }
        
        body = {
            'kernel_id': kernel_id,
            'version': version,
            'packs': packs,
            'env': env,
        }
        
        try:
            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Log but don't fail - heartbeat is best-effort
            print(f"Heartbeat failed: {e}")
            return {'ok': False, 'error': str(e)}
    
    def proposePolicy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propose a policy to Governance Hub for review and approval
        
        Args:
            request: Proposal request dict with:
                - org_id: str
                - title: str
                - summary: str
                - proposal_kind: str ('policy' | 'limit' | 'runbook' | 'revocation_suggestion')
                - proposal_spec_version: int
                - proposal: dict with 'type' and 'data'
                - rationale: str
                - evidence: dict (optional)
                - author_type: str ('agent' | 'user' | 'system')
                - author_id: str
        
        Returns:
            Response dict with proposal_id, status, and message
        """
        url = f"{self.platform_url}/functions/v1/policy-propose"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.kernel_api_key}',
        }
        
        try:
            print(f"[GOVERNANCE] POST {url} with org_id={request.get('org_id')}, proposal_kind={request.get('proposal_kind')}")
            response = requests.post(url, headers=headers, json=request, timeout=10)
            print(f"[GOVERNANCE] Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            # Handle both {data: {...}} and direct response formats
            data = result.get('data', result)
            print(f"[GOVERNANCE] Proposal submitted successfully: {data.get('proposal_id')}")
            
            return data
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error') or error_msg
                    print(f"[GOVERNANCE] Error response: {error_msg}")
                except:
                    pass
            raise Exception(f"Policy proposal failed: {error_msg}")
    
    def get_usage(self, tenant_id: str, period_start: Optional[str] = None,
                  period_end: Optional[str] = None) -> UsageResponse:
        """
        Get usage statistics for a tenant from Repo B
        
        Args:
            tenant_id: Tenant UUID
            period_start: Start of period (ISO timestamp, defaults to start of current month)
            period_end: End of period (ISO timestamp, defaults to now)
        
        Returns:
            UsageResponse with tier, calls_used, calls_limit, etc.
        """
        url = f"{self.platform_url}/functions/v1/usage"
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.kernel_api_key}',
        }
        
        # Default to current month if not provided
        from datetime import datetime, timezone
        if not period_end:
            period_end = datetime.now(timezone.utc).isoformat()
        if not period_start:
            # Start of current month
            now = datetime.now(timezone.utc)
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        body = {
            'tenant_id': tenant_id,
            'period_start': period_start,
            'period_end': period_end,
        }
        
        try:
            print(f"[USAGE] GET {url} for tenant_id={tenant_id}")
            response = requests.post(url, headers=headers, json=body, timeout=5)
            print(f"[USAGE] Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            
            # Handle both {data: {...}} and direct response formats
            data = result.get('data', result)
            
            # Extract usage data with defaults
            tier = data.get('tier', 'free')
            calls_used = data.get('calls_used', 0)
            calls_limit = data.get('calls_limit', 100 if tier == 'free' else 999999)
            
            return UsageResponse(
                tenant_id=tenant_id,
                tier=tier,
                calls_used=calls_used,
                calls_limit=calls_limit,
                period_start=period_start,
                period_end=period_end,
            )
        except requests.exceptions.RequestException as e:
            # If platform is unreachable, default to free tier with 0 calls
            # This allows the system to continue operating
            print(f"[USAGE] Usage query failed: {e}, defaulting to free tier")
            return UsageResponse(
                tenant_id=tenant_id,
                tier='free',
                calls_used=0,
                calls_limit=100,
                period_start=period_start or '',
                period_end=period_end or '',
            )