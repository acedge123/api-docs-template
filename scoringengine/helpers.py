from scoringengine.models import Lead, LeadLog, AnswerLog


def add_lead_log(lead: Lead):
    old_lead = LeadLog.objects.create(
        lead_id=lead.lead_id,
        timestamp=lead.timestamp,
        x_axis=lead.x_axis,
        y_axis=lead.y_axis,
        total_score=lead.total_score,
        owner=lead.owner,
    )
    for answer in lead.answers.all():
        AnswerLog.objects.create(
            lead=old_lead,
            field_name=answer.field_name,
            response=answer.response,
            value_number=answer.value_number,
            value=answer.value,
            date_value=answer.date_value,
            values=answer.values,
            points=answer.points,
        )
