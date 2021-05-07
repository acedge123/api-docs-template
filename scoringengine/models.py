from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class Rule(models.Model):
    question = models.OneToOneField('Question', on_delete=models.CASCADE, related_name='rule')

    rule = models.CharField(max_length=200)
    response_text = models.CharField(max_length=200)

    affiliate_name = models.CharField(max_length=200, blank=True)
    affiliate_image = models.URLField(max_length=2048, blank=True)
    affiliate_link = models.URLField(max_length=2048, blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        return self.rule


class Question(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(limit_value=1)])
    text = models.CharField(max_length=200)

    field_name = models.CharField(max_length=200)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=1,
                                 validators=[MinValueValidator(limit_value=0)])
    x_axis = models.BooleanField()
    y_axis = models.BooleanField()

    combined_with = models.ManyToManyField('self', blank=True)

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='questions')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['number', 'owner'], name='unique_number'),
            models.UniqueConstraint(fields=['field_name', 'owner'], name='unique_field_name')
        ]

    def __str__(self):
        return f'Q{self.number}. {self.text}'


class Choice(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    point = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['question', 'text'], name='unique_choice'),
        ]

    def __str__(self):
        return self.text
