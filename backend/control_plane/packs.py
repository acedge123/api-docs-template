"""Lead scoring domain pack — real(ish) actions for api-docs-template.

Tenant model: **User**
All domain objects are scoped by `owner=<request.user>`.

Auth model: **DRF Token**, passed via `X-API-Key`.
"""

import csv
import io
from typing import Any, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify

from control_plane.acp.types import ActionDef, Pack
from scoringengine.helpers import calculate_x_and_y_scores, collect_answers_values
from scoringengine.models import Answer, Choice, Lead, Question, Recommendation, ScoringModel


def _require_user(ctx):
    user = ctx.get("user")
    if not user:
        raise ValueError("Missing authenticated user in context")
    return user


def handle_questions_list(params, ctx):
    """List questions (and choices) for the tenant."""
    user = _require_user(ctx)

    qs = Question.objects.filter(owner=user).prefetch_related("choices").order_by(
        "number"
    )

    items = []
    for q in qs:
        items.append(
            {
                "id": q.id,
                "number": q.number,
                "text": q.text,
                "field_name": q.field_name,
                "type": q.type,
                "multiple_values": bool(q.multiple_values),
                "min_value": q.min_value,
                "max_value": q.max_value,
                "choices": [
                    {"text": c.text, "slug": c.slug, "value": float(c.value)}
                    for c in q.choices.all().order_by("id")
                ],
            }
        )

    return {"data": items}


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


def handle_questions_upsert_bulk(params, ctx):
    """Create/update the canonical landing-page questions for the tenant.

    Params:
      - questions: [{number, text, field_name, type, multiple_values?, min_value?, max_value?, choices?}]
        where choices: [{text, slug?, value}]

    Notes:
      - Upsert key: (owner, field_name)
      - For CHOICES/MC questions: will upsert choices by (question, slug)
    """
    user = _require_user(ctx)
    questions: List[Dict[str, Any]] = params.get("questions") or []
    if not isinstance(questions, list) or not questions:
        raise ValueError("Missing required param: questions (non-empty array)")

    created_q = 0
    updated_q = 0
    created_c = 0
    updated_c = 0

    with transaction.atomic():
        for qd in questions:
            field_name = (qd.get("field_name") or "").strip()
            if not field_name:
                raise ValueError("Question field_name is required")

            defaults = {
                "number": int(qd.get("number") or 0),
                "text": (qd.get("text") or "").strip()[:200],
                "type": (qd.get("type") or "").strip(),
                "multiple_values": bool(qd.get("multiple_values", False)),
                "min_value": qd.get("min_value"),
                "max_value": qd.get("max_value"),
                "owner": user,
            }

            obj, created = Question.objects.update_or_create(
                owner=user, field_name=field_name, defaults=defaults
            )
            if created:
                created_q += 1
            else:
                updated_q += 1

            # Upsert choices (if provided)
            choices = qd.get("choices") or []
            if choices:
                if not isinstance(choices, list):
                    raise ValueError(f"choices for {field_name} must be an array")

                for cd in choices:
                    c_text = (cd.get("text") or "").strip()[:200]
                    if not c_text:
                        raise ValueError(f"choice text required for question {field_name}")

                    c_slug = (cd.get("slug") or slugify(c_text)).strip()
                    if not c_slug:
                        c_slug = slugify(c_text)

                    c_value = cd.get("value")
                    if c_value is None:
                        raise ValueError(f"choice value required for question {field_name}/{c_slug}")

                    c_obj, c_created = Choice.objects.update_or_create(
                        question=obj,
                        slug=c_slug,
                        defaults={"text": c_text, "value": c_value},
                    )
                    if c_created:
                        created_c += 1
                    else:
                        updated_c += 1

    return {
        "data": {
            "questions": {"created": created_q, "updated": updated_q},
            "choices": {"created": created_c, "updated": updated_c},
        }
    }


def handle_models_upsert_bulk(params, ctx):
    """Upsert scoring models by question_field_name.

    Params:
      - models: [{question_field_name, weight?, x_axis, y_axis, formula?}]
    """
    user = _require_user(ctx)
    models = params.get("models") or []
    if not isinstance(models, list) or not models:
        raise ValueError("Missing required param: models (non-empty array)")

    created = 0
    updated = 0

    with transaction.atomic():
        for md in models:
            qfn = (md.get("question_field_name") or "").strip()
            if not qfn:
                raise ValueError("question_field_name is required")

            q = Question.objects.filter(owner=user, field_name=qfn).first()
            if not q:
                raise ValueError(f"Question not found: {qfn}")

            defaults = {
                "owner": user,
                "weight": md.get("weight", 1),
                "x_axis": bool(md.get("x_axis", False)),
                "y_axis": bool(md.get("y_axis", False)),
                "formula": md.get("formula", ""),
            }

            sm, was_created = ScoringModel.objects.update_or_create(
                owner=user, question=q, defaults=defaults
            )
            if was_created:
                created += 1
            else:
                updated += 1

            try:
                sm.full_clean()
            except ValidationError as e:
                raise ValueError(str(e))

    return {"data": {"created": created, "updated": updated}}


def handle_rules_upsert_bulk(params, ctx):
    """Upsert recommendation rules by question_field_name.

    Params:
      - rules: [{question_field_name, rule, response_text?, affiliate_name?, affiliate_link?, redirect_url?}]
    """
    user = _require_user(ctx)
    rules = params.get("rules") or []
    if not isinstance(rules, list) or not rules:
        raise ValueError("Missing required param: rules (non-empty array)")

    created = 0
    updated = 0

    with transaction.atomic():
        for rd in rules:
            qfn = (rd.get("question_field_name") or "").strip()
            if not qfn:
                raise ValueError("question_field_name is required")

            q = Question.objects.filter(owner=user, field_name=qfn).first()
            if not q:
                raise ValueError(f"Question not found: {qfn}")

            defaults = {
                "owner": user,
                "rule": (rd.get("rule") or "").strip(),
                "response_text": rd.get("response_text", ""),
                "affiliate_name": rd.get("affiliate_name", ""),
                "affiliate_image": rd.get("affiliate_image", ""),
                "affiliate_link": rd.get("affiliate_link", ""),
                "redirect_url": rd.get("redirect_url", ""),
            }

            rec, was_created = Recommendation.objects.update_or_create(
                owner=user, question=q, defaults=defaults
            )
            if was_created:
                created += 1
            else:
                updated += 1

            try:
                rec.full_clean()
            except ValidationError as e:
                raise ValueError(str(e))

    return {"data": {"created": created, "updated": updated}}


def handle_leads_create(params, ctx):
    """Create a lead for the tenant and score it.

    Params:
      - answers: [{field_name, response}] (recommended)
      - allow_partial: bool (default true)

    Behavior:
      - Computes x_axis/y_axis via existing helpers
      - Stores Lead + Answer rows (including per-answer points)
    """
    user = _require_user(ctx)

    answers_data = params.get("answers") or []
    if not isinstance(answers_data, list) or not answers_data:
        raise ValueError("Missing required param: answers (non-empty array)")

    allow_partial = bool(params.get("allow_partial", True))

    provided_field_names = []
    for a in answers_data:
        fn = (a.get("field_name") or "").strip()
        if not fn:
            raise ValueError("Each answer requires field_name")
        provided_field_names.append(fn)

    if not allow_partial:
        for q in user.questions.all():
            if q.field_name not in provided_field_names:
                raise ValueError("Not all answers provided")

    # Mutates answers_data in-place: adds value/values/date_value/points
    collect_answers_values(user, answers_data)

    x_axis, y_axis = calculate_x_and_y_scores(user, answers_data)
    total_score = x_axis + y_axis

    if ctx.get("dry_run"):
        return {
            "data": {
                "preview": True,
                "x_axis": float(x_axis),
                "y_axis": float(y_axis),
                "total_score": float(total_score),
                "answers": answers_data,
            }
        }

    with transaction.atomic():
        lead = Lead.objects.create(
            owner=user,
            x_axis=x_axis,
            y_axis=y_axis,
            total_score=total_score,
        )

        answer_rows = []
        for a in answers_data:
            answer_rows.append(
                Answer(
                    lead=lead,
                    field_name=a.get("field_name"),
                    response=a.get("response", ""),
                    value_number=a.get("value_number"),
                    value=a.get("value"),
                    date_value=a.get("date_value"),
                    values=a.get("values"),
                    points=a.get("points"),
                    response_text=a.get("response_text", ""),
                    affiliate_name=a.get("affiliate_name", ""),
                    affiliate_image=a.get("affiliate_image", ""),
                    affiliate_link=a.get("affiliate_link", ""),
                    redirect_url=a.get("redirect_url", ""),
                )
            )

        Answer.objects.bulk_create(answer_rows)

    return {
        "data": {
            "lead_id": str(lead.lead_id),
            "x_axis": float(lead.x_axis),
            "y_axis": float(lead.y_axis),
            "total_score": float(lead.total_score),
        }
    }


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
        w.writerow(
            [lead.lead_id, lead.timestamp, lead.x_axis, lead.y_axis, lead.total_score]
        )
        count += 1

    return {"data": {"record_count": count, "csv": buf.getvalue()}}


leadscoring_pack = Pack(
    name="leadscoring",
    actions=[
        ActionDef(
            name="domain.leadscoring.questions.list",
            scope="manage.read",
            description="List leadscoring questions (and choices) for the tenant",
            params_schema={"type": "object", "properties": {}},
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.questions.upsert_bulk",
            scope="manage.domain",
            description="Upsert leadscoring questions + choices for the tenant",
            params_schema={
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {"type": "object"},
                    }
                },
                "required": ["questions"],
            },
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.leads.create",
            scope="manage.domain",
            description="Create a lead (with answers) and compute scores",
            params_schema={
                "type": "object",
                "properties": {
                    "answers": {"type": "array", "items": {"type": "object"}},
                    "allow_partial": {"type": "boolean", "default": True},
                },
                "required": ["answers"],
            },
            supports_dry_run=True,
        ),
        ActionDef(
            name="domain.leadscoring.models.upsert_bulk",
            scope="manage.domain",
            description="Upsert scoring models by question_field_name",
            params_schema={
                "type": "object",
                "properties": {
                    "models": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["models"],
            },
            supports_dry_run=False,
        ),
        ActionDef(
            name="domain.leadscoring.rules.upsert_bulk",
            scope="manage.domain",
            description="Upsert recommendation rules by question_field_name",
            params_schema={
                "type": "object",
                "properties": {
                    "rules": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["rules"],
            },
            supports_dry_run=False,
        ),
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
        "domain.leadscoring.questions.list": handle_questions_list,
        "domain.leadscoring.questions.upsert_bulk": handle_questions_upsert_bulk,
        "domain.leadscoring.leads.create": handle_leads_create,
        "domain.leadscoring.models.list": handle_models_list,
        "domain.leadscoring.models.create": handle_models_create,
        "domain.leadscoring.models.upsert_bulk": handle_models_upsert_bulk,
        "domain.leadscoring.rules.list": handle_rules_list,
        "domain.leadscoring.rules.upsert_bulk": handle_rules_upsert_bulk,
        "domain.leadscoring.scores.recompute": handle_scores_recompute,
        "domain.leadscoring.leads.export": handle_leads_export,
    },
)
