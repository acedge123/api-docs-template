"""
ACP Router — implements spec/ contract
"""

import json
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from .types import ActionDef, Pack


def _generate_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:16]}"


def _validate_request(req: Any) -> Tuple[bool, Optional[str]]:
    """Validate request per spec. Returns (ok, error_msg)."""
    if not isinstance(req, dict):
        return False, "Request must be an object"
    if "action" not in req or not isinstance(req["action"], str) or not req["action"].strip():
        return False, "action must be a non-empty string"
    if "params" in req and (not isinstance(req["params"], dict) or req["params"] is None):
        return False, "params must be an object"
    if "dry_run" in req and not isinstance(req["dry_run"], bool):
        return False, "dry_run must be a boolean"
    if "idempotency_key" in req and not isinstance(req["idempotency_key"], str):
        return False, "idempotency_key must be a string"
    return True, None


def _merge_packs(packs: List[Pack]) -> tuple[List[ActionDef], Dict[str, Callable]]:
    """Merge packs into single action registry."""
    all_actions: List[ActionDef] = []
    all_handlers: Dict[str, Callable] = {}
    seen = set()
    for pack in packs:
        for action in pack.actions:
            if action.name in seen:
                raise ValueError(f"Duplicate action: {action.name}")
            seen.add(action.name)
            all_actions.append(action)
        for name, handler in pack.handlers.items():
            if name in all_handlers:
                raise ValueError(f"Duplicate handler: {name}")
            all_handlers[name] = handler
    return all_actions, all_handlers


def create_manage_router(
    audit_adapter: Any,
    idempotency_adapter: Any,
    rate_limit_adapter: Any,
    ceilings_adapter: Any,
    bindings: Dict[str, Any],
    packs: List[Pack],
    executor: Any = None,  # Optional executor adapter (Repo C)
    control_plane: Any = None,  # Optional control plane adapter (Repo B)
) -> Callable[[Dict, Dict], Dict]:
    """
    Returns router: (request, meta) -> response
    meta: { "request": Django request, "ip_address": str, "user_agent": str }
    """
    meta_pack = _get_meta_pack()
    all_packs = [meta_pack] + list(packs)
    all_actions, all_handlers = _merge_packs(all_packs)

    # Set global registry for meta.actions
    _set_global_actions([a.to_dict() for a in all_actions])

    action_registry: Dict[str, Tuple[ActionDef, Callable]] = {}
    scope_map: Dict[str, str] = {}
    for action in all_actions:
        action_registry[action.name] = (action, all_handlers[action.name])
        scope_map[action.name] = action.scope

    def _log_audit(entry: Dict) -> None:
        if audit_adapter:
            audit_adapter.log(entry)

    def _get_api_key(req) -> Tuple[bool, Optional[str], Optional[str], Optional[List[str]], Optional[get_user_model()]]:
        """Extract and validate API key.

        For api-docs-template v1, we treat the **DRF Token** as the API key.

        Header: `X-API-Key: <token>`
        Returns: (ok, tenant_id, api_key_id, scopes, user)
        """
        api_key = req.headers.get("X-API-Key") or req.headers.get("x-api-key")
        if not api_key or not api_key.strip():
            return False, None, None, None, None

        try:
            token = Token.objects.select_related("user").get(key=api_key.strip())
        except Token.DoesNotExist:
            return False, None, None, None, None

        user = token.user
        tenant_id = str(user.id)

        # No scoped keys yet; treat all valid tokens as full control-plane access.
        scopes = ["manage.read", "manage.domain"]
        api_key_id = token.key
        return True, tenant_id, api_key_id, scopes, user

    def router(request_body: Dict, meta: Dict) -> Dict:
        request_id = _generate_request_id()
        req_obj = meta.get("request")
        ip_address = meta.get("ip_address", "")
        user_agent = meta.get("user_agent", "")

        ok, err = _validate_request(request_body)
        if not ok:
            return {
                "ok": False,
                "request_id": request_id,
                "error": err,
                "code": "VALIDATION_ERROR",
            }

        action = request_body.get("action", "")
        params = request_body.get("params") or {}
        dry_run = request_body.get("dry_run", False)
        idempotency_key = request_body.get("idempotency_key")

        if not req_obj:
            return {
                "ok": False,
                "request_id": request_id,
                "error": "Request object required for authentication",
                "code": "INVALID_API_KEY",
            }

        auth_ok, tenant_id, api_key_id, scopes, user = _get_api_key(req_obj)
        if not auth_ok:
            _log_audit({
                "tenant_id": "",
                "actor_type": "api_key",
                "actor_id": "unknown",
                "action": action,
                "request_id": request_id,
                "result": "error",
                "error_message": "Missing or invalid X-API-Key",
                "ip_address": ip_address,
                "dry_run": dry_run,
            })
            return {
                "ok": False,
                "request_id": request_id,
                "error": "Missing or invalid X-API-Key",
                "code": "INVALID_API_KEY",
            }

        if action not in action_registry:
            _log_audit({
                "tenant_id": tenant_id,
                "actor_type": "api_key",
                "actor_id": api_key_id or "unknown",
                "action": action,
                "request_id": request_id,
                "result": "error",
                "error_message": f"Unknown action: {action}",
                "ip_address": ip_address,
                "dry_run": dry_run,
            })
            return {
                "ok": False,
                "request_id": request_id,
                "error": f"Unknown action: {action}",
                "code": "NOT_FOUND",
            }

        action_def, handler = action_registry[action]
        required_scope = scope_map.get(action, action_def.scope)

        if required_scope and (not scopes or required_scope not in scopes):
            _log_audit({
                "tenant_id": tenant_id,
                "actor_type": "api_key",
                "actor_id": api_key_id or "unknown",
                "action": action,
                "request_id": request_id,
                "result": "denied",
                "error_message": f"Insufficient scope: requires '{required_scope}'",
                "ip_address": ip_address,
                "dry_run": dry_run,
            })
            return {
                "ok": False,
                "request_id": request_id,
                "error": f"Insufficient scope: action '{action}' requires '{required_scope}'",
                "code": "SCOPE_DENIED",
            }

        if dry_run and not action_def.supports_dry_run:
            return {
                "ok": False,
                "request_id": request_id,
                "error": f"Action {action} does not support dry_run mode",
                "code": "VALIDATION_ERROR",
            }

        # Authorization check via Repo B (for write actions)
        policy_decision_id = None
        if control_plane and not dry_run and required_scope in ("manage.domain", "manage.write"):
            # Check if this is a write action (create, update, delete)
            is_write_action = any(keyword in action.lower() for keyword in ['create', 'update', 'delete', 'cancel'])
            
            if is_write_action:
                try:
                    from control_plane.control_plane_adapter import AuthorizationRequest
                    import hashlib
                    import json
                    
                    # Create request hash (simplified - should use canonical JSON)
                    params_str = json.dumps(params, sort_keys=True)
                    request_hash = hashlib.sha256(params_str.encode()).hexdigest()
                    
                    # Create params_summary (small subset, sanitized)
                    params_summary = {}
                    if isinstance(params, dict):
                        # Only include non-sensitive fields, limit size
                        for key, value in list(params.items())[:5]:  # Limit to 5 fields
                            if key.lower() not in ['password', 'secret', 'token', 'key']:
                                if isinstance(value, (str, int, float, bool)):
                                    params_summary[key] = str(value)[:100]  # Truncate long values
                    
                    auth_request = AuthorizationRequest(
                        kernel_id=bindings.get('kernelId', 'leadscore-kernel'),
                        tenant_id=tenant_id,
                        actor={
                            'type': 'api_key',
                            'id': api_key_id or 'unknown',
                            'api_key_id': api_key_id,
                        },
                        action=action,
                        request_hash=request_hash,
                        params_summary=params_summary if params_summary else None,
                    )
                    
                    auth_response = control_plane.authorize(auth_request)
                    policy_decision_id = auth_response.decision_id
                    
                    if auth_response.decision == 'deny':
                        _log_audit({
                            "tenant_id": tenant_id,
                            "actor_type": "api_key",
                            "actor_id": api_key_id or "unknown",
                            "action": action,
                            "request_id": request_id,
                            "result": "denied",
                            "error_message": auth_response.reason or "Policy denied",
                            "ip_address": ip_address,
                            "dry_run": dry_run,
                        })
                        return {
                            "ok": False,
                            "request_id": request_id,
                            "error": auth_response.reason or "Action denied by policy",
                            "code": "SCOPE_DENIED",
                        }
                    elif auth_response.decision == 'require_approval':
                        _log_audit({
                            "tenant_id": tenant_id,
                            "actor_type": "api_key",
                            "actor_id": api_key_id or "unknown",
                            "action": action,
                            "request_id": request_id,
                            "result": "denied",
                            "error_message": "Action requires approval",
                            "ip_address": ip_address,
                            "dry_run": dry_run,
                        })
                        return {
                            "ok": False,
                            "request_id": request_id,
                            "error": "Action requires approval",
                            "code": "REQUIRES_APPROVAL",
                            "approval_id": auth_response.approval_id,
                        }
                    # If 'allow', continue execution
                except Exception as e:
                    # If Repo B is unreachable, fail-closed for write actions
                    _log_audit({
                        "tenant_id": tenant_id,
                        "actor_type": "api_key",
                        "actor_id": api_key_id or "unknown",
                        "action": action,
                        "request_id": request_id,
                        "result": "denied",
                        "error_message": f"Authorization check failed: {str(e)}",
                        "ip_address": ip_address,
                        "dry_run": dry_run,
                    })
                    return {
                        "ok": False,
                        "request_id": request_id,
                        "error": f"Authorization check failed: {str(e)}",
                        "code": "AUTHORIZATION_ERROR",
                    }

        # Idempotency replay (stub: idempotency_adapter would implement)
        if idempotency_key and not dry_run and idempotency_adapter:
            replay = idempotency_adapter.get_replay(tenant_id, action, idempotency_key)
            if replay is not None:
                _log_audit({
                    "tenant_id": tenant_id,
                    "actor_type": "api_key",
                    "actor_id": api_key_id or "unknown",
                    "action": action,
                    "request_id": request_id,
                    "result": "success",
                    "idempotency_key": idempotency_key,
                    "ip_address": ip_address,
                    "dry_run": False,
                })
                return {
                    "ok": True,
                    "request_id": request_id,
                    "data": replay,
                    "code": "IDEMPOTENT_REPLAY",
                }

        try:
            ctx = {
                "tenant_id": tenant_id,
                "api_key_id": api_key_id,
                "scopes": scopes or [],
                "dry_run": dry_run,
                "request_id": request_id,
                "user": user,
                "executor": executor,  # Pass executor to handlers
                "control_plane": control_plane,  # Pass control plane to handlers
                "bindings": bindings,  # Pass bindings (includes kernelId, integration)
            }
            result = handler(params, ctx)
        except Exception as e:
            _log_audit({
                "tenant_id": tenant_id,
                "actor_type": "api_key",
                "actor_id": api_key_id or "unknown",
                "action": action,
                "request_id": request_id,
                "result": "error",
                "error_message": str(e),
                "ip_address": ip_address,
                "dry_run": dry_run,
            })
            return {
                "ok": False,
                "request_id": request_id,
                "error": str(e),
                "code": "INTERNAL_ERROR",
            }

        if dry_run and isinstance(result, dict) and "impact" in result:
            data = result.get("impact", result)
        else:
            data = result.get("data", result) if isinstance(result, dict) else result

        if idempotency_key and not dry_run and idempotency_adapter:
            idempotency_adapter.store_replay(tenant_id, action, idempotency_key, data)

        _log_audit({
            "tenant_id": tenant_id,
            "actor_type": "api_key",
            "actor_id": api_key_id or "unknown",
            "action": action,
            "request_id": request_id,
            "result": "success",
            "ip_address": ip_address,
            "dry_run": dry_run,
            "policy_decision_id": policy_decision_id,  # Include if authorization was checked
        })

        return {
            "ok": True,
            "request_id": request_id,
            "data": data,
            "dry_run": dry_run,
            "constraints_applied": [f"tenant_scoped: {tenant_id}"],
        }

    return router


def _get_meta_pack() -> Pack:
    """Built-in meta pack."""

    def handle_meta_actions(params, ctx):
        # Return actions from global registry (set at router creation)
        actions = _get_global_actions()
        return {
            "actions": actions,
            "api_version": "v1",
            "total_actions": len(actions),
        }

    def handle_meta_version(params, ctx):
        actions = _get_global_actions()
        return {
            "api_version": "v1",
            "schema_version": "2026-02-11",
            "actions_count": len(actions),
        }

    return Pack(
        name="meta",
        actions=[
            ActionDef(
                name="meta.actions",
                scope="manage.read",
                description="List all available actions with schemas and required scopes",
                params_schema={"type": "object", "properties": {}},
                supports_dry_run=False,
            ),
            ActionDef(
                name="meta.version",
                scope="manage.read",
                description="Get API version and schema information",
                params_schema={"type": "object", "properties": {}},
                supports_dry_run=False,
            ),
        ],
        handlers={"meta.actions": handle_meta_actions, "meta.version": handle_meta_version},
    )


_GLOBAL_ACTIONS: List[Dict] = []


def _set_global_actions(actions: List[Dict]) -> None:
    global _GLOBAL_ACTIONS
    _GLOBAL_ACTIONS = actions


def _get_global_actions() -> List[Dict]:
    return _GLOBAL_ACTIONS
