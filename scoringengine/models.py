import math
import re
import uuid

from datetime import date
from itertools import chain
from math import sqrt
from random import randint

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

ARITHMETIC_OPERATORS = ["+", "-", "*", "%", "/", "**", "//"]
COMPARISON_OPERATORS = [">", "<", "==", "!=", ">=", "<="]
LOGICAL_OPERATORS = ["and", "or", "not"]

AGGREGATE_FUNCTIONS = ["count", "max", "mean", "median", "min", "sum"]
MATH_FUNCTIONS = ["sqrt"]
DATE_FUNCTIONS = ["days", "today"]

NUMBER_REGEX = r"[0-9.]+"
DATE_REGEX = r"\d{4}-\d{2}-\d{2}"
FIELD_NAME_REGEX = r"\w+(\[\-?\d+\])?"

AGGREGATE_FUNCTIONS_REGEX = (
    rf"({'|'.join(AGGREGATE_FUNCTIONS)})\({{{FIELD_NAME_REGEX}}}\)"
)
MATH_FUNCTIONS_REGEX = rf"({'|'.join(MATH_FUNCTIONS)})\((.*?)\)"
DATE_FUNCTIONS_REGEX = rf"({'|'.join(DATE_FUNCTIONS)})\((.*?)\)"
DAYS_FUNCTIONS_REGEX = rf"\(({{{FIELD_NAME_REGEX}}}|{DATE_FUNCTIONS_REGEX})\s*-\s*({{{FIELD_NAME_REGEX}}}|{DATE_FUNCTIONS_REGEX})\).days"

RULE_PREFIX = "If"
RULE_REGEX = rf'(^{RULE_PREFIX})(({NUMBER_REGEX}|{DATE_REGEX}|{{{FIELD_NAME_REGEX}}}|{AGGREGATE_FUNCTIONS_REGEX}|{MATH_FUNCTIONS_REGEX}|{DATE_FUNCTIONS_REGEX}|{DAYS_FUNCTIONS_REGEX})|({"|".join([re.escape(o) for o in ARITHMETIC_OPERATORS + COMPARISON_OPERATORS + LOGICAL_OPERATORS])})|\s*|[()]*)+'

FORMULA_REGEX = rf'(({NUMBER_REGEX}|{{{FIELD_NAME_REGEX}}}|{AGGREGATE_FUNCTIONS_REGEX}|{MATH_FUNCTIONS_REGEX}|{DATE_FUNCTIONS_REGEX}|{DAYS_FUNCTIONS_REGEX})|({"|".join([re.escape(o) for o in ARITHMETIC_OPERATORS])})|\s*|[()]*)+'


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Generate API token for each newly created user"""

    if created:
        Token.objects.create(user=instance)


def days(dt):
    return dt.days


def generate_mocked_data(formula: str, owner: get_user_model()) -> dict:
    mocked_data = {}

    for k in re.findall(rf"{{({FIELD_NAME_REGEX})}}", formula):
        field_name = re.sub(r"\[.+\]", "", k[0])
        question = Question.objects.filter(field_name=field_name, owner=owner).first()

        if question and question.type == Question.DATE:
            value = date.today()

        elif question and question.type == Question.INTEGER:
            value = randint(1, 100)

        elif question and question.type == Question.SLIDER:
            value = randint(question.min_value or 0, question.max_value or 100)

        else:
            value = f"{{{field_name}}}"

        mocked_data[field_name] = (
            [value, value, value, value]
            if question and question.multiple_values
            else value
        )

    return mocked_data


def validate_field_name(value):
    """Check that entered field name is valid rule variable"""

    if not re.fullmatch(FIELD_NAME_REGEX, value):
        raise ValidationError(
            '"%(field_name)s" is not valid Field name',
            params={"field_name": value},
            code="invalid_field_name",
        )


def validate_rule(value):
    """Check that entered rule is valid: contain only allowed parts and can be evaluated using "eval" function"""

    if not re.fullmatch(RULE_REGEX, value):
        raise ValidationError("Rule is invalid", code="invalid_rule")


def validate_formula(value):
    """Check that entered formula is valid: contain only allowed parts and can be evaluated using "eval" function"""

    if not re.fullmatch(FORMULA_REGEX, value):
        raise ValidationError("Formula is invalid", code="invalid_formula")


def prepare_answers(formula: str, answers: dict) -> (str, dict):
    prepared_answers = {}
    formatted_formula = formula

    for field_name in re.findall(r"{(.+?)}", formula):
        re_item = re.search(r"\[(\-?\d+)\]", field_name)

        if re_item:
            stripped_field_name = field_name.replace(re_item.group(0), "")
            item_number = int(re_item.group(1))

            formatted_field_name = f"{stripped_field_name}_{f'm{-item_number}' if item_number < 0 else item_number}"

            if stripped_field_name in answers:
                try:
                    answer = answers[stripped_field_name][item_number]

                except IndexError:
                    answer = 1

                prepared_answers[formatted_field_name] = (
                    f"date({answer.year}, {answer.month}, {answer.day})"
                    if isinstance(answer, date)
                    else answer
                )
                formatted_formula = formatted_formula.replace(
                    field_name, formatted_field_name
                )

        elif field_name in answers:
            prepared_answers[field_name] = answers[field_name]

    return formatted_formula, prepared_answers


def prepare_formula(formula: str, answers: dict) -> (str, dict):
    prepared_formula = formula

    for dd in re.findall(r"\d{4}-\d{2}-\d{2}", prepared_formula):
        prepared_formula = prepared_formula.replace(
            dd, f"date({','.join([d.lstrip('0') for d in dd.split('-')])})"
        )

    while True:
        re_avg = re.search(
            r"(mean|median|sum|min|max|count)\({(\w+)}\)", prepared_formula
        )

        if re_avg:
            func_name = re_avg.group(1)
            field_name = re_avg.group(2)

            if not isinstance(answers[field_name], list):
                raise ValidationError(
                    '"Math functions can be used only with multiple value questions. %(field_name)s" is not multiple value',
                    params={"field_name": value},
                    code="invalid_field_name",
                )
                continue

            if all([isinstance(v, date) for v in answers[field_name]]):
                if func_name == "mean":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(
                            (answers[field_name][-1] - answers[field_name][0]).days
                            / len(answers[field_name])
                        ),
                    )

                elif func_name == "median":
                    if len(answers[field_name]) > 1:
                        _date = answers[field_name][0]
                        min_days = 999999999999
                        max_days = 0
                        for n in range(1, len(answers[field_name])):
                            if (answers[field_name][n] - _date).days < min_days:
                                min_days = (answers[field_name][n] - _date).days

                            if (answers[field_name][n] - _date).days > max_days:
                                max_days = (answers[field_name][n] - _date).days

                            _date = answers[field_name][n]

                        days = (max_days - min_days) / 2.0

                    else:
                        days = 0

                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0), str(days)
                    )

                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(
                            (answers[field_name][-1] - answers[field_name][0]).days
                            / len(answers[field_name])
                        ),
                    )

                elif func_name == "sum":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str((answers[field_name][-1] - answers[field_name][0]).days),
                    )

                elif func_name == "min":
                    _date = answers[field_name][0]
                    if len(answers[field_name]) > 1:
                        days = 999999999999
                        for n in range(1, len(answers[field_name])):
                            if (answers[field_name][n] - _date).days < days:
                                days = (answers[field_name][n] - _date).days
                            _date = answers[field_name][n]

                    else:
                        days = 0

                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0), str(days)
                    )

                elif func_name == "max":
                    _date = answers[field_name][0]
                    days = 0
                    for n in range(1, len(answers[field_name])):
                        if (answers[field_name][n] - _date).days > days:
                            days = (answers[field_name][n] - _date).days
                        _date = answers[field_name][n]

                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0), str(days)
                    )

                elif func_name == "count":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0), str(len(answers[field_name]))
                    )

            else:
                if func_name == "mean":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(sum(answers[field_name]) / len(answers[field_name])),
                    )

                elif func_name == "median":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(
                            (max(answers[field_name]) - min(answers[field_name])) / 2.0
                        ),
                    )

                elif func_name == "sum":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(sum(answers[field_name])),
                    )

                elif func_name == "min":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(min(answers[field_name])),
                    )

                elif func_name == "max":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(max(answers[field_name])),
                    )

                elif func_name == "count":
                    prepared_formula = prepared_formula.replace(
                        re_avg.group(0),
                        str(len(answers[field_name])),
                    )
        else:
            break

    prepared_formula = prepared_formula.replace("today()", "date.today()")

    return prepared_formula, answers


class RecommendationFieldsMixin(models.Model):
    response_text = models.TextField(blank=True)

    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)

    redirect_url = models.URLField(max_length=2048, blank=True)

    fields = (
        "response_text",
        "affiliate_name",
        "affiliate_image",
        "affiliate_link",
        "redirect_url",
    )

    class Meta:
        abstract = True


class Recommendation(RecommendationFieldsMixin):
    question = models.OneToOneField(
        "Question", on_delete=models.CASCADE, related_name="recommendation"
    )

    rule = models.CharField(
        max_length=500,
        validators=[validate_rule],
        help_text=f'Rule should start with "If" and may contain only valid numbers, questions with choices '
        f'"Field names" in curly braces (e.g. {{field_name}}) '
        f"combined with "
        f'arithmetic ({", ".join(ARITHMETIC_OPERATORS)}), '
        f'comparison ({", ".join(COMPARISON_OPERATORS)}), '
        f'logical operations ({", ".join(LOGICAL_OPERATORS)}) '
        "and parentheses to select points based on expression result."
        f'</br>Aggregate functions which may be used in are: {", ".join(AGGREGATE_FUNCTIONS)}'
        f'</br>Mathematical functions which may be used in are: {", ".join(MATH_FUNCTIONS)}'
        f'</br>Date functions which may be used in are: {", ".join(DATE_FUNCTIONS)}',
    )

    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="recommendations"
    )

    def __str__(self):
        return f"Q{self.question.number}: {self.rule}"

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)

        try:
            Question.eval_rule(
                self.rule, data=generate_mocked_data(self.rule, self.owner)
            )
        except SyntaxError as ex:
            raise ValidationError(
                {
                    "rule": f'Rule syntax invalid "{RULE_PREFIX} {ex.text[:ex.offset - 1]}>>>here>>>{ex.text[ex.offset - 1:]}"'
                },
                code="invalid_rule",
            )
        except NameError:
            # No syntax errors in rule
            pass


class ScoringModel(models.Model):
    question = models.OneToOneField(
        "Question", on_delete=models.CASCADE, related_name="scoring_model"
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1,
        validators=[MinValueValidator(limit_value=0)],
    )
    x_axis = models.BooleanField()
    y_axis = models.BooleanField()

    formula = models.CharField(
        max_length=500,
        blank=True,
        validators=[validate_formula],
        help_text=f"Leave empty to select points based on direct value from associated question.</br>"
        f'Add expression with "Field names" in curly braces (e.g. {{field_name}}), '
        f'arithmetic ({", ".join(ARITHMETIC_OPERATORS)}) operations '
        "and parentheses to select points based on expression result."
        f'</br>Aggregate functions which may be used in are: {", ".join(AGGREGATE_FUNCTIONS)}'
        f'</br>Mathematical functions which may be used in are: {", ".join(MATH_FUNCTIONS)}'
        f'</br>Date functions which may be used in are: {", ".join(DATE_FUNCTIONS)}',
    )

    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="scoring_models"
    )

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude)

        try:
            ScoringModel.eval_formula(
                self.formula, data=generate_mocked_data(self.formula, self.owner)
            )

        except SyntaxError as ex:
            raise ValidationError(
                {
                    "formula": f'Formula syntax invalid "{ex.text[:ex.offset - 1]}>>>here>>>{ex.text[ex.offset - 1:]}"'
                },
                code="invalid_formula",
            )

        except NameError:
            # No syntax errors in formula
            pass

    @staticmethod
    def eval_formula(formula, data):
        """Eval formula for provided data and return rounded result"""
        try:
            prepared_formula, prepared_data = prepare_answers(formula, data)
            prepared_formula, prepared_data = prepare_formula(
                prepared_formula, prepared_data
            )

            return eval(prepared_formula.format(**prepared_data))

        except ZeroDivisionError:
            return None

    def calculate_points(self, answers):
        """Calculate points based on calculated value.
        For Question.MULTIPLE_CHOICES points determined as sum of separate points for each provided value.
        """

        def calculate_points_for_value(val):
            """Return points based on calculated value"""

            if self.question.type == Question.DATE:
                for value_range in self.dates_ranges.order_by("pk").all():
                    start = (
                        value_range.start if value_range.start is not None else date.min
                    )
                    end = value_range.end if value_range.end is not None else date.max

                    if start <= val < end:
                        return round(value_range.points * self.weight, 2)

            else:
                for value_range in self.ranges.order_by("pk").all():
                    start = (
                        value_range.start
                        if value_range.start is not None
                        else -math.inf
                    )
                    end = value_range.end if value_range.end is not None else math.inf

                    if start <= val < end:
                        return round(value_range.points * self.weight, 2)

            return None

        # Calculate value
        if not self.formula:
            value = answers.get(self.question.field_name)

            if self.question.type == Question.MULTIPLE_CHOICES:
                points = [
                    calculate_points_for_value(v)
                    for v in (
                        list(chain.from_iterable(value.values()))
                        if isinstance(value, dict)
                        else value
                    )
                ]
                points = [p for p in points if p is not None]

                if points:
                    return sum(points)

                return None
        else:
            value = self.eval_formula(self.formula, answers)

        if value is not None:
            if isinstance(value, list):
                return sum([calculate_points_for_value(v) for v in value])

            return calculate_points_for_value(value)

        return None

    def __str__(self):
        return f'Q{self.question.number}: {self.formula if self.formula else f"{{{self.question.field_name}}}"}'


class ValueRange(models.Model):
    scoring_model = models.ForeignKey(
        "ScoringModel", on_delete=models.CASCADE, related_name="ranges"
    )

    start = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Left empty for right-closed range",
    )
    end = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Left empty for left-closed range",
    )

    points = models.IntegerField(help_text="Used for X-axis, Y-axis scores calculation")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scoring_model", "start", "end"], name="unique_range"
            ),
        ]

    def __str__(self):
        return f'[{self.start if self.start is not None else "-inf"}, {self.end if self.end is not None else "+inf"})'


class DatesRange(models.Model):
    scoring_model = models.ForeignKey(
        "ScoringModel", on_delete=models.CASCADE, related_name="dates_ranges"
    )

    start = models.DateField(
        blank=True,
        null=True,
        help_text="Left empty for right-closed range",
    )
    end = models.DateField(
        blank=True,
        null=True,
        help_text="Left empty for left-closed range",
    )

    points = models.IntegerField(help_text="Used for X-axis, Y-axis scores calculation")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scoring_model", "start", "end"], name="unique_date_range"
            ),
        ]

    def __str__(self):
        return f'[{self.start if self.start is not None else "-inf"}, {self.end if self.end is not None else "+inf"})'


class Question(models.Model):
    DATE = "D"
    CHOICES = "CH"
    INTEGER = "I"
    MULTIPLE_CHOICES = "MC"
    OPEN = "O"
    SLIDER = "S"

    TYPE_CHOICES = (
        (DATE, "Date"),
        (CHOICES, "Choices"),
        (INTEGER, "Integer"),
        (MULTIPLE_CHOICES, "Multiple choices"),
        (OPEN, "Open"),
        (SLIDER, "Slider"),
    )

    number = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=1)])
    text = models.CharField(max_length=200)

    field_name = models.CharField(
        max_length=200,
        validators=[validate_field_name],
        help_text="Field name should contain only letters, numbers and underscore",
    )
    multiple_values = models.BooleanField(default=False)
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        help_text="<b>Open</b> question without specific expected answer. "
        'Has associated value "1" if answer provided and "0" otherwise. '
        "Can be used in recommendations rules and in scoring models formulas for X-axis, "
        "Y-axis score calculation. </br> "
        "<b>Choices</b> question with predefined expected answers options. "
        "Answer can be any text. Each answer option has associated value. "
        "Can be used in recommendations rules and in scoring models formulas for X-axis, "
        "Y-axis score calculation. </br>"
        "<b>Multiple choices</b> question with predefined expected answers options. "
        "Answer can be any text. Multiple answers selection allowed. "
        "Each answer option has associated value. Can be used in scoring model for X-axis, "
        "Y-axis score calculation but not in recommendations rules and not in scoring models formulas. </br>"
        "<b>Slider</b> question with predefined range of possible values. "
        "Answer is a value. Can be used in recommendations rules and in scoring models formulas for X-axis, "
        "Y-axis score calculation. </br>"
        "<b>Integer</b> works pretty the same as <b>Slider</b> but without range </br>"
        "<b>Date</b> doesn't have predefined range. </br>",
    )

    # For SLIDER type question
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)

    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="questions"
    )

    class Meta:
        ordering = (
            "owner",
            "number",
        )
        constraints = [
            models.UniqueConstraint(fields=["number", "owner"], name="unique_number"),
            models.UniqueConstraint(
                fields=["field_name", "owner"], name="unique_field_name"
            ),
        ]

    @staticmethod
    def eval_rule(rule, data):
        """Remove RULE_PREFIX and eval rule for provided data"""
        try:
            prepared_rule, prepared_data = prepare_answers(rule, data)
            prepared_rule, prepared_data = prepare_formula(prepared_rule, prepared_data)

            return eval(prepared_rule.removeprefix(RULE_PREFIX).format(**prepared_data))

        except ZeroDivisionError:
            return False

    def check_rule(self, answers):
        try:
            return self.eval_rule(self.recommendation.rule, answers)
        except Recommendation.DoesNotExist:
            return False

    def get_recommendation_dict(self):
        try:
            return {
                "response_text": self.recommendation.response_text,
                "affiliate_name": self.recommendation.affiliate_name,
                "affiliate_image": self.recommendation.affiliate_image,
                "affiliate_link": self.recommendation.affiliate_link,
                "redirect_url": self.recommendation.redirect_url,
            }
        except Recommendation.DoesNotExist:
            return {}

    @staticmethod
    def get_possible_field_names(user):
        """Return field names of questions that can be used in recommendation rule and scoring model formula"""
        return [
            q.field_name
            for q in user.questions.all()
            if q.type
            in [
                Question.SLIDER,
                Question.INTEGER,
                Question.CHOICES,
                Question.OPEN,
                Question.DATE,
            ]
        ]

    def calculate_points(self, answers):
        """Calculate question points using scoring model if question has assigned scoring model"""

        try:
            return self.scoring_model.calculate_points(answers)
        except ScoringModel.DoesNotExist:
            return None

    def __str__(self):
        return f"Q{self.number}. {self.text}"


class Choice(models.Model):
    question = models.ForeignKey(
        "Question", on_delete=models.CASCADE, related_name="choices"
    )

    text = models.CharField(max_length=200)
    slug = models.SlugField()
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Value that will be used in rules calculation. For ranges it is "
        "recommended to use highest number in the range.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["question", "text"], name="unique_choice"),
            models.UniqueConstraint(fields=["question", "slug"], name="unique_slug"),
        ]

    def __str__(self):
        return self.text


class Lead(models.Model):
    lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    x_axis = models.DecimalField(max_digits=12, decimal_places=2)
    y_axis = models.DecimalField(max_digits=12, decimal_places=2)
    total_score = models.DecimalField(max_digits=12, decimal_places=2)

    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="leads"
    )

    def __str__(self):
        return str(self.lead_id)


class Answer(RecommendationFieldsMixin):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="answers")

    field_name = models.CharField(max_length=200)
    response = models.CharField(max_length=200, blank=True)

    value_number = models.PositiveBigIntegerField(blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    date_value = models.DateField(blank=True, null=True)
    values = ArrayField(
        models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True),
        null=True,
    )
    points = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.field_name}: {self.response}"

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["lead", "field_name"], name="unique_answer"
    #         ),
    #     ]
