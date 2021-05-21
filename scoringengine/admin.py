import re

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import CheckboxSelectMultiple
from rest_framework.authtoken import admin as drf_admin
from rest_framework.authtoken.models import TokenProxy

from scoringengine.models import Question, Choice, Rule, Lead, Answer

admin.site.site_title = 'Scoring engine site admin'
admin.site.site_header = 'Scoring engine administration'


class RestrictedAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        query_set = super().get_queryset(request)

        if not request.user.is_superuser:
            query_set = query_set.filter(owner=request.user)

        return query_set

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        if request.user.is_superuser:
            list_display += ('owner',)

        return list_display

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=None, change=False, **kwargs)

        # Hide owner field and pre-populate it with current user.
        # This is needed for unique constraints validation.
        form.base_fields['owner'].widget = forms.HiddenInput()
        form.base_fields['owner'].initial = request.user

        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'owner':
            kwargs['queryset'] = get_user_model().objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    min_num = 1


class QuestionAdmin(RestrictedAdmin):
    inlines = [ChoiceInline]
    list_display = ('__str__', 'field_name', 'x_axis', 'y_axis')
    ordering = ['owner__id', 'number']

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'combined_with':
            kwargs['queryset'] = Question.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RuleAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        # Check that rule contain only existing field names
        rule = cleaned_data.get('rule')

        if rule:
            user = cleaned_data.get('owner')

            valid_field_names = [q.field_name for q in user.questions.all()]

            invalid_field_name_errors = []
            for rule_field_name in re.findall(r'{(\w*)}', rule):
                if rule_field_name not in valid_field_names:
                    invalid_field_name_errors.append(ValidationError('Field name "%(value)s" used in Rule is not existed',
                                                                     params={'value': rule_field_name}))

            if invalid_field_name_errors:
                raise ValidationError(invalid_field_name_errors)

        return cleaned_data


class RuleAdmin(RestrictedAdmin):
    form = RuleAdminForm
    list_display = ('__str__', 'response_text', 'affiliate_name', 'redirect_url')
    ordering = ['question__number']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'question':
            kwargs['queryset'] = Question.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=None, change=False, **kwargs)

        existing_field_names = ", ".join([q.field_name for q in request.user.questions.all()]) or 'No questions created yet'

        # Extend rule help_text to show possible field names
        form.base_fields['rule'].help_text += f'</br></br>Existing field names: <b>{existing_field_names}</b>'

        return form


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    readonly_fields = ()


class LeadAdmin(RestrictedAdmin):
    inlines = [AnswerInline]
    list_display = ('lead_id', 'timestamp')
    ordering = ['owner__id', 'lead_id']
    readonly_fields = ('timestamp',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TokenAdmin(drf_admin.TokenAdmin):
    def get_queryset(self, request):
        query_set = super().get_queryset(request)

        if not request.user.is_superuser:
            query_set = query_set.filter(user=request.user)

        return query_set

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'user':
            if not request.user.is_superuser:
                kwargs['queryset'] = get_user_model().objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(Lead, LeadAdmin)

admin.site.unregister(TokenProxy)
admin.site.register(TokenProxy, TokenAdmin)
