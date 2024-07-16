import re
from datetime import datetime
from rest_framework.exceptions import ValidationError
from scoringengine.models import Lead, LeadLog, AnswerLog, Question


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


def collect_answers_values(owner, answers_data):
    """Collect answers values for questions"""

    for answer_data in answers_data:
        value_number = re.search(r"\[\d+\]$", answer_data["field_name"])

        if value_number:
            value_number = value_number.group(0)
            field_name = answer_data["field_name"].replace(value_number, "")
            answer_data["value_number"] = int(value_number[1:-1])

        else:
            field_name = answer_data["field_name"]

        question = owner.questions.filter(field_name=field_name).first()

        if question is None:
            raise ValidationError(
                {
                    "answers": {
                        "field_name": [
                            f"There are no question with '{answer_data['field_name']}' field name"
                        ]
                    }
                }
            )

        if not question.multiple_values and answer_data["field_name"] != field_name:
            raise ValidationError(
                {
                    "answers": {
                        "field_name": [
                            f"Question '{answer_data['field_name']}' is not multiple values type"
                        ]
                    }
                }
            )

        answer_data["field_name"] = field_name

        if question.type == Question.DATE:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", answer_data["response"]):
                raise ValidationError(
                    {
                        "answers": {
                            "response": [
                                f"Date '{answer_data['response']}' is not in format YYYY-MM-DD for question with "
                                f"question with '{answer_data['field_name']}' field name"
                            ]
                        }
                    }
                )

            answer_data["date_value"] = datetime.strptime(
                answer_data["response"], "%Y-%m-%d"
            ).date()

        elif question.type == Question.CHOICES:
            choice = question.choices.filter(slug=answer_data["response"]).first()

            if choice is None:
                raise ValidationError(
                    {
                        "answers": {
                            "response": [
                                f"There are no choice with '{answer_data['response']}' response in "
                                f"question with '{answer_data['field_name']}' field name"
                            ]
                        }
                    }
                )
            else:
                answer_data["response"] = choice.text
                answer_data["value"] = choice.value

        elif question.type == Question.INTEGER:
            try:
                value = int(answer_data["response"])
                answer_data["value"] = value

            except ValueError:
                raise ValidationError(
                    {
                        "answers": {
                            "response": [
                                f"Response '{answer_data['response']}' is invalid response for question with "
                                f"'{answer_data['field_name']}' field name"
                            ]
                        }
                    }
                )

        elif question.type == Question.MULTIPLE_CHOICES:
            texts = []
            values = []
            for slug in answer_data["response"].split(","):
                choice = question.choices.filter(slug=slug.strip()).first()

                if choice is None:
                    raise ValidationError(
                        {
                            "answers": {
                                "response": [
                                    f"There are no choice with '{slug.strip()}' response in "
                                    f"question with '{answer_data['field_name']}' field name"
                                ]
                            }
                        }
                    )
                else:
                    texts.append(choice.text)
                    values.append(choice.value)

            answer_data["response"] = ", ".join(texts)
            answer_data["values"] = values

        elif question.type == Question.SLIDER:
            try:
                value = float(answer_data["response"])
            except ValueError:
                raise ValidationError(
                    {
                        "answers": {
                            "response": [
                                f"Response '{answer_data['response']}' is invalid response for question with "
                                f"'{answer_data['field_name']}' field name"
                            ]
                        }
                    }
                )

            if not (question.min_value <= value <= question.max_value):
                raise ValidationError(
                    {
                        "answers": {
                            "response": [
                                f"Response for question with '{answer_data['field_name']}' field name "
                                f"should be within [{question.min_value}, {question.max_value}] range"
                            ]
                        }
                    }
                )

            answer_data["value"] = value

        elif question.type == Question.OPEN:
            answer_data["value"] = 1 if answer_data["response"] else 0


def calculate_x_and_y_scores(owner, answers_data):
    """Calculate answer points and X-axis and Y-axis scores for questions"""

    answers = {}
    for answer in answers_data:
        field_name = answer["field_name"]

        value_number = answer.get("value_number")
        if value_number is not None:
            if field_name not in answers:
                answers[field_name] = []

            if answer.get("date_value") is not None:
                answers[field_name].append(answer["date_value"])

            elif answer.get("value") is not None:
                answers[field_name].append(answer["value"])

            elif answer.get("values") is not None:
                answers[field_name].append(answer["values"])

        else:
            if answer.get("date_value") is not None:
                answers[field_name] = answer["date_value"]

            elif answer.get("value") is not None:
                answers[field_name] = answer["value"]

            elif answer.get("values") is not None:
                answers[field_name] = answer["values"]

    x_axis = 0
    y_axis = 0

    points = {}

    for answer_data in answers_data:
        field_name = answer_data["field_name"]
        question = owner.questions.filter(field_name=field_name).first()

        if field_name not in points:
            p = question.calculate_points(answers)
            points[field_name] = p

            if points[field_name] is not None:
                if question.scoring_model.x_axis:
                    x_axis += p

                if question.scoring_model.y_axis:
                    y_axis += p

        answer_data["points"] = points[field_name]

    return x_axis, y_axis


def collect_recommendations(owner, answers_data):
    """Collect recommendations by checking each question rule against provided answers"""

    answers = {}
    for answer in answers_data:
        field_name = answer["field_name"]

        value_number = answer.get("value_number")
        if value_number is not None:
            if field_name not in answers:
                answers[field_name] = []

            if answer.get("date_value") is not None:
                answers[field_name].append(answer["date_value"])

            elif answer.get("value") is not None:
                answers[field_name].append(answer["value"])

        else:
            if answer.get("date_value") is not None:
                answers[field_name] = answer["date_value"]

            elif answer.get("value") is not None:
                answers[field_name] = answer["value"]

    for answer_data in answers_data:
        question = owner.questions.filter(field_name=answer_data["field_name"]).first()

        if question.check_rule(answers):
            answer_data.update(question.get_recommendation_dict())
