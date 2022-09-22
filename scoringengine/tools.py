from django.contrib.auth import get_user_model

from scoringengine.models import (
    Answer,
    Choice,
    Lead,
    Question,
    Recommendation,
    ScoringModel,
    ValueRange,
)

User = get_user_model()


def clone_quiz_structure(source_user: User, target_user: User):
    for question_old in Question.objects.filter(owner=source_user).all():
        question_new = Question.objects.create(
            owner=target_user,
            number=question_old.number,
            text=question_old.text,
            field_name=question_old.field_name,
            type=question_old.type,
            min_value=question_old.min_value,
            max_value=question_old.max_value,
        )

        for choice in question_old.choices.all():
            Choice.objects.create(
                question=question_new,
                text=choice.text,
                slug=choice.slug,
                value=choice.value,
            )


def clone_scoring_model(source_user: User, target_user: User):
    for sm_old in ScoringModel.objects.filter(owner=source_user).all():
        sm_new = ScoringModel.objects.create(
            owner=target_user,
            question=Question.objects.get(
                field_name=sm_old.question.field_name, owner=target_user
            ),
            weight=sm_old.weight,
            x_axis=sm_old.x_axis,
            y_axis=sm_old.y_axis,
            formula=sm_old.formula,
        )

        for vr_old in sm_old.ranges.all():
            ValueRange.objects.create(
                scoring_model=sm_new,
                start=vr_old.start,
                end=vr_old.end,
                points=vr_old.points,
            )

    for recommendation in Recommendation.objects.filter(owner=source_user):
        Recommendation.objects.create(
            owner=target_user,
            question=Question.objects.get(
                field_name=sm_old.question.field_name, owner=target_user
            ),
            rule=recommendation.rule,
            response_text=recommendation.response_text,
            affiliate_name=recommendation.affiliate_name,
            affiliate_image=recommendation.affiliate_image,
            affiliate_link=recommendation.affiliate_link,
            redirect_url=recommendation.redirect_url,
        )


def clone_leads_and_answers(source_user: User, target_user: User):
    for lead_old in Lead.objects.filter(owner=source_user).all():
        lead_new = Lead.objects.create(
            owner=target_user,
            timestamp=lead_old.timestamp,
            x_axis=lead_old.x_axis,
            y_axis=lead_old.y_axis,
            total_score=lead_old.total_score,
        )

        for answer_old in lead_old.answers.all():
            Answer.objects.create(
                lead=lead_new,
                field_name=answer_old.field_name,
                response=answer_old.response,
                value=answer_old.value,
                values=answer_old.values,
                points=answer_old.points,
                response_text=answer_old.response_text,
                affiliate_name=answer_old.affiliate_name,
                affiliate_image=answer_old.affiliate_image,
                affiliate_link=answer_old.affiliate_link,
                redirect_url=answer_old.redirect_url,
            )


def clone_account(
    source_user: User,
    target_user: User,
    quiz_structure: bool = True,
    scoring_model: bool = True,
    leads_and_answers: bool = True,
):
    if quiz_structure:
        clone_quiz_structure(source_user, target_user)

        if scoring_model:
            clone_scoring_model(source_user, target_user)

            if leads_and_answers:
                clone_leads_and_answers(source_user, target_user)
