import math
import re
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

ARITHMETIC_OPERATORS = ['+', '-', '*', '/']
COMPARISON_OPERATORS = ['>', '<', '==', '!=', '>=', '<=']
LOGICAL_OPERATORS = ['and', 'or', 'not']

NUMBER_REGEX = r'[0-9.]+'
FIELD_NAME_REGEX = r'\w+'

RULE_PREFIX = 'If'
RULE_REGEX = rf'(^{RULE_PREFIX})(({NUMBER_REGEX}|{{{FIELD_NAME_REGEX}}})|({"|".join([re.escape(o) for o in ARITHMETIC_OPERATORS + COMPARISON_OPERATORS + LOGICAL_OPERATORS])})|\s*|[()]*)+'

FORMULA_REGEX = rf'(({NUMBER_REGEX}|{{{FIELD_NAME_REGEX}}})|({"|".join([re.escape(o) for o in ARITHMETIC_OPERATORS])})|\s*|[()]*)+'


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """ Generate API token for each newly created user """

    if created:
        Token.objects.create(user=instance)


def validate_field_name(value):
    """ Check that entered field name is valid rule variable """

    if not re.fullmatch(FIELD_NAME_REGEX, value):
        raise ValidationError('"%(field_name)s" is not valid Field name', params={'field_name': value}, code='invalid_field_name')


def validate_rule(value):
    """ Check that entered rule is valid: contain only allowed parts and can be evaluated using "eval" function """

    if not re.fullmatch(RULE_REGEX, value):
        raise ValidationError('Rule is invalid', code='invalid_rule')

    mocked_data = {k: f'{{{k}}}' for k in re.findall(fr'{{({FIELD_NAME_REGEX})}}', value)}

    try:
        Question.eval_rule(value, data=mocked_data)
    except SyntaxError as ex:
        raise ValidationError(
            f'Rule syntax invalid "{RULE_PREFIX} {ex.text[:ex.offset - 1]}>>>here>>>{ex.text[ex.offset - 1:]}"',
            code='invalid_rule'
        )
    except NameError:
        # No syntax errors in rule
        pass


def validate_formula(value):
    """ Check that entered formula is valid: contain only allowed parts and can be evaluated using "eval" function """

    if not re.fullmatch(FORMULA_REGEX, value):
        raise ValidationError('Formula is invalid', code='invalid_formula')

    mocked_data = {k: f'{{{k}}}' for k in re.findall(fr'{{({FIELD_NAME_REGEX})}}', value)}

    try:
        ScoringModel.eval_formula(value, data=mocked_data)
    except SyntaxError as ex:
        raise ValidationError(
            f'Formula syntax invalid "{ex.text[:ex.offset - 1]}>>>here>>>{ex.text[ex.offset - 1:]}"',
            code='invalid_formula'
        )
    except NameError:
        # No syntax errors in formula
        pass


class Recommendation(models.Model):
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='recommendation')

    rule = models.CharField(
        max_length=200, validators=[validate_rule],
        help_text=f'Rule should start with "If" and may contain only valid numbers, questions with choices '
                  f'"Field names" in curly braces (e.g. {{field_name}}) '
                  f'combined with '
                  f'arithmetic ({", ".join(ARITHMETIC_OPERATORS)}), '
                  f'comparison ({", ".join(COMPARISON_OPERATORS)}), '
                  f'logical operations ({", ".join(LOGICAL_OPERATORS)})'
                  f'and parentheses')
    response_text = models.CharField(max_length=200, blank=True)

    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)

    redirect_url = models.URLField(max_length=2048, blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recommendations')

    def __str__(self):
        return f'Q{self.question.number}: {self.rule}'


class ScoringModel(models.Model):
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='scoring_model')

    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
                                 validators=[MinValueValidator(limit_value=0)])
    x_axis = models.BooleanField()
    y_axis = models.BooleanField()

    formula = models.CharField(
        max_length=200, blank=True, validators=[validate_formula],
        help_text=f'Leave empty to select points based on direct value from associated question.</br>'
                  f'Add expression with "Field names" in curly braces (e.g. {{field_name}}), '
                  f'arithmetic ({", ".join(ARITHMETIC_OPERATORS)}) operations '
                  f'and parentheses '
                  f'to select points based on expression result.')

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='scoring_models')

    @staticmethod
    def eval_formula(formula, data):
        """ Eval formula for provided data and return rounded result """
        try:
            return eval(formula.format(**data))
        except ZeroDivisionError:
            return None

    def calculate_points(self, answers):
        # Calculate value
        if not self.formula:
            value = answers.get(self.question.field_name)
        else:
            value = self.eval_formula(self.formula, answers)

        if value is not None:
            # Get points based on calculated value
            for value_range in self.ranges.order_by('pk').all():
                start = value_range.start if value_range.start is not None else -math.inf
                end = value_range.end if value_range.end is not None else math.inf

                if start <= value < end:
                    return round(value_range.points * self.weight, 2)

        return None

    def __str__(self):
        return f'Q{self.question.number}: {self.formula if self.formula else f"{{{self.question.field_name}}}"}'


class ValueRange(models.Model):
    scoring_model = models.ForeignKey('ScoringModel', on_delete=models.CASCADE, related_name='ranges')

    start = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                help_text='Left empty for right-closed range')
    end = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                              help_text='Left empty for left-closed range')

    points = models.IntegerField(help_text='Used for X-axis, Y-axis scores calculation')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['scoring_model', 'start', 'end'], name='unique_range'),
        ]

    def __str__(self):
        return f'[{self.start if self.start is not None else "-inf"}, {self.end if self.end is not None else "+inf"})'


class Question(models.Model):
    OPEN = 'O'
    CHOICES = 'CH'
    SLIDER = 'S'

    TYPE_CHOICES = (
        (OPEN, 'Open'),
        (CHOICES, 'Choices'),
        (SLIDER, 'Slider'),
    )

    number = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=1)])
    text = models.CharField(max_length=200)

    field_name = models.CharField(
        max_length=200, validators=[validate_field_name],
        help_text='Field name should contain only letters, numbers and underscore')
    type = models.CharField(
        max_length=2, choices=TYPE_CHOICES,
        help_text='<b>Open</b> questions without specific expected answer. Has no associated value, '
                  'so can not be used in recommendations rules and in scoring models formulas for X-axis, Y-axis score '
                  'calculation. </br> '
                  '<b>Choices</b> question with predefined expected answers options. Answer can be any text. '
                  'Each answer option has associated value. Can be used in recommendations rules and in scoring models '
                  'formulas for X-axis, Y-axis score calculation. </br>'
                  '<b>Slider</b> question with predefined range of possible values. Answer is a value. '
                  'Can be used in recommendations rules and in scoring models formulas for X-axis, Y-axis score '
                  'calculation. </br>'
    )

    # For SLIDER type question
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='questions')

    class Meta:
        ordering = ('owner', 'number',)
        constraints = [
            models.UniqueConstraint(fields=['number', 'owner'], name='unique_number'),
            models.UniqueConstraint(fields=['field_name', 'owner'], name='unique_field_name')
        ]

    @staticmethod
    def eval_rule(rule, data):
        """ Remove RULE_PREFIX and eval rule for provided data """
        try:
            return eval(rule.removeprefix(RULE_PREFIX).format(**data))
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
                'response_text': self.recommendation.response_text,
                'affiliate_name': self.recommendation.affiliate_name,
                'affiliate_image': self.recommendation.affiliate_image,
                'affiliate_link': self.recommendation.affiliate_link,
                'redirect_url': self.recommendation.redirect_url
            }
        except Recommendation.DoesNotExist:
            return {}

    @staticmethod
    def get_possible_field_names(user):
        """ Return field names of questions that has values """
        return [q.field_name for q in user.questions.all() if q.type in (Question.SLIDER, Question.CHOICES)]

    def calculate_points(self, answers):
        """ Calculate question points using scoring model if question type is appropriate
            and question has assigned scoring model
        """

        if self.type == Question.OPEN:
            return None

        try:
            return self.scoring_model.calculate_points(answers)
        except ScoringModel.DoesNotExist:
            return None

    def __str__(self):
        return f'Q{self.number}. {self.text}'


class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='choices')

    text = models.CharField(max_length=200)
    slug = models.SlugField()
    value = models.DecimalField(
        max_digits=12, decimal_places=2, help_text='Value that will be used in rules calculation. For ranges it is '
                                                   'recommended to use highest number in the range.')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'], name='unique_choice'),
            models.UniqueConstraint(fields=['question', 'slug'], name='unique_slug'),
        ]

    def __str__(self):
        return self.text


class Lead(models.Model):
    lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    timestamp = models.DateTimeField(auto_now_add=True)

    x_axis = models.DecimalField(max_digits=5, decimal_places=2)
    y_axis = models.DecimalField(max_digits=5, decimal_places=2)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='leads')

    def __str__(self):
        return str(self.lead_id)


class Answer(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='answers')

    field_name = models.CharField(max_length=200)
    response = models.CharField(max_length=200)

    value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    points = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    response_text = models.CharField(max_length=200, blank=True)
    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)
    redirect_url = models.URLField(max_length=2048, blank=True)

    def __str__(self):
        return f'{self.field_name}: {self.response}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lead', 'field_name'], name='unique_answer'),
        ]
