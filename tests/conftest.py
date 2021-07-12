import uuid

import pytest
from django.contrib.admin import AdminSite
from django.test import RequestFactory
from rest_framework.authtoken.models import TokenProxy

from scoringengine.admin import QuestionAdmin, RecommendationAdmin, LeadAdmin, TokenAdmin
from scoringengine.models import Question, Recommendation, Choice, Lead, Answer, ScoringModel, ValueRange


@pytest.fixture()
def user_with_all_perms(django_user_model):
    """ Monkeypatch User model to "have all permissions" """
    UserModel = django_user_model

    def has_perm(self, *args, **kwargs):
        return True

    UserModel.has_perm = has_perm

    return UserModel


@pytest.fixture()
def user(user_with_all_perms):
    User = user_with_all_perms

    u, _ = User.objects.get_or_create(
        username='test-admin',
        defaults={'is_staff': True}
    )

    return u


@pytest.fixture()
def user1(user_with_all_perms):
    User = user_with_all_perms

    u, _ = User.objects.get_or_create(
        username='test1-admin',
        defaults={'is_staff': True}
    )

    return u


@pytest.fixture()
def question_data(user):
    return {
        'number': 99,
        'type': Question.OPEN,
        'text': 'Test question?',
        'field_name': 'test_question',
        'owner': user
    }


@pytest.fixture()
def question_with_no_recommendation(question_data):
    q = Question(pk=99, **question_data)

    q.save()

    yield q

    q.delete()


@pytest.fixture()
def question(recommendation):
    return recommendation.question


@pytest.fixture()
def questions_for_user(user):
    q1 = Question(
        pk=1,
        type=Question.CHOICES,
        number=1,
        text='Question one - choices - with scoring model - user?',
        field_name='q1u',
        owner=user,
    )
    q2 = Question(
        pk=2,
        type=Question.CHOICES,
        number=2,
        text='Question two - choices - without scoring model - user?',
        field_name='q2u',
        owner=user
    )
    q3 = Question(
        pk=3,
        type=Question.SLIDER,
        number=3,
        text='Question three - slider - with scoring model - user?',
        field_name='q3u',
        min_value=0,
        max_value=10,
        owner=user
    )
    q4 = Question(
        pk=4,
        type=Question.OPEN,
        number=4,
        text='Zip code - open',
        field_name='zc',
        owner=user
    )

    q1.save()
    q2.save()
    q3.save()
    q4.save()

    c1 = Choice(
        pk=1,
        question=q1,
        text='Below 1',
        slug='below-1',
        value=1,
    )
    c2 = Choice(
        pk=2,
        question=q1,
        text='1 - 2',
        slug='1-2',
        value=2,
    )
    c3 = Choice(
        pk=3,
        question=q1,
        text='2+',
        slug='2',
        value=3,
    )
    c4 = Choice(
        pk=4,
        question=q2,
        text='1',
        slug='1',
        value=2,
    )

    c1.save()
    c2.save()
    c3.save()
    c4.save()

    r = Recommendation(
        pk=1,
        question=q2,
        rule='If {q1u} == {q2u}',
        response_text='Rule is True',
        affiliate_name='Example affiliate',
        affiliate_image='https://example.com/image.jpeg',
        affiliate_link='https://example.com/',
        owner=user
    )

    r.save()

    sm = ScoringModel(
        pk=1,
        question=q1,
        weight=1.1,
        x_axis=True,
        y_axis=True,
        formula='{q1u} / {q3u}',
        owner=user
    )
    sm1 = ScoringModel(
        pk=2,
        question=q3,
        weight=1.3,
        x_axis=True,
        y_axis=False,
        owner=user
    )

    sm.save()
    sm1.save()

    vr = ValueRange(
        pk=1,
        scoring_model=sm,
        end=1,
        points=1
    )
    vr1 = ValueRange(
        pk=2,
        scoring_model=sm,
        start=1,
        end=2,
        points=2
    )
    vr2 = ValueRange(
        pk=3,
        scoring_model=sm,
        start=2,
        points=3
    )
    vr3 = ValueRange(
        pk=4,
        scoring_model=sm1,
        points=9
    )

    vr.save()
    vr1.save()
    vr2.save()
    vr3.save()

    yield [q1, q2, q3, q4]

    q1.delete()
    q2.delete()
    q3.delete()
    q4.delete()


@pytest.fixture()
def questions_for_user1(user1):
    q1 = Question(
        pk=10,
        type=Question.CHOICES,
        number=1,
        text='Question one user1?',
        field_name='q1u1',
        # x_axis=False,
        # y_axis=False,
        owner=user1
    )

    q1.save()

    c1 = Choice(
        pk=10,
        question=q1,
        text='Below 1',
        slug='below-1',
        value=1,
        # points=1
    )
    c2 = Choice(
        pk=11,
        question=q1,
        text='2+',
        slug='2',
        value=2,
        # points=2
    )

    c1.save()
    c2.save()

    r = Recommendation(
        pk=10,
        question=q1,
        rule='If {q1u1} == 1',
        owner=user1
    )

    r.save()

    yield [q1]

    q1.delete()


@pytest.fixture()
def questions(questions_for_user, questions_for_user1):
    return questions_for_user + questions_for_user1


@pytest.fixture()
def recommendation_data(user, question_with_no_recommendation):
    return {
        'question': question_with_no_recommendation,
        'rule': 'If {Rent} / {Income} > 0.5',
        'response_text': 'Rule is True',
        'affiliate_name': 'Example affiliate',
        'affiliate_image': 'https://example.com/image.jpeg',
        'affiliate_link': 'https://example.com/',
        'owner': user
    }


@pytest.fixture()
def recommendation(recommendation_data):
    r = Recommendation(**recommendation_data)

    r.save()

    yield r

    r.delete()


@pytest.fixture()
def lead_data(user):
    return {
        'x_axis': 1.1,
        'y_axis': 2.3,
        'owner': user
    }


@pytest.fixture()
def lead(lead_data, questions_for_user):
    l = Lead(**lead_data)

    l.save()

    a1 = Answer(
        lead=l,
        field_name=questions_for_user[0].field_name,
        response=questions_for_user[0].choices.first().text,
        points=0,  # questions_for_user[0].choices.first().points * questions_for_user[0].weight,
        response_text='Response',
        affiliate_name='Example affiliate',
        affiliate_image='https://example.com/image.jpeg',
        affiliate_link='https://example.com/',
        redirect_url='https://example.com/redirect'
    )
    a2 = Answer(
        lead=l,
        field_name=questions_for_user[1].field_name,
        response=questions_for_user[1].choices.first().text,
        points=0  # questions_for_user[1].choices.first().points * questions_for_user[1].weight,
    )

    a1.save()
    a2.save()

    yield l

    l.delete()


@pytest.fixture()
def generate_lead_id():
    def func():
        return str(uuid.uuid4())

    return func


@pytest.fixture()
def leads_for_user(user):
    l = Lead(
        pk=1,
        x_axis=1,
        y_axis=2.3,
        owner=user
    )

    l.save()

    a1 = Answer(
        pk=1,
        lead=l,
        field_name='fn1u',
        response='response user',
    )

    a1.save()

    yield [l]

    l.delete()


@pytest.fixture()
def leads_for_user1(user1):
    l = Lead(
        pk=10,
        x_axis=1,
        y_axis=2.3,
        owner=user1
    )

    l.save()

    a1 = Answer(
        pk=10,
        lead=l,
        field_name='fn1u1',
        response='response user1',
    )

    a1.save()

    yield [l]

    l.delete()


@pytest.fixture()
def leads(leads_for_user, leads_for_user1):
    return leads_for_user + leads_for_user1


@pytest.fixture()
def admin_site():
    return AdminSite()


@pytest.fixture()
def question_admin_and_model(admin_site):
    return QuestionAdmin(model=Question, admin_site=admin_site), Question


@pytest.fixture()
def recommendation_admin_and_model(admin_site):
    return RecommendationAdmin(model=Recommendation, admin_site=admin_site), Recommendation


@pytest.fixture()
def lead_admin_and_model(admin_site):
    return LeadAdmin(model=Lead, admin_site=admin_site), Lead


@pytest.fixture()
def token_admin_and_model(admin_site):
    return TokenAdmin(model=TokenProxy, admin_site=admin_site), TokenProxy


@pytest.fixture()
def fake_request(user, rf: RequestFactory):
    request = rf.request()
    request.user = user

    return request


@pytest.fixture()
def db_field_mock(mocker):
    def get_mock(field_name):
        mock = mocker.Mock()
        type(mock).name = field_name

        return mock

    return get_mock
