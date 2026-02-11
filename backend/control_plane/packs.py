"""
Lead scoring domain pack — stub actions for api-docs-template
"""

from control_plane.acp.types import ActionDef, Pack


def handle_models_list(params, ctx):
    """List scoring models (stub)."""
    return {"data": []}


def handle_models_create(params, ctx):
    """Create scoring model (stub)."""
    if ctx.get("dry_run"):
        return {
            "data": {"model_id": "preview", **params},
            "impact": {
                "creates": [{"type": "scoring_model", "count": 1}],
                "updates": [],
                "deletes": [],
                "side_effects": [],
                "risk": "low",
                "warnings": [],
            },
        }
    return {"data": {"model_id": "stub", **params}}


def handle_rules_list(params, ctx):
    """List scoring rules (stub)."""
    return {"data": []}


def handle_scores_recompute(params, ctx):
    """Recompute scores (stub)."""
    return {"data": {"recomputed": 0}}


def handle_leads_export(params, ctx):
    """Export leads (stub)."""
    return {"data": {"export_url": "", "record_count": 0}}


leadscoring_pack = Pack(
    name="leadscoring",
    actions=[
        ActionDef(
            name="domain.leadscoring.models.list",
            scope="manage.read",
            description="List all scoring models for the tenant",
            params_schema={"type": "object", "properties": {}},
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.models.create",
            scope="manage.domain",
            description="Create a new scoring model",
            params_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "model_type": {"type": "string", "enum": ["linear", "ml", "rule_based"]},
                },
                "required": ["name", "model_type"],
            },
            supports_dry_run=True,
        ),
        ActionDef(
            name="domain.leadscoring.rules.list",
            scope="manage.read",
            description="List scoring rules",
            params_schema={"type": "object", "properties": {}},
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.scores.recompute",
            scope="manage.domain",
            description="Recompute scores for leads",
            params_schema={
                "type": "object",
                "properties": {"model_id": {"type": "string"}, "lead_ids": {"type": "array"}},
                "required": ["model_id"],
            },
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.leads.export",
            scope="manage.read",
            description="Export leads with scores",
            params_schema={
                "type": "object",
                "properties": {"model_id": {"type": "string"}, "filters": {"type": "object"}},
                "required": ["model_id"],
            },
            supports_dry_run=False,
        ),
    ],
    handlers={
        "domain.leadscoring.models.list": handle_models_list,
        "domain.leadscoring.models.create": handle_models_create,
        "domain.leadscoring.rules.list": handle_rules_list,
        "domain.leadscoring.scores.recompute": handle_scores_recompute,
        "domain.leadscoring.leads.export": handle_leads_export,
    },
)
