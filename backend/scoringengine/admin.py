import re

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Q
from django.template.response import TemplateResponse
from django.urls import path
from import_export.admin import ExportMixin
from rangefilter.filters import (
    BaseRangeFilter,
    DateRangeFilter,
    DateRangeFilterBuilder,
    NumericRangeFilter,
    NumericRangeFilterBuilder,
)
from rest_framework.authtoken import admin as drf_admin
from rest_framework.authtoken.models import TokenProxy

from scoringengine.forms import TestPostLeadForm
from scoringengine.helpers import (
    calculate_x_and_y_scores,
    collect_answers_values,
    collect_recommendations,
)
from scoringengine.models import (
    Answer,
    AnswerLog,
    Choice,
    DatesRange,
    Lead,
    LeadLog,
    Question,
    Recommendation,
    RecommendationFieldsMixin,
    ScoringModel,
    ValueRange,
)
from scoringengine.resources import LeadResource

User = get_user_model()

admin.site.site_title = "Scoring engine site admin"
admin.site.site_header = "Scoring engine administration"


class OwnAdminSite(admin.AdminSite):
    site_title = "Scoring engine site admin"
    site_header = "Scoring engine administration"

    def get_app_list(self, request):
        app_list = super().get_app_list(request)

        for app in app_list:
            if app["app_label"] == "scoringengine":
                app["models"].append(
                    {
                        "name": "Test post lead",
                        "object_name": "testpostlead",
                        "admin_url": "/admin/scoringengine/test-post-lead/",
                        "add_url": False,
                        "view_only": True,
                    }
                )

        return app_list

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "scoringengine/test-post-lead/",
                # self.test_post_lead,
                admin_site.admin_view(self.test_post_lead),
                name="test_post_lead",
            ),
        ]
        return my_urls + urls

    def test_post_lead(self, request):
        app_list = self.get_app_list(request)
        form = TestPostLeadForm(data=request.POST, owner=request.user)

        response = {}

        if request.method == "POST" and form.is_valid():
            answers_data = [
                {
                    "field_name": field_name,
                    "response": (
                        ",".join(response) if isinstance(response, list) else response
                    ),
                }
                for field_name, response in form.cleaned_data.items()
            ]
            collect_answers_values(request.user, answers_data)

            x_axis, y_axis = calculate_x_and_y_scores(request.user, answers_data)
            total_score = x_axis + y_axis

            collect_recommendations(request.user, answers_data)

            response["x_axis"] = x_axis
            response["y_axis"] = y_axis
            response["total_score"] = total_score

            response["recommendations"] = dict(
                [
                    (
                        answer["field_name"],
                        {
                            "response_text": answer["response_text"],
                            "affiliate_name": answer["affiliate_name"],
                            "affiliate_image": answer["affiliate_image"],
                            "affiliate_link": answer["affiliate_link"],
                            "redirect_url": answer["redirect_url"],
                        },
                    )
                    for answer in answers_data
                    if "response_text" in answer
                ]
            )

        context = {
            **self.each_context(request),
            "title": "Test post lead",
            "app_list": app_list,
            "form": form,
            "response": response,
        }

        request.current_app = self.name

        return TemplateResponse(request, "admin/test_post_lead.html", context)


admin_site = OwnAdminSite()


class ValidateFieldNameModelAdminForm(forms.ModelForm):
    """Check that field contains only valid field names"""

    field_to_validate = None

    def clean(self):
        cleaned_data = super().clean()

        if self.field_to_validate:
            value = cleaned_data.get(self.field_to_validate)

            if value:
                user = cleaned_data.get("owner")

                invalid_field_name_errors = []
                for field_name in re.findall(r"{(\w*)}", value):
                    if field_name not in Question.get_possible_field_names(user):
                        invalid_field_name_errors.append(
                            ValidationError(
                                'Field name "%(value)s" used in %(field)s is not valid.',
                                params={
                                    "value": field_name,
                                    "field": self.field_to_validate.title(),
                                },
                            )
                        )

                if invalid_field_name_errors:
                    raise ValidationError(invalid_field_name_errors)

        return cleaned_data


class RestrictedAdmin(admin.ModelAdmin):
    field_to_extend_help_text = None

    def get_queryset(self, request):
        query_set = super().get_queryset(request)

        if not request.user.is_superuser:
            if hasattr(request.user, "catalogue_as_master"):
                query_set = query_set.filter(
                    owner__in=request.user.catalogue_as_master.slaves.all()
                )
            else:
                query_set = query_set.filter(owner=request.user)

        return query_set

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        if request.user.is_superuser or hasattr(request.user, "catalogue_as_master"):
            list_display += ("owner",)

        return list_display

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=None, change=False, **kwargs)

        # Hide owner field and pre-populate it with current user.
        # This is needed for unique constraints validation.
        if not request.user.is_superuser:
            if hasattr(request.user, "catalogue_as_master"):
                form.base_fields["owner"].required = True
                form.base_fields["owner"].queryset = (
                    request.user.catalogue_as_master.slaves.all()
                )

            else:
                form.base_fields["owner"].widget = forms.HiddenInput()
                form.base_fields["owner"].initial = request.user
        else:
            form.base_fields["owner"].required = True
            form.base_fields["owner"].queryset = User.objects.all()

        if self.field_to_extend_help_text:
            possible_field_names = (
                ", ".join(Question.get_possible_field_names(request.user))
                or "No appropriate questions created yet"
            )

            # Extend model help_text to show possible field names
            form.base_fields[
                self.field_to_extend_help_text
            ].help_text += (
                f"</br></br>Possible field names: <b>{possible_field_names}</b>"
            )

            return form

        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ensure that user can set only himself as owner
        if db_field.name == "owner":
            kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ChoiceInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()

        # Require at least one Choice for Choices question type
        if self.instance.type in (Question.CHOICES, Question.MULTIPLE_CHOICES):
            count = 0
            for form in self.forms:
                try:
                    if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                        count += 1
                except AttributeError:
                    # annoyingly, if a subform is invalid Django explicitly raises
                    # an AttributeError for cleaned_data
                    pass
            if count < 1:
                raise ValidationError("Question must have at least one choice")


class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceInlineFormset
    extra = 0
    prepopulated_fields = {"slug": ("text",)}


class QuestionAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        min_value = cleaned_data.get("min_value")
        max_value = cleaned_data.get("max_value")

        if min_value is not None and max_value is not None and min_value >= max_value:
            raise ValidationError("Min value must be less than Max value.")

        return cleaned_data

    def clean_min_value(self):
        question_type = self.cleaned_data.get("type")
        min_value = self.cleaned_data.get("min_value")

        if question_type == Question.SLIDER and min_value is None:
            raise ValidationError("This field is required.")

        return self.cleaned_data.get("min_value")

    def clean_max_value(self):
        question_type = self.cleaned_data.get("type")
        max_value = self.cleaned_data.get("max_value")

        if question_type == Question.SLIDER and max_value is None:
            raise ValidationError("This field is required.")

        return self.cleaned_data.get("max_value")


class QuestionAdmin(RestrictedAdmin):
    form = QuestionAdminForm
    inlines = [ChoiceInline]
    list_display = ("__str__", "field_name", "type", "multiple_values")
    ordering = ["owner__id", "number"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "api_request_template/",
                self.admin_site.admin_view(self.api_request_template),
                name="api_request_template",
            ),
        ]
        return my_urls + urls

    def api_request_template(self, request):
        questions = request.user.questions.order_by("pk")

        headers = [
            f"Authorization: Token {request.user.auth_token}",
            "Content-Type: application/json",
        ]

        answers = {}
        for q in questions:
            if q.type == Question.MULTIPLE_CHOICES:
                answers[q.field_name] = (
                    f"put one or multiple responses separated by commas for '{q.field_name}' question here"
                )
            else:
                answers[q.field_name] = (
                    f"put response for '{q.field_name}' question here"
                )

        payload = {
            "lead_id": "(optional) uuid4 lead identifier, if not used just remove whole line",
            "answers": answers,
        }

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(request),
            "title": "API request template",
            "headers": headers,
            "payload": payload,
        }

        return TemplateResponse(
            request, "admin/scoringengine/question/api_request_template.html", context
        )

    class Media:
        js = ("admin/js/question_admin.js",)


class RuleAdminForm(ValidateFieldNameModelAdminForm):
    field_to_validate = "rule"


class RecommendationFieldsAdminMixin:
    """Rearrange fields to put fields from RecommendationFieldsMixin at last place"""

    def get_fields(self, request, obj=None):
        last_fields = RecommendationFieldsMixin.fields
        fields = super().get_fields(request, obj)

        for field in last_fields:
            if field in fields:
                fields.remove(field)
                fields.append(field)

        return fields


class RecommendationAdmin(RecommendationFieldsAdminMixin, RestrictedAdmin):
    form = RuleAdminForm
    list_display = ("__str__", "response_text", "affiliate_name", "redirect_url")
    ordering = ["question__number"]

    field_to_extend_help_text = "rule"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ensure that user can select only questions he own
        if db_field.name == "question":
            kwargs["queryset"] = Question.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ValueRangeInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                    start = form.cleaned_data.get("start")
                    end = form.cleaned_data.get("end")

                    if start is not None and end is not None and start > end:
                        raise ValidationError(
                            "Start of range must be less than or equal to End"
                        )
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicitly raises
                # an AttributeError for cleaned_data
                pass


class ValueRangeInline(admin.TabularInline):
    model = ValueRange
    formset = ValueRangeInlineFormset
    extra = 0
    min_num = 0


class DatesRangeInline(admin.TabularInline):
    model = DatesRange
    formset = ValueRangeInlineFormset
    extra = 0
    min_num = 0


class ScoringModelAdminForm(ValidateFieldNameModelAdminForm):
    field_to_validate = "formula"


class ScoringModelAdmin(RestrictedAdmin):
    form = ScoringModelAdminForm
    inlines = [ValueRangeInline, DatesRangeInline]
    list_display = ("__str__", "weight", "x_axis", "y_axis")
    ordering = ["question__number"]

    field_to_extend_help_text = "formula"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ensure that user can select only available questions he own
        if db_field.name == "question":
            if not request.user.is_superuser:
                if hasattr(request.user, "catalogue_as_master"):
                    kwargs["queryset"] = Question.objects.filter(
                        owner=request.user.catalogue_as_master.slaves.all()
                    )
                else:
                    kwargs["queryset"] = Question.objects.filter(owner=request.user)

            else:
                kwargs["queryset"] = Question.objects.all()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_inlines(self, request, obj):
        if obj and hasattr(obj, "question") and obj.question.type != Question.DATE:
            return [ValueRangeInline]

        return [ValueRangeInline, DatesRangeInline]


class AnswerInline(RecommendationFieldsAdminMixin, admin.StackedInline):
    model = Answer
    extra = 0


class AnswerLogInline(RecommendationFieldsAdminMixin, admin.StackedInline):
    model = AnswerLog
    extra = 0


class AnswersQuerysetFilterMixin:
    def __init__(self, field, request, params, model, model_admin, field_path):
        field_name = getattr(self, "field_name")
        self.lookup_kwarg_gte = f"{field_name}__gte"
        self.lookup_kwarg_lte = f"{field_name}__lte"

        super(BaseRangeFilter, self).__init__(
            field, request, params, model, model_admin, field_path
        )

        self.default_gte, self.default_lte = self._get_default_values(
            request, model_admin, field_path
        )
        self.title = self._get_default_title(request, model_admin, field_path)

        self.request = request
        self.model_admin = model_admin
        self.form = self.get_form(request)

    def queryset(self, request, queryset):
        if self.form.is_valid():
            field_path = self.field_path.replace("answers__", "")
            field_name = getattr(self, "field_name")
            return queryset.filter(
                Exists(
                    Answer.objects.filter(
                        lead_id=OuterRef("pk"),
                        field_name=field_name,
                        **dict(
                            [
                                (key.replace(field_name, field_path), value)
                                for key, value in self.form.cleaned_data.items()
                                if value is not None
                            ]
                        ),
                    )
                )
            )

        return queryset


def AnswerRangeFilterBuilder(
    title, question_type, field_name, default_start=None, default_end=None
):
    filter_cls = type(
        str("AnswerNumericRangeFilter"),
        (
            AnswersQuerysetFilterMixin,
            DateRangeFilter if question_type == Question.DATE else NumericRangeFilter,
        ),
        {
            "__from_builder": True,
            "default_title": title,
            "field_name": field_name,
            "default_start": default_start,
            "default_end": default_end,
        },
    )

    return filter_cls


class LeadAdminAbstract(ExportMixin, RestrictedAdmin):
    list_display = (
        "lead_id",
        "x_axis",
        "y_axis",
        "total_score",
        "timestamp",
    )
    ordering = ["owner__id", "-timestamp"]
    readonly_fields = ("timestamp",)
    resource_classes = [LeadResource]
    search_fields = ("lead_id", "answers__response")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_list_filter(self, request):
        questions_qs = Question.objects.filter(
            type__in=[Question.DATE, Question.INTEGER, Question.SLIDER]
        )

        if isinstance(request.user, User) and hasattr(
            request.user, "catalogue_as_master"
        ):
            questions_qs = questions_qs.filter(
                Q(owner=request.user)
                | Q(owner__in=request.user.catalogue_as_master.slaves.all())
            )
        else:
            questions_qs = questions_qs.filter(owner=request.user)

        questions = {}
        for question in questions_qs.order_by("number"):
            if question.field_name in questions:
                continue

            questions[question.field_name] = {
                "title": question.text,
                "question_type": question.type,
                "field_name": question.field_name,
                "default_start": (
                    question.min_value if question.type == Question.SLIDER else None
                ),
                "default_end": (
                    question.max_value if question.type == Question.SLIDER else None
                ),
            }

        answers_fields = [
            (
                (
                    "answers__date_value"
                    if question["question_type"] == Question.DATE
                    else "answers__value"
                ),
                AnswerRangeFilterBuilder(**question),
            )
            for question in questions.values()
        ]

        return (
            ("x_axis", NumericRangeFilterBuilder("X Axis Range")),
            ("y_axis", NumericRangeFilterBuilder("Y Axis Range")),
            ("total_score", NumericRangeFilterBuilder("Total Score Range")),
            ("timestamp", DateRangeFilterBuilder("Timestamp Range")),
            *answers_fields,
        )


class LeadAdmin(LeadAdminAbstract):
    inlines = [AnswerInline]


class LeadLogAdmin(LeadAdminAbstract):
    inlines = [AnswerLogInline]


class TokenAdmin(drf_admin.TokenAdmin):
    def get_queryset(self, request):
        # Ensure user can access only his api tokens
        query_set = super().get_queryset(request)

        if not request.user.is_superuser:
            query_set = query_set.filter(user=request.user)

        return query_set

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ensure user can create api token only for himself
        if db_field.name == "user":
            if not request.user.is_superuser:
                kwargs["queryset"] = User.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin_site.register(Question, QuestionAdmin)
admin_site.register(Recommendation, RecommendationAdmin)
admin_site.register(ScoringModel, ScoringModelAdmin)
admin_site.register(Lead, LeadAdmin)
admin_site.register(LeadLog, LeadLogAdmin)

admin_site.register(TokenProxy, TokenAdmin)
