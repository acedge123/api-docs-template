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
        raise ValidationError('"%(value)s" is not valid Field name', params={'field_name': value}, code='invalid_field_name')


def validate_choice_text(value):
    """ Check that entered question choice text is contain at least one positive number """

    if not re.findall(r'\d+', value):
        raise ValidationError('Text should contain at least one positive number', params={'choice_text': value},
                              code='invalid_choice_text')


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


class Rule(models.Model):
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='rule')

    rule = models.CharField(
        max_length=200, validators=[validate_rule],
        help_text=f'Rule should start with "If" and may contain only valid numbers, questions "Field names" '
                  f'in curly braces (e.g. {{field_name}}) '
                  f'combined with '
                  f'arithmetic ({", ".join(RULE_ARITHMETIC_OPERATORS)}), '
                  f'comparison ({", ".join(RULE_COMPARISON_OPERATORS)}) and '
                  f'logical operations ({", ".join(RULE_LOGICAL_OPERATORS)})')
    response_text = models.CharField(max_length=200, blank=True)

    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)

    redirect_url = models.URLField(max_length=2048, blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        return f'Q{self.question.number}: {self.rule}'


class Question(models.Model):
    number = models.PositiveIntegerField(validators=[MinValueValidator(limit_value=1)])
    text = models.CharField(max_length=200)

    field_name = models.CharField(
        max_length=200, validators=[validate_field_name],
        help_text='Field name should contain only letters, numbers and underscore')
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
                                 validators=[MinValueValidator(limit_value=0)])
    x_axis = models.BooleanField()
    y_axis = models.BooleanField()

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='questions')

    class Meta:
        ordering = ('owner', 'number',)
        constraints = [
            models.UniqueConstraint(fields=['number', 'owner'], name='unique_number'),
            models.UniqueConstraint(fields=['field_name', 'owner'], name='unique_field_name')
        ]

    @staticmethod
    def extract_answers_values(answers):
        """ Extract max number from answers, to be able check rule. """

        return {field_name: max([int(w) for w in re.findall(r'\d+', answer)]) for field_name, answer in answers.items()}

    @staticmethod
    def eval_rule(rule, data):
        """ Remove RULE_PREFIX and eval rule for provided data """

        return eval(rule.removeprefix(RULE_PREFIX).format(**data))

    def check_rule(self, answers):
        try:
            data = self.extract_answers_values(answers)
            return self.eval_rule(self.rule.rule, data)
        except Rule.DoesNotExist:
            return False

    def get_recommendation_dict(self):
        try:
            return {
                'response_text': f'Q{self.number}. {self.rule.response_text}' if self.rule.response_text else '',
                'affiliate_name': self.rule.affiliate_name,
                'affiliate_image': self.rule.affiliate_image,
                'affiliate_link': self.rule.affiliate_link,
                'redirect_url': self.rule.redirect_url
            }
        except Rule.DoesNotExist:
            return {}

    def __str__(self):
        return f'Q{self.number}. {self.text}'


class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(
        max_length=200, validators=[validate_choice_text],
        help_text='Text should contain at least one positive number. Max number will be used in rules checks')
    points = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'], name='unique_choice'),
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
