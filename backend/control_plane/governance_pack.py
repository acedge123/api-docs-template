"""
Governance Pack - Enables agents to propose policies to Governance Hub (Repo B)

This pack provides a proposal-only model where:
- Agents can propose policies via governance.propose_policy
- Agents cannot publish policies (human approval required)
- All proposals are audited
- Platform admins review and approve/reject
"""

from typing import Any, Dict

from control_plane.acp.types import ActionDef, Pack


def handle_propose_policy(params: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle governance.propose_policy action.
    
    Forwards proposal to Repo B's /functions/v1/policy-propose endpoint.
    Repo A never stores or activates policies - it only forwards proposals.
    
    Args:
        params: Request parameters containing:
            - title: str (max 120 chars)
            - summary: str (max 300 chars)
            - proposal_kind: str ('policy' | 'limit' | 'runbook' | 'revocation_suggestion')
            - proposal: dict with 'type' ('LimitPolicy' | 'RequireApprovalPolicy') and 'data'
            - rationale: str (max 2000 chars)
            - evidence: dict (optional) with 'audit_event_ids' and 'links'
        ctx: Action context containing:
            - tenant_id: str (local tenant ID)
            - api_key_id: str
            - bindings: dict (includes kernelId, integration, org_id)
            - control_plane: ControlPlaneAdapter instance
            - executor: ExecutorAdapter instance (optional)
            - user: Django user object
            - dry_run: bool
    
    Returns:
        dict with proposal_id, status, and message
    """
    # Get control plane adapter from context (router passes it directly)
    control_plane = ctx.get("control_plane")
    if not control_plane:
        raise ValueError("ControlPlaneAdapter not configured. Set control_plane in router config.")
    
    # Check if proposePolicy method exists
    if not hasattr(control_plane, 'proposePolicy'):
        raise ValueError("ControlPlaneAdapter does not support proposePolicy. Use HttpControlPlaneAdapter.")
    
    # Get org_id from bindings or environment
    # Note: org_id is the organization UUID from Repo B, not the tenant UUID
    # It can be set in bindings or as an environment variable
    bindings = ctx.get("bindings", {})
    import os
    org_id = bindings.get("org_id") or bindings.get("organization_id") or os.environ.get("ACP_ORG_ID")
    if not org_id:
        raise ValueError(
            "org_id not found. Set ACP_ORG_ID environment variable or add 'org_id' to bindings. "
            "This should be the organization UUID from Repo B (not the tenant UUID)."
        )
    
    # Validate proposal structure
    proposal = params.get("proposal")
    if not proposal or not proposal.get("type") or not proposal.get("data"):
        raise ValueError("Invalid proposal structure. Must have type and data fields.")
    
    # Build proposal request
    proposal_request = {
        "org_id": org_id,
        "title": params.get("title"),
        "summary": params.get("summary"),
        "proposal_kind": params.get("proposal_kind"),
        "proposal_spec_version": 1,
        "proposal": {
            "type": proposal.get("type"),
            "data": proposal.get("data"),
        },
        "rationale": params.get("rationale"),
        "evidence": params.get("evidence") or {},
        "author_type": "agent",
        "author_id": ctx.get("api_key_id") or "unknown",
    }
    
    # Validate proposal_kind
    valid_kinds = ["policy", "limit", "runbook", "revocation_suggestion"]
    if proposal_request["proposal_kind"] not in valid_kinds:
        raise ValueError(f"Invalid proposal_kind: {proposal_request['proposal_kind']}. Must be one of: {', '.join(valid_kinds)}")
    
    # Validate proposal type
    valid_types = ["LimitPolicy", "RequireApprovalPolicy"]
    if proposal_request["proposal"]["type"] not in valid_types:
        raise ValueError(f"Invalid proposal type: {proposal_request['proposal']['type']}. Must be one of: {', '.join(valid_types)}")
    
    # Forward to Repo B
    try:
        proposal_response = control_plane.proposePolicy(proposal_request)
    except Exception as e:
        # Note: Audit logging is handled by the router, so we just raise the error
        raise ValueError(f"Failed to propose policy: {str(e)}")
    
    return {
        "data": {
            "proposal_id": proposal_response.get("proposal_id"),
            "status": proposal_response.get("status"),
            "message": proposal_response.get("message", "Proposal submitted successfully"),
        }
    }


governance_pack = Pack(
    name="governance",
    actions=[
        ActionDef(
            name="governance.propose_policy",
            scope="manage.governance",
            description="Propose a policy, limit, or runbook to Governance Hub for review and approval",
            params_schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "maxLength": 120,
                        "description": "Short title for the proposal (max 120 chars)",
                    },
                    "summary": {
                        "type": "string",
                        "maxLength": 300,
                        "description": "Brief summary of the proposal (max 300 chars)",
                    },
                    "proposal_kind": {
                        "type": "string",
                        "enum": ["policy", "limit", "runbook", "revocation_suggestion"],
                        "description": "Type of proposal",
                    },
                    "proposal": {
                        "type": "object",
                        "description": "The proposal payload (LimitPolicy or RequireApprovalPolicy)",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["LimitPolicy", "RequireApprovalPolicy"],
                            },
                            "data": {
                                "type": "object",
                                "description": "Proposal-specific data",
                            },
                        },
                        "required": ["type", "data"],
                    },
                    "rationale": {
                        "type": "string",
                        "maxLength": 2000,
                        "description": "Explanation for why this proposal is needed (max 2000 chars)",
                    },
                    "evidence": {
                        "type": "object",
                        "description": "Supporting evidence (optional)",
                        "properties": {
                            "audit_event_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Audit event IDs that support this proposal",
                            },
                            "links": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "URLs to relevant documentation or evidence",
                            },
                        },
                    },
                },
                "required": ["title", "summary", "proposal_kind", "proposal", "rationale"],
            },
            supports_dry_run=True,
        ),
    ],
    handlers={
        "governance.propose_policy": handle_propose_policy,
    },
)
