"""Lead scoring domain pack — real(ish) actions for api-docs-template.

Tenant model: **User**
All domain objects are scoped by `owner=<request.user>`.

Auth model: **DRF Token**, passed via `X-API-Key`.
"""

import csv
import io

from django.core.exceptions import ValidationError

from control_plane.acp.types import ActionDef, Pack
from scoringengine.models import Question, Recommendation, ScoringModel, Lead


def _require_user(ctx):
    user = ctx.get("user")
    if not user:
        raise ValueError("Missing authenticated user in context")
    return user


def handle_models_list(params, ctx):
    """List scoring models for the tenant (owner)."""
    user = _require_user(ctx)

    qs = (
        ScoringModel.objects.filter(owner=user)
        .select_related("question")
        .order_by("question__number")
    )

    items = []
    for sm in qs:
        items.append(
            {
                "question_id": sm.question_id,
                "question_number": sm.question.number,
                "question_field_name": sm.question.field_name,
                "weight": float(sm.weight),
                "x_axis": bool(sm.x_axis),
                "y_axis": bool(sm.y_axis),
                "formula": sm.formula,
            }
        )

    return {"data": items}


def handle_models_create(params, ctx):
    """Create a scoring model for an existing question (owner-scoped)."""
    user = _require_user(ctx)

    question_id = params.get("question_id")
    if not question_id:
        raise ValueError("Missing required param: question_id")

    q = Question.objects.filter(owner=user, id=question_id).first()
    if not q:
        raise ValueError("Question not found")

    if hasattr(q, "scoring_model"):
        raise ValueError("ScoringModel already exists for this question")

    payload = {
        "question": q,
        "owner": user,
        "weight": params.get("weight", 1),
        "x_axis": bool(params.get("x_axis", False)),
        "y_axis": bool(params.get("y_axis", False)),
        "formula": params.get("formula", ""),
    }

    if ctx.get("dry_run"):
        return {
            "data": {"preview": True, **payload, "question_id": q.id},
            "impact": {
                "creates": [{"type": "scoring_model", "count": 1}],
                "updates": [],
                "deletes": [],
                "side_effects": [],
                "risk": "low",
                "warnings": ["dry_run=true: no database write performed"],
            },
        }

    sm = ScoringModel(**payload)
    try:
        sm.full_clean()
    except ValidationError as e:
        raise ValueError(str(e))

    sm.save()

    return {
        "data": {
            "question_id": sm.question_id,
            "weight": float(sm.weight),
            "x_axis": bool(sm.x_axis),
            "y_axis": bool(sm.y_axis),
            "formula": sm.formula,
        }
    }


def handle_rules_list(params, ctx):
    """List recommendation rules (Recommendation) for the tenant."""
    user = _require_user(ctx)

    qs = (
        Recommendation.objects.filter(owner=user)
        .select_related("question")
        .order_by("question__number")
    )

    items = []
    for r in qs:
        items.append(
            {
                "question_id": r.question_id,
                "question_number": r.question.number,
                "question_field_name": r.question.field_name,
                "rule": r.rule,
                "response_text": r.response_text,
                "affiliate_name": r.affiliate_name,
            }
        )

    return {"data": items}


def handle_scores_recompute(params, ctx):
    """Recompute lead totals (placeholder for a real background job).

    Currently: recalculates `total_score = x_axis + y_axis` for selected leads.
    """
    user = _require_user(ctx)
    lead_ids = params.get("lead_ids")

    qs = Lead.objects.filter(owner=user)
    if lead_ids:
        qs = qs.filter(lead_id__in=lead_ids)

    updated = 0
    for lead in qs.iterator():
        lead.total_score = lead.x_axis + lead.y_axis
        lead.save(update_fields=["total_score"])
        updated += 1

    return {"data": {"updated": updated}}


def handle_leads_export(params, ctx):
    """Export leads with scores.

    Returns a small CSV payload inline (good enough for agent POC).
    """
    user = _require_user(ctx)
    limit = int(params.get("limit", 200))

    qs = Lead.objects.filter(owner=user).order_by("-timestamp")[:limit]

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["lead_id", "timestamp", "x_axis", "y_axis", "total_score"])
    count = 0
    for lead in qs:
        w.writerow([lead.lead_id, lead.timestamp, lead.x_axis, lead.y_axis, lead.total_score])
        count += 1

    return {"data": {"record_count": count, "csv": buf.getvalue()}}


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
            description="Create a scoring model for an existing Question (one-to-one)",
            params_schema={
                "type": "object",
                "properties": {
                    "question_id": {"type": "integer"},
                    "weight": {"type": "number", "default": 1},
                    "x_axis": {"type": "boolean", "default": False},
                    "y_axis": {"type": "boolean", "default": False},
                    "formula": {"type": "string", "default": ""},
                },
                "required": ["question_id"],
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
            description="Recompute lead totals for the tenant (placeholder implementation)",
            params_schema={
                "type": "object",
                "properties": {
                    "lead_ids": {"type": "array", "items": {"type": "string"}},
                },
            },
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.leads.export",
            scope="manage.read",
            description="Export leads with scores (returns inline CSV payload)",
            params_schema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 200},
                },
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
