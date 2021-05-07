from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from scoringengine.models import Question, Choice, Rule

admin.site.site_title = 'Scoring engine site admin'
admin.site.site_header = 'Scoring engine administration'


class RestrictedAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj=None) or []

        if not request.user.is_superuser:
            exclude += ['owner']

        return exclude

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

    def save_model(self, request, obj, form, change):
        if obj.owner_id is None:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


class QuestionAdmin(RestrictedAdmin):
    inlines = [ChoiceInline]
    list_display = ('__str__', 'field_name')
    ordering = ['owner__id', 'number']

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'combined_with':
            kwargs['queryset'] = Question.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RuleAdmin(RestrictedAdmin):
    list_display = ('rule', 'response_text')
    ordering = ['question__number']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'question':
            kwargs['queryset'] = Question.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Rule, RuleAdmin)
