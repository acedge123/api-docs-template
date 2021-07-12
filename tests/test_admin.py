import pytest
from django import forms

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('model_admin', ['question_admin_and_model', 'recommendation_admin_and_model',
                                         'lead_admin_and_model'])
class TestCommonRestrictedAdminMethods:

    @pytest.mark.usefixtures('questions', 'leads')
    def test_get_queryset_returns_only_owned_objects_for_non_superuser(self, request, user, user1, model_admin,
                                                                       fake_request):
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

    @pytest.mark.usefixtures('questions', 'leads')
    def test_get_queryset_returns_all_objects_for_superuser(self, request, user, user1, model_admin,
                                                            admin_user, fake_request):
        model_admin, model = request.getfixturevalue(model_admin)

        fake_request.user = admin_user
        objects = model_admin.get_queryset(fake_request)

        for obj in model.objects.filter(owner=user):
            assert obj in objects

        for obj in model.objects.filter(owner=user1):
            assert obj in objects

    def test_list_display_show_owner_field_for_superuser(self, request, admin_user, model_admin, fake_request):
        model_admin, _ = request.getfixturevalue(model_admin)

        # Regular user should not see owner
        list_display = model_admin.get_list_display(fake_request)

        assert 'owner' not in list_display

        # Super user should see owner
        fake_request.user = admin_user
        list_display = model_admin.get_list_display(fake_request)

        assert 'owner' in list_display

    def test_get_form_hide_owner_set_owner_initial_value(self, request, model_admin, fake_request):
        model_admin, _ = request.getfixturevalue(model_admin)

        form = model_admin.get_form(fake_request)

        # Check that owner field is hidden
        assert isinstance(form.base_fields['owner'].widget, forms.HiddenInput)
        # Check that owner initial set to current request.user
        assert form.base_fields['owner'].initial == fake_request.user

    def test_get_formfield_for_foreignkey_restrict_owner_options(self, request, model_admin, db_field_mock,
                                                                 fake_request):
        model_admin, _ = request.getfixturevalue(model_admin)
        owner_db_field_mock = db_field_mock('owner')

        model_admin.formfield_for_foreignkey(owner_db_field_mock, fake_request)
        queryset = owner_db_field_mock.formfield.call_args.kwargs['queryset']

        assert queryset.get() == fake_request.user


class TestRecommendationAdmin:

    @pytest.mark.usefixtures('questions')
    def test_get_formfield_for_foreignkey_restrict_question_options(self, recommendation_admin_and_model, db_field_mock,
                                                                    user, user1, fake_request):
        recommendation_admin, _ = recommendation_admin_and_model
        question_db_field_mock = db_field_mock('question')

        recommendation_admin.formfield_for_foreignkey(question_db_field_mock, fake_request)
        queryset = question_db_field_mock.formfield.call_args.kwargs['queryset']

        questions = queryset.all()

        for question in user.questions.all():
            assert question in questions

        for question in user1.questions.all():
            assert question not in questions

    @pytest.mark.usefixtures('questions')
    def test_get_form_extend_help_text_of_rule_field(self, recommendation_admin_and_model, fake_request):
        recommendation_admin, _ = recommendation_admin_and_model
        form = recommendation_admin.get_form(fake_request)

        expected_help_text = '</br></br>Possible field names: <b>q1u, q2u, q3u</b>'

        assert form.base_fields['rule'].help_text.endswith(expected_help_text)

    def test_get_form_extend_help_text_of_rule_field_no_questions(self, recommendation_admin_and_model, fake_request):
        recommendation_admin, _ = recommendation_admin_and_model

        form = recommendation_admin.get_form(fake_request)

        expected_help_text = '</br></br>Possible field names: <b>No appropriate questions created yet</b>'

        assert form.base_fields['rule'].help_text.endswith(expected_help_text)

    @pytest.mark.parametrize('rule', [
        'If {q1u} / {q2u} > 0.5',
        'If {q1u} > 99',
        'If {q3u}',
    ])
    @pytest.mark.usefixtures('questions')
    def test_recommendation_validation_field_names_are_valid(self, recommendation_admin_and_model, fake_request, user,
                                                             rule):
        recommendation_admin, _ = recommendation_admin_and_model
        form_class = recommendation_admin.get_form(fake_request)

        form = form_class({
            'question': user.questions.first(),
            'rule': rule,
            'owner': user
        })

        assert form.is_valid()
        assert len(form.errors) == 0

    @pytest.mark.parametrize('rule,error_message', [
        (
            'If {q1u} > 0 or {not_existing_field_name} > 0',
            ['Field name "not_existing_field_name" used in Rule is not valid.']
        ),
        (
            'If {zc}',
            ['Field name "zc" used in Rule is not valid.']
        ),
        (
            'If {not_existing_field_name} or {zc}',
            ['Field name "not_existing_field_name" used in Rule is not valid.',
             'Field name "zc" used in Rule is not valid.']
        ),
    ])
    @pytest.mark.usefixtures('questions')
    def test_recommendation_validation_field_names_are_not_valid(self, recommendation_admin_and_model, fake_request,
                                                                 user, rule, error_message):
        recommendation_admin, _ = recommendation_admin_and_model
        form_class = recommendation_admin.get_form(fake_request)

        form = form_class({
            'question': user.questions.first(),
            'rule': rule,
            'owner': user
        })

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert '__all__' in form.errors
        assert form.errors['__all__'] == error_message


class TestLeadAdmin:

    def test_has_add_permission_false_regular_user(self, lead_admin_and_model, fake_request):
        lead_admin, _ = lead_admin_and_model

        assert not lead_admin.has_add_permission(fake_request)

    def test_has_add_permission_false_superuser(self, lead_admin_and_model, fake_request, admin_user):
        lead_admin, _ = lead_admin_and_model
        fake_request.user = admin_user

        assert not lead_admin.has_add_permission(fake_request)

    def test_has_change_permission_false_regular_user(self, lead_admin_and_model, fake_request):
        lead_admin, _ = lead_admin_and_model

        assert not lead_admin.has_change_permission(fake_request)

    def test_has_change_permission_false_superuser(self, lead_admin_and_model, fake_request, admin_user):
        lead_admin, _ = lead_admin_and_model
        fake_request.user = admin_user

        assert not lead_admin.has_change_permission(fake_request)


class TestTokenAdmin:

    def test_get_queryset_returns_only_owned_tokens_for_non_superuser(self, user, user1, token_admin_and_model,
                                                                      fake_request):
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

    def test_get_queryset_returns_all_tokens_for_superuser(self, user, user1, token_admin_and_model,
                                                           admin_user, fake_request):
        token_admin, token_model = token_admin_and_model

        fake_request.user = admin_user
        tokens = token_admin.get_queryset(fake_request)

        for token in token_model.objects.filter(user=user):
            assert token in tokens

        for token in token_model.objects.filter(user=user1):
            assert token in tokens

    def test_get_formfield_for_foreignkey_restrict_user_options(self, token_admin_and_model, db_field_mock,
                                                                fake_request):
        token_admin, token_model = token_admin_and_model
        user_db_field_mock = db_field_mock('user')

        token_admin.formfield_for_foreignkey(user_db_field_mock, fake_request)
        queryset = user_db_field_mock.formfield.call_args.kwargs['queryset']

        assert queryset.get() == fake_request.user

    def test_get_formfield_for_foreignkey_not_restrict_user_options_for_superuser(self, token_admin_and_model,
                                                                                  admin_user, db_field_mock,
                                                                                  fake_request):
        token_admin, token_model = token_admin_and_model
        user_db_field_mock = db_field_mock('user')

        fake_request.user = admin_user

        token_admin.formfield_for_foreignkey(user_db_field_mock, fake_request)
        # Queryset is not changed for superuser. No "queryset" in kwargs because of mock
        assert user_db_field_mock.formfield.call_args.kwargs.get('queryset') is None
