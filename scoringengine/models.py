import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

RULE_PREFIX = 'If '
RULE_REGEX = r''  # TODO: Add this


class Rule(models.Model):
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='rule')

    # TODO: Improve help text
    rule_text = models.CharField(max_length=200,
                                 help_text='Use arithmetic operations and logical operations "and", "or", "not"')
    response_text = models.CharField(max_length=200)

    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        return f'Q{self.question.number}: {self.rule_text}'


class Question(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(limit_value=1)])
    text = models.CharField(max_length=200)

    field_name = models.CharField(max_length=200)
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

    def check_rule(self, answers):
        try:
            rule = self.rule.rule_text.removeprefix(RULE_PREFIX)
            return eval(rule.format(**answers))
        except Rule.DoesNotExist:
            return False

    def get_recommendation_dict(self):
        try:
            return {
                'response_text': f'Q{self.number}. {self.rule.response_text}',
                'affiliate_name': self.rule.affiliate_name,
                'affiliate_image': self.rule.affiliate_image,
                'affiliate_link': self.rule.affiliate_link,
            }
        except Rule.DoesNotExist:
            return {}

    def __str__(self):
        return f'Q{self.number}. {self.text}'


class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
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

    def __str__(self):
        return f'{self.field_name}: {self.response}'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['lead', 'field_name'], name='unique_answer'),
        ]
