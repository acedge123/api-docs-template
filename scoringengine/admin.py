import re

from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.template.response import TemplateResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import mark_safe

from rest_framework.authtoken import admin as drf_admin
from rest_framework.authtoken.models import TokenProxy

from scoringengine.models import (
    Question,
    Choice,
    Recommendation,
    ScoringModel,
    ValueRange,
    Lead,
    Answer,
)
from scoringengine.tools import clone_account

User = get_user_model()

admin.site.site_title = "Scoring engine site admin"
admin.site.site_header = "Scoring engine administration"


class ValidateFieldNameModelAdminForm(forms.ModelForm):
    """Check that field contain only valid field names"""

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
            query_set = query_set.filter(owner=request.user)

        return query_set

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        if request.user.is_superuser:
            list_display += ("owner",)

        return list_display

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=None, change=False, **kwargs)

        # Hide owner field and pre-populate it with current user.
        # This is needed for unique constraints validation.
        form.base_fields["owner"].widget = forms.HiddenInput()
        form.base_fields["owner"].initial = request.user

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
    list_display = ("__str__", "field_name", "type")
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
                answers[
                    q.field_name
                ] = f"put one or multiple responses separated by commas for '{q.field_name}' question here"
            else:
                answers[
                    q.field_name
                ] = f"put response for '{q.field_name}' question here"

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


class RecommendationAdmin(RestrictedAdmin):
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
    min_num = 1


class ScoringModelAdminForm(ValidateFieldNameModelAdminForm):
    field_to_validate = "formula"


class ScoringModelAdmin(RestrictedAdmin):
    form = ScoringModelAdminForm
    inlines = [ValueRangeInline]
    list_display = ("__str__", "weight", "x_axis", "y_axis")
    ordering = ["question__number"]

    field_to_extend_help_text = "formula"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ensure that user can select only available questions he own
        if db_field.name == "question":
            kwargs["queryset"] = Question.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0


class LeadAdmin(RestrictedAdmin):
    inlines = [AnswerInline]
    list_display = ("lead_id", "timestamp")
    ordering = ["owner__id", "-timestamp"]
    readonly_fields = ("timestamp",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


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


admin.site.register(Question, QuestionAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(ScoringModel, ScoringModelAdmin)
admin.site.register(Lead, LeadAdmin)

admin.site.unregister(TokenProxy)
admin.site.register(TokenProxy, TokenAdmin)

admin.site.unregister(User)


class CloneUserForm(forms.Form):
    username = forms.CharField(required=True, label="Username")
    password1 = forms.CharField(
        required=True, label="Password", widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        required=True, label="Password repeat", widget=forms.PasswordInput
    )
    copy_quiz_structure = forms.BooleanField(
        label="Copy quiz structure", required=False
    )
    copy_scoring_model = forms.BooleanField(label="Copy scoring model", required=False)
    copy_leads = forms.BooleanField(label="Copy leads and answers", required=False)

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data["username"]).exists():
            raise forms.ValidationError("User with this username already exists.")

        return self.cleaned_data["username"]

    def clean_password2(self):
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError("Passwords are not the same.")

        return self.cleaned_data["password2"]

    def clean_copy_scoring_model(self):
        if self.cleaned_data["copy_scoring_model"] and not self.cleaned_data.get(
            "copy_quiz_structure", False
        ):
            raise forms.ValidationError(
                "You cannot copy scoring model without quiz structure"
            )

        return self.cleaned_data["copy_scoring_model"]

    def clean_copy_leads(self):
        if self.cleaned_data["copy_leads"] and (
            not self.cleaned_data.get("copy_scoring_model", False)
            or not self.cleaned_data.get("copy_quiz_structure", False)
        ):
            raise forms.ValidationError(
                "You cannot copy leads and answers without scoring model and quiz structure"
            )

        return self.cleaned_data["copy_leads"]

    def clone_user(self, source_user: User):
        user = User.objects.create(
            username=self.cleaned_data["username"], is_staff=True, is_active=True
        )
        user.set_password(self.cleaned_data["password1"])
        user.save()

        user.user_permissions.set(source_user.user_permissions.all())
        user.groups.set(source_user.groups.all())

        clone_account(
            source_user,
            user,
            self.cleaned_data.get("copy_quiz_structure", False),
            self.cleaned_data.get("copy_scoring_model", False),
            self.cleaned_data.get("copy_leads", False),
        )

        return user


@admin.register(User)
class UserOwnAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("actions_column",)
    readonly_fields = UserAdmin.readonly_fields + ("actions_column",)

    def actions_column(self, obj: User):
        return mark_safe(
            '<a href="{}">Clone</a>'.format(
                reverse("admin:auth_user_clone", kwargs={"object_id": obj.pk})
            )
        )

    def clone(self, request, object_id):
        try:
            obj = User.objects.get(pk=object_id)

            if request.method == "POST":
                form = CloneUserForm(data=request.POST)

                if form.is_valid():
                    form.clone_user(obj)
                    messages.add_message(request, messages.SUCCESS, "User cloned.")
                    return redirect(reverse("admin:auth_user_changelist"))

            else:
                form = CloneUserForm()

            opts = self.model._meta
            app_label = opts.app_label

            return render(
                request,
                "admin/auth/user/clone.html",
                {
                    **self.admin_site.each_context(request),
                    "opts": opts,
                    "app_label": app_label,
                    "has_view_permission": self.has_view_permission(request, obj),
                    "original": "Clone account",
                    "form": form,
                },
            )

        except User.DoesNotExist:
            return redirect(reverse("admin:auth_user_changelist"))

    def get_urls(self):
        return [
            path(
                "<int:object_id>/clone/",
                self.clone,
                name="auth_user_clone",
            ),
        ] + super().get_urls()

    actions_column.short_description = "Actions"
