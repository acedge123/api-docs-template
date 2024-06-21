import pytest
from django import forms
from django.urls import resolve, reverse

from scoringengine.models import Question

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "model_admin",
    [
        "question_admin_and_model",
        "recommendation_admin_and_model",
        "lead_admin_and_model",
        "scoring_model_admin_and_model",
    ],
)
class TestCommonRestrictedAdminMethods:
    @pytest.mark.usefixtures("questions", "leads")
    def test_get_queryset_returns_only_owned_objects_for_non_superuser(
        self, request, user, user1, model_admin, fake_request
    ):
        model_admin, model = request.getfixturevalue(model_admin)

        objects = model_admin.get_queryset(fake_request)

        for obj in model.objects.filter(owner=user):
            assert obj in objects

        for obj in model.objects.filter(owner=user1):
            assert obj not in objects

        fake_request.user = user1
        objects = model_admin.get_queryset(fake_request)

        for obj in model.objects.filter(owner=user):
            assert obj not in objects

        for obj in model.objects.filter(owner=user1):
            assert obj in objects

    @pytest.mark.usefixtures("questions", "leads")
    def test_get_queryset_returns_all_objects_for_superuser(
        self, request, user, user1, model_admin, admin_user, fake_request
    ):
        model_admin, model = request.getfixturevalue(model_admin)

        fake_request.user = admin_user
        objects = model_admin.get_queryset(fake_request)

        for obj in model.objects.filter(owner=user):
            assert obj in objects

        for obj in model.objects.filter(owner=user1):
            assert obj in objects

    def test_list_display_show_owner_field_for_superuser(
        self, request, admin_user, model_admin, fake_request
    ):
        model_admin, _ = request.getfixturevalue(model_admin)

        # Regular user should not see owner
        list_display = model_admin.get_list_display(fake_request)

        assert "owner" not in list_display

        # Super user should see owner
        fake_request.user = admin_user
        list_display = model_admin.get_list_display(fake_request)

        assert "owner" in list_display

    def test_get_form_hide_owner_set_owner_initial_value(
        self, request, model_admin, fake_request
    ):
        model_admin, _ = request.getfixturevalue(model_admin)

        form = model_admin.get_form(fake_request)

        # Check that owner field is hidden
        assert isinstance(form.base_fields["owner"].widget, forms.HiddenInput)
        # Check that owner initial set to current request.user
        assert form.base_fields["owner"].initial == fake_request.user

    @pytest.mark.usefixtures("questions")
    def test_get_form_extend_help_text_of_field_to_extend_help_text(
        self, request, model_admin, fake_request
    ):
        model_admin, _ = request.getfixturevalue(model_admin)

        form = model_admin.get_form(fake_request)

        expected_help_text = (
            "</br></br>Possible field names: <b>q1u, q2u, q3u, zc, q6u</b>"
        )

        if model_admin.field_to_extend_help_text:
            assert form.base_fields[
                model_admin.field_to_extend_help_text
            ].help_text.endswith(expected_help_text)

    def test_get_form_extend_help_text_of_field_to_extend_help_text_no_questions(
        self, request, model_admin, fake_request
    ):
        model_admin, _ = request.getfixturevalue(model_admin)

        form = model_admin.get_form(fake_request)

        expected_help_text = "</br></br>Possible field names: <b>No appropriate questions created yet</b>"

        if model_admin.field_to_extend_help_text:
            assert form.base_fields[
                model_admin.field_to_extend_help_text
            ].help_text.endswith(expected_help_text)

    def test_get_formfield_for_foreignkey_restrict_owner_options(
        self, request, model_admin, db_field_mock, fake_request
    ):
        model_admin, _ = request.getfixturevalue(model_admin)
        owner_db_field_mock = db_field_mock("owner")

        model_admin.formfield_for_foreignkey(owner_db_field_mock, fake_request)
        queryset = owner_db_field_mock.formfield.call_args.kwargs["queryset"]

        assert queryset.get() == fake_request.user


class TestRecommendationAdmin:
    @pytest.mark.usefixtures("questions")
    def test_get_formfield_for_foreignkey_restrict_question_options(
        self, recommendation_admin_and_model, db_field_mock, user, user1, fake_request
    ):
        recommendation_admin, _ = recommendation_admin_and_model
        question_db_field_mock = db_field_mock("question")

        recommendation_admin.formfield_for_foreignkey(
            question_db_field_mock, fake_request
        )
        queryset = question_db_field_mock.formfield.call_args.kwargs["queryset"]

        questions = queryset.all()

        for question in user.questions.all():
            assert question in questions

        for question in user1.questions.all():
            assert question not in questions

    @pytest.mark.parametrize(
        "rule",
        [
            "If {q1u} / {q2u} > 0.5",
            "If {q1u} > 99",
            "If {q3u}",
        ],
    )
    @pytest.mark.usefixtures("questions")
    def test_recommendation_validation_field_names_are_valid(
        self, recommendation_admin_and_model, fake_request, user, rule
    ):
        recommendation_admin, _ = recommendation_admin_and_model
        form_class = recommendation_admin.get_form(fake_request)

        form = form_class(
            {"question": user.questions.first(), "rule": rule, "owner": user}
        )

        assert form.is_valid()
        assert len(form.errors) == 0

    @pytest.mark.parametrize(
        "rule,error_message",
        [
            (
                "If {q1u} > 0 or {not_existing_field_name} > 0",
                ['Field name "not_existing_field_name" used in Rule is not valid.'],
            ),
            ("If {q5u}", ['Field name "q5u" used in Rule is not valid.']),
            (
                "If {not_existing_field_name} or {q5u}",
                [
                    'Field name "not_existing_field_name" used in Rule is not valid.',
                    'Field name "q5u" used in Rule is not valid.',
                ],
            ),
        ],
    )
    @pytest.mark.usefixtures("questions")
    def test_recommendation_validation_field_names_are_not_valid(
        self, recommendation_admin_and_model, fake_request, user, rule, error_message
    ):
        recommendation_admin, _ = recommendation_admin_and_model
        form_class = recommendation_admin.get_form(fake_request)

        form = form_class(
            {"question": user.questions.first(), "rule": rule, "owner": user}
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "__all__" in form.errors
        assert form.errors["__all__"] == error_message

    def test_fields_order(self, recommendation_admin_and_model, fake_request):
        recommendation_admin, _ = recommendation_admin_and_model

        expected_fields_order = [
            "question",
            "rule",
            "owner",
            "response_text",
            "affiliate_name",
            "affiliate_image",
            "affiliate_link",
            "redirect_url",
        ]
        fields = recommendation_admin.get_fields(fake_request)

        assert fields == expected_fields_order


class TestLeadAdmin:
    def test_has_add_permission_false_regular_user(
        self, lead_admin_and_model, fake_request
    ):
        lead_admin, _ = lead_admin_and_model

        assert not lead_admin.has_add_permission(fake_request)

    def test_has_add_permission_false_superuser(
        self, lead_admin_and_model, fake_request, admin_user
    ):
        lead_admin, _ = lead_admin_and_model
        fake_request.user = admin_user

        assert not lead_admin.has_add_permission(fake_request)

    def test_has_change_permission_false_regular_user(
        self, lead_admin_and_model, fake_request
    ):
        lead_admin, _ = lead_admin_and_model

        assert not lead_admin.has_change_permission(fake_request)

    def test_has_change_permission_false_superuser(
        self, lead_admin_and_model, fake_request, admin_user
    ):
        lead_admin, _ = lead_admin_and_model
        fake_request.user = admin_user

        assert not lead_admin.has_change_permission(fake_request)


class TestAnswerInline:
    def test_fields_order(self, answer_inline_and_model, fake_request):
        answer_inline, _ = answer_inline_and_model

        expected_fields_order = [
            "field_name",
            "response",
            "value_number",
            "value",
            "date_value",
            "values",
            "points",
            "lead",
            "response_text",
            "affiliate_name",
            "affiliate_image",
            "affiliate_link",
            "redirect_url",
        ]
        fields = answer_inline.get_fields(fake_request)

        assert fields == expected_fields_order


class TestTokenAdmin:
    def test_get_queryset_returns_only_owned_tokens_for_non_superuser(
        self, user, user1, token_admin_and_model, fake_request
    ):
        token_admin, token_model = token_admin_and_model

        tokens = token_admin.get_queryset(fake_request)

        for token in token_model.objects.filter(user=user):
            assert token in tokens

        for token in token_model.objects.filter(user=user1):
            assert token not in tokens

        fake_request.user = user1
        tokens = token_admin.get_queryset(fake_request)

        for token in token_model.objects.filter(user=user):
            assert token not in tokens

        for token in token_model.objects.filter(user=user1):
            assert token in tokens

    def test_get_queryset_returns_all_tokens_for_superuser(
        self, user, user1, token_admin_and_model, admin_user, fake_request
    ):
        token_admin, token_model = token_admin_and_model

        fake_request.user = admin_user
        tokens = token_admin.get_queryset(fake_request)

        for token in token_model.objects.filter(user=user):
            assert token in tokens

        for token in token_model.objects.filter(user=user1):
            assert token in tokens

    def test_get_formfield_for_foreignkey_restrict_user_options(
        self, token_admin_and_model, db_field_mock, fake_request
    ):
        token_admin, token_model = token_admin_and_model
        user_db_field_mock = db_field_mock("user")

        token_admin.formfield_for_foreignkey(user_db_field_mock, fake_request)
        queryset = user_db_field_mock.formfield.call_args.kwargs["queryset"]

        assert queryset.get() == fake_request.user

    def test_get_formfield_for_foreignkey_not_restrict_user_options_for_superuser(
        self, token_admin_and_model, admin_user, db_field_mock, fake_request
    ):
        token_admin, token_model = token_admin_and_model
        user_db_field_mock = db_field_mock("user")

        fake_request.user = admin_user

        token_admin.formfield_for_foreignkey(user_db_field_mock, fake_request)
        # Queryset is not changed for superuser. No "queryset" in kwargs because of mock
        assert user_db_field_mock.formfield.call_args.kwargs.get("queryset") is None


class TestScoringModelAdmin:
    @pytest.mark.usefixtures("questions")
    def test_get_formfield_for_foreignkey_restrict_question_options(
        self, scoring_model_admin_and_model, db_field_mock, user, user1, fake_request
    ):
        scoring_model_admin, _ = scoring_model_admin_and_model
        question_db_field_mock = db_field_mock("question")

        scoring_model_admin.formfield_for_foreignkey(
            question_db_field_mock, fake_request
        )
        queryset = question_db_field_mock.formfield.call_args.kwargs["queryset"]

        questions = queryset.all()

        for question in user.questions.all():
            assert question in questions

        for question in user1.questions.all():
            assert question not in questions

    @pytest.mark.parametrize(
        "formula",
        [
            "{q1u} / {q2u} * 0.5",
            "{q1u} + 99",
            "{q3u}",
        ],
    )
    @pytest.mark.usefixtures("questions")
    def test_scoring_model_validation_field_names_are_valid(
        self, scoring_model_admin_and_model, fake_request, user, formula
    ):
        scoring_model_admin, _ = scoring_model_admin_and_model
        form_class = scoring_model_admin.get_form(fake_request)

        form = form_class(
            {
                "question": user.questions.filter(scoring_model__isnull=True).first(),
                "weight": 1,
                "formula": formula,
                "owner": user,
            }
        )

        assert form.is_valid()
        assert len(form.errors) == 0

    @pytest.mark.parametrize(
        "formula,error_message",
        [
            (
                "{q1u} * {not_existing_field_name} / 0",
                ['Field name "not_existing_field_name" used in Formula is not valid.'],
            ),
            ("{q5u}", ['Field name "q5u" used in Formula is not valid.']),
            (
                "{not_existing_field_name} + {q5u}",
                [
                    'Field name "not_existing_field_name" used in Formula is not valid.',
                    'Field name "q5u" used in Formula is not valid.',
                ],
            ),
        ],
    )
    @pytest.mark.usefixtures("questions")
    def test_scoring_model_validation_field_names_are_not_valid(
        self, scoring_model_admin_and_model, fake_request, user, formula, error_message
    ):
        scoring_model_admin, _ = scoring_model_admin_and_model
        form_class = scoring_model_admin.get_form(fake_request)

        form = form_class(
            {
                "question": user.questions.filter(scoring_model__isnull=True).first(),
                "weight": 1,
                "formula": formula,
                "owner": user,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "__all__" in form.errors
        assert form.errors["__all__"] == error_message

    @pytest.mark.parametrize(
        "start,end,deleted",
        [
            ("0", "1", None),
            ("1", "1", None),
            ("2", "1", "on"),
        ],
    )
    def test_value_range_start_less_than_or_equal_end_if_not_deleted_valid(
        self, scoring_model_admin_and_model, fake_request, start, end, deleted
    ):
        scoring_model_admin, scoring_model = scoring_model_admin_and_model

        sm = scoring_model(id=111)

        value_range_inline = scoring_model_admin.get_inline_instances(fake_request, sm)[
            0
        ]
        formset_class = value_range_inline.get_formset(fake_request, sm)

        data = {
            "ranges-TOTAL_FORMS": "1",
            "ranges-INITIAL_FORMS": "0",
            "ranges-0-scoring_model": "111",
            "ranges-0-start": start,
            "ranges-0-end": end,
            "ranges-0-points": "1",
            "ranges-0-DELETE": deleted,
        }

        formset = formset_class(data, instance=sm)

        assert formset.is_valid()
        assert len(formset.non_form_errors()) == 0

    def test_value_range_start_less_than_or_equal_end_if_not_deleted_not_valid(
        self, scoring_model_admin_and_model, fake_request
    ):
        scoring_model_admin, scoring_model = scoring_model_admin_and_model

        sm = scoring_model(id=111)

        value_range_inline = scoring_model_admin.get_inline_instances(fake_request, sm)[
            0
        ]
        formset_class = value_range_inline.get_formset(fake_request, sm)

        data = {
            "ranges-TOTAL_FORMS": "1",
            "ranges-INITIAL_FORMS": "0",
            "ranges-0-scoring_model": "111",
            "ranges-0-start": "5",
            "ranges-0-end": "1",
            "ranges-0-points": "1",
        }

        formset = formset_class(data, instance=sm)

        assert not formset.is_valid()
        assert formset.non_form_errors() == [
            "Start of range must be less than or equal to End"
        ]


class TestQuestionAdmin:
    def test_min_max_values_validation_valid(
        self, question_admin_and_model, fake_request, question_data
    ):
        question_admin, _ = question_admin_and_model
        form_class = question_admin.get_form(fake_request)

        question_data["min_value"] = 1
        question_data["max_value"] = 2

        form = form_class(question_data)

        assert form.is_valid()
        assert len(form.errors) == 0

    @pytest.mark.parametrize(
        "min_value,max_value",
        [
            (1, 1),
            (2, 1),
        ],
    )
    def test_min_max_values_validation_not_valid(
        self,
        question_admin_and_model,
        fake_request,
        question_data,
        min_value,
        max_value,
    ):
        question_admin, _ = question_admin_and_model
        form_class = question_admin.get_form(fake_request)

        question_data["min_value"] = min_value
        question_data["max_value"] = max_value

        form = form_class(question_data)

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "__all__" in form.errors
        assert form.errors["__all__"] == ["Min value must be less than Max value."]

    @pytest.mark.parametrize(
        "value,question_type",
        [
            (None, Question.OPEN),
            (None, Question.CHOICES),
            (1, Question.SLIDER),
            (0, Question.SLIDER),
        ],
    )
    def test_min_value_is_not_required(
        self,
        question_admin_and_model,
        fake_request,
        question_data,
        value,
        question_type,
    ):
        question_admin, _ = question_admin_and_model
        form_class = question_admin.get_form(fake_request)

        question_data["type"] = question_type
        question_data["max_value"] = 10
        question_data["min_value"] = value

        form = form_class(question_data)

        assert form.is_valid()
        assert len(form.errors) == 0

    def test_min_value_is_required_for_slider_question_type(
        self, question_admin_and_model, fake_request, question_data
    ):
        question_admin, _ = question_admin_and_model
        form_class = question_admin.get_form(fake_request)

        question_data["type"] = Question.SLIDER
        question_data["min_value"] = None

        form = form_class(question_data)

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "min_value" in form.errors
        assert form.errors["min_value"] == ["This field is required."]

    @pytest.mark.parametrize(
        "value,question_type",
        [
            (None, Question.OPEN),
            (None, Question.CHOICES),
            (1, Question.SLIDER),
            (0, Question.SLIDER),
        ],
    )
    def test_max_value_is_not_required(
        self,
        question_admin_and_model,
        fake_request,
        question_data,
        value,
        question_type,
    ):
        question_admin, _ = question_admin_and_model
        form_class = question_admin.get_form(fake_request)

        question_data["type"] = question_type
        question_data["min_value"] = -1
        question_data["max_value"] = value

        form = form_class(question_data)

        assert form.is_valid()
        assert len(form.errors) == 0

    def test_max_value_is_required_for_slider_question_type(
        self, question_admin_and_model, fake_request, question_data
    ):
        question_admin, _ = question_admin_and_model
        form_class = question_admin.get_form(fake_request)

        question_data["type"] = Question.SLIDER
        question_data["max_value"] = None

        form = form_class(question_data)

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "max_value" in form.errors
        assert form.errors["max_value"] == ["This field is required."]

    @pytest.mark.parametrize("question_type", [Question.OPEN, Question.SLIDER])
    def test_choices_not_required_for_open_and_slider_questions_types(
        self, question_admin_and_model, fake_request, question_type
    ):
        question_admin, question_model = question_admin_and_model

        q = question_model(type=question_type)

        choice_inline = question_admin.get_inline_instances(fake_request, q)[0]
        formset_class = choice_inline.get_formset(fake_request, q)

        data = {
            "choices-TOTAL_FORMS": "1",
            "choices-INITIAL_FORMS": "0",
        }

        formset = formset_class(data, instance=q)

        assert formset.is_valid()
        assert len(formset.non_form_errors()) == 0

    def test_choices_required_for_choices_question_type(
        self, question_admin_and_model, fake_request
    ):
        question_admin, question_model = question_admin_and_model

        q = question_model(id=111, type=Question.CHOICES)

        choice_inline = question_admin.get_inline_instances(fake_request, q)[0]
        formset_class = choice_inline.get_formset(fake_request, q)

        data = {
            "choices-TOTAL_FORMS": "1",
            "choices-INITIAL_FORMS": "0",
        }

        formset = formset_class(data, instance=q)

        assert not formset.is_valid()
        assert formset.non_form_errors() == ["Question must have at least one choice"]

    def test_choices_required_for_choices_question_type_if_all_choices_deleted(
        self, question_admin_and_model, fake_request
    ):
        question_admin, question_model = question_admin_and_model

        q = question_model(id=111, type=Question.CHOICES)

        choice_inline = question_admin.get_inline_instances(fake_request, q)[0]
        formset_class = choice_inline.get_formset(fake_request, q)

        data = {
            "choices-TOTAL_FORMS": "1",
            "choices-INITIAL_FORMS": "0",
            "choices-0-question": "111",
            "choices-0-text": "t",
            "choices-0-slug": "s",
            "choices-0-value": "1",
        }

        formset = formset_class(data, instance=q)

        assert formset.is_valid()
        assert len(formset.non_form_errors()) == 0

        data["choices-0-DELETE"] = "on"

        formset = formset_class(data, instance=q)

        assert not formset.is_valid()
        assert formset.non_form_errors() == ["Question must have at least one choice"]

    def test_request_template_url(self):
        assert (
            reverse("admin:api_request_template")
            == "/admin/scoringengine/question/api_request_template/"
        )
        assert (
            resolve("/admin/scoringengine/question/api_request_template/").view_name
            == "admin:api_request_template"
        )

    def test_request_template_require_login(self, django_client):
        url = reverse("admin:api_request_template")

        django_client.logout()

        response = django_client.get(url)

        assert response.status_code == 302
        assert response.url == f"/admin/login/?next={url}"

    @pytest.mark.usefixtures("questions")
    def test_api_request_template(self, django_client, user):
        url = reverse("admin:api_request_template")

        expected_headers = [
            f"Authorization: Token {user.auth_token}",
            "Content-Type: application/json",
        ]
        expected_payload = {
            "lead_id": "(optional) uuid4 lead identifier, if not used just remove whole line",
            "answers": {
                "q1u": "put response for 'q1u' question here",
                "q2u": "put response for 'q2u' question here",
                "q3u": "put response for 'q3u' question here",
                "zc": "put response for 'zc' question here",
                "q5u": "put one or multiple responses separated by commas for 'q5u' question here",
                "q6u": "put response for 'q6u' question here",
            },
        }

        response = django_client.get(url)

        assert response.status_code == 200
        assert (
            response.template_name
            == "admin/scoringengine/question/api_request_template.html"
        )

        assert "site_title" in response.context_data
        assert "site_header" in response.context_data
        assert "site_url" in response.context_data
        assert "has_permission" in response.context_data
        assert "available_apps" in response.context_data
        assert "is_popup" in response.context_data
        assert "is_nav_sidebar_enabled" in response.context_data
        assert "opts" in response.context_data
        assert "has_view_permission" in response.context_data

        assert response.context_data["title"] == "API request template"
        assert response.context_data["headers"] == expected_headers
        assert response.context_data["payload"] == expected_payload
