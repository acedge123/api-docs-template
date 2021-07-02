import re
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

RULE_PREFIX = 'If'
RULE_ARITHMETIC_OPERATORS = ['+', '-', '*', '/']
RULE_COMPARISON_OPERATORS = ['>', '<', '==', '!=', '>=', '<=']
RULE_LOGICAL_OPERATORS = ['and', 'or', 'not']
RULE_NUMBER = r'[0-9.]+'
RULE_VARIABLE = r'\w+'
RULE_REGEX = rf'(^{RULE_PREFIX})(({RULE_NUMBER}|{{{RULE_VARIABLE}}})|({"|".join([re.escape(o) for o in RULE_ARITHMETIC_OPERATORS + RULE_COMPARISON_OPERATORS + RULE_LOGICAL_OPERATORS])})|\s*)+'


@receiver(post_save, sender=get_user_model())
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """ Generate API token for each newly created user """

    if created:
        Token.objects.create(user=instance)


def validate_field_name(value):
    """ Check that entered field name is valid rule variable """

    if not re.fullmatch(RULE_VARIABLE, value):
        raise ValidationError('"%(field_name)s" is not valid Field name', params={'field_name': value}, code='invalid_field_name')


def validate_rule(value):
    """ Check that entered rule is valid: contain only allowed parts and can be evaluated using "eval" function """

    if not re.fullmatch(RULE_REGEX, value):
        raise ValidationError('Rule is invalid', params={'rule': value}, code='invalid_rule')

    mocked_data = {k: 1 for k in re.findall(fr'{{({RULE_VARIABLE})}}', value)}

    try:
        Question.eval_rule(value, data=mocked_data)
    except SyntaxError as ex:
        raise ValidationError(f'Rule syntax invalid "{RULE_PREFIX} {ex.text[:ex.offset - 1]}>>>here>>>{ex.text[ex.offset - 1:]}"',
                              params={'rule': value}, code='invalid_rule')


class Recommendation(models.Model):
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='recommendation')

    rule = models.CharField(
        max_length=200, validators=[validate_rule],
        help_text=f'Rule should start with "If" and may contain only valid numbers, questions with choices '
                  f'"Field names" in curly braces (e.g. {{field_name}}) '
                  f'combined with '
                  f'arithmetic ({", ".join(RULE_ARITHMETIC_OPERATORS)}), '
                  f'comparison ({", ".join(RULE_COMPARISON_OPERATORS)}) and '
                  f'logical operations ({", ".join(RULE_LOGICAL_OPERATORS)})')
    response_text = models.CharField(max_length=200, blank=True)

    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)

    redirect_url = models.URLField(max_length=2048, blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='recommendations')

    def __str__(self):
        return f'Q{self.question.number}: {self.rule}'


class Question(models.Model):
    number = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=1)])
    text = models.CharField(max_length=200)

    field_name = models.CharField(
        max_length=200, validators=[validate_field_name],
        help_text='Field name should contain only letters, numbers and underscore')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
                                 help_text='<b>Note:</b> Used only for question with choices',
                                 validators=[MinValueValidator(limit_value=0)])
    x_axis = models.BooleanField(help_text='<b>Note:</b> Used only for question with choices')
    y_axis = models.BooleanField(help_text='<b>Note:</b> Used only for question with choices')

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

        return eval(rule.removeprefix(RULE_PREFIX).format(**data))

    def check_rule(self, answers):
        try:
            return self.eval_rule(self.recommendation.rule, answers)
        except Recommendation.DoesNotExist:
            return False

    def get_recommendation_dict(self):
        try:
            return {
                'response_text': f'Q{self.number}. {self.recommendation.response_text}' if self.recommendation.response_text else '',
                'affiliate_name': self.recommendation.affiliate_name,
                'affiliate_image': self.recommendation.affiliate_image,
                'affiliate_link': self.recommendation.affiliate_link,
                'redirect_url': self.recommendation.redirect_url
            }
        except Recommendation.DoesNotExist:
            return {}

    @staticmethod
    def get_possible_field_names(user):
        """ Return field names of questions that has choices """
        return [q.field_name for q in user.questions.all() if q.choices.exists()]

    def __str__(self):
        return f'Q{self.number}. {self.text}'


class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    slug = models.SlugField()
    value = models.DecimalField(
        max_digits=12, decimal_places=2, help_text='Value that will be used in rules calculation. For ranges it is '
                                                   'recommended to use highest number in the range.')
    points = models.IntegerField(help_text='Used for X-axis, Y-axis scores calculation')

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
