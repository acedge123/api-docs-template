from datetime import date, timedelta
from random import choice, randint

from django import forms

from scoringengine.models import Question


class TestPostLeadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop("owner")
        super().__init__(*args, **kwargs)

        for question in Question.objects.filter(owner=self.owner).all():
            if question.type == Question.DATE:
                if question.multiple_values:
                    for n in range(0, 5):
                        self.fields[f"{question.field_name}[{n}]"] = forms.DateField(
                            label=f"{question.text}[{n}]",
                            initial=date.today() - timedelta(days=5 - n),
                        )

                else:
                    self.fields[question.field_name] = forms.DateField(
                        label=question.text, initial=date.today()
                    )

            elif question.type == Question.CHOICES:
                choices = list(question.choices.all())
                self.fields[question.field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=[(_c.slug, _c.text) for _c in choices],
                    initial=choice(choices).slug,
                )

            elif question.type == Question.INTEGER:
                if question.multiple_values:
                    for n in range(0, 5):
                        self.fields[f"{question.field_name}[{n}]"] = forms.IntegerField(
                            label=f"{question.text}[{n}]", initial=randint(1, 1000)
                        )
                else:
                    self.fields[question.field_name] = forms.IntegerField(
                        label=question.text, initial=randint(1, 1000)
                    )

            elif question.type == Question.MULTIPLE_CHOICES:
                choices = list(question.choices.all())
                self.fields[question.field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=[(_c.slug, _c.text) for _c in choices],
                    initial=[choice(choices).slug],
                )

            elif question.type == Question.SLIDER:
                if question.multiple_values:
                    for n in range(0, 5):
                        self.fields[f"{question.field_name}[{n}]"] = forms.IntegerField(
                            label=f"{question.text}[{n}]",
                            min_value=question.min_value,
                            max_value=question.max_value,
                            initial=randint(question.min_value, question.max_value),
                        )
                else:
                    self.fields[question.field_name] = forms.IntegerField(
                        label=question.text,
                        min_value=question.min_value,
                        max_value=question.max_value,
                        initial=randint(question.min_value, question.max_value),
                    )

            elif question.type == Question.OPEN:
                self.fields[question.field_name] = forms.CharField(
                    label=question.text,
                    initial="Open answer",
                )

    def clean(self):
        for field, value in self.cleaned_data.items():
            if isinstance(value, date):
                self.cleaned_data[field] = value.strftime("%Y-%m-%d")
