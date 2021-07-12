import re

import pytest
from django.core.exceptions import ValidationError

from scoringengine.models import Choice, Question, Lead, Answer, Recommendation

pytestmark = pytest.mark.django_db


class TestRecommendation:

    @pytest.mark.parametrize('rule', [
        '{Rent} / {Income} > 0.5',
        'If Rent > 99',
        'If {---} > 0 and {Income} < 0',
        'If {---} > 0 && {Income} < 0',
    ])
    def test_rule_raise_validation_error_rule_invalid(self, recommendation_data, rule):
        recommendation_data['rule'] = rule

        recommendation = Recommendation(**recommendation_data)

        with pytest.raises(ValidationError, match='Rule is invalid'):
            recommendation.full_clean()

    @pytest.mark.parametrize('rule,error_message', [
        ('If {Rent} not > 99', 'Rule syntax invalid "If 1 not >>>here>>>> 99"'),
        ('If {Rent} > not 99', 'Rule syntax invalid "If 1 > >>>here>>>not 99"'),
        ('If {Rent} > 99 not', 'Rule syntax invalid "If 1 > 99 no>>>here>>>t"'),
        ('If {Rent} +/ 99', re.escape('Rule syntax invalid "If 1 +>>>here>>>/ 99"')),
        ('If {Rent} + 99.99.9 > 0', re.escape('Rule syntax invalid "If 1 + 99.99>>>here>>>.9 > 0"')),
    ])
    def test_rule_raise_validation_error_rule_syntax_invalid(self, recommendation_data, rule, error_message):
        recommendation_data['rule'] = rule

        recommendation = Recommendation(**recommendation_data)

        with pytest.raises(ValidationError, match=error_message):
            recommendation.full_clean()

    @pytest.mark.parametrize('rule', [
        'If {Rent} / {Income} > 0.5',
        'If {Rent} > 99',
        'If {Rent} > 0 and {Income} < 0',
        'If {A} + {B} - {C} * {D} / {E}',
        'If {A} > {B} < {C} == {D} != {E} >= {F} <= {G}',
        'If {A} and {B} or {C} and not {D} or not {E}',
        'If 0 + 12 + 0.99 + 2.222',
        'If 0 + 12 + (0.99 + 2.222)',
    ])
    def test_rule_is_valid(self, recommendation_data, rule):
        recommendation_data['rule'] = rule

        recommendation = Recommendation(**recommendation_data)
        recommendation.full_clean()

    def test_str(self, question):
        rule = 'If {Test} == {Rule}'

        recommendation = Recommendation(question=question, rule='If {Test} == {Rule}')

        assert str(recommendation) == f'Q{question.number}: {rule}'


class TestQuestion:
    @pytest.mark.parametrize('field_name', ['Invalid Field Name', 'Invalid Field_name', '---'])
    def test_field_name_is_valid_rule_variable_raise_validation_error(self, question_data, field_name):
        question_data['field_name'] = field_name

        question = Question(**question_data)

        with pytest.raises(ValidationError, match=f'"{field_name}" is not valid Field name'):
            question.full_clean()

    @pytest.mark.parametrize('field_name', ['Field_name', 'field_name', 'FieldName', '000', 'Field4', 'field_4'])
    def test_field_name_is_valid_rule_variable(self, question_data, field_name):
        question_data['field_name'] = field_name

        question = Question(**question_data)

        question.full_clean()

    @pytest.mark.parametrize('rule,data,expected_result', [
        ('If {field_name0} == 99', {'field_name0': 99}, True),
        ('If {field_name0} < {field_name1}', {'field_name0': 99, 'field_name1': 299}, True),
        ('If {field_name0} > 0 and not {field_name1} > 0', {'field_name0': 99, 'field_name1': 299}, False),
        ('If 0 > 1', {}, False),
    ])
    def test_eval_rule(self, rule, data, expected_result):
        assert Question.eval_rule(rule, data) == expected_result

    def test_eval_rule_raise_syntax_error(self):
        rule = 'If 1 = 1'
        data = {}

        with pytest.raises(SyntaxError):
            Question.eval_rule(rule, data)

    def test_check_rule_question_with_no_rule(self, question_with_no_recommendation):
        assert not question_with_no_recommendation.check_rule({})

    def test_check_rule_is_true(self, question):
        answers = {
            'Income': 3999.00,
            'Rent': 4999.00
        }

        assert question.check_rule(answers)

    def test_check_rule_is_false(self, question):
        answers = {
            'Income': 10000.01,
            'Rent': 999.99
        }

        assert not question.check_rule(answers)

    def test_get_recommendation_dict_question_with_no_rule(self, question_with_no_recommendation):
        assert question_with_no_recommendation.get_recommendation_dict() == {}

    def test_get_recommendation_dict(self, question):
        expected_result = {
            'response_text': f'Q{question.number}. {question.recommendation.response_text}',
            'affiliate_name': question.recommendation.affiliate_name,
            'affiliate_image': question.recommendation.affiliate_image,
            'affiliate_link': question.recommendation.affiliate_link,
            'redirect_url': question.recommendation.redirect_url
        }

        assert question.get_recommendation_dict() == expected_result

        question.recommendation.response_text = ''
        expected_result = {
            'response_text': '',
            'affiliate_name': question.recommendation.affiliate_name,
            'affiliate_image': question.recommendation.affiliate_image,
            'affiliate_link': question.recommendation.affiliate_link,
            'redirect_url': question.recommendation.redirect_url
        }

        assert question.get_recommendation_dict() == expected_result

    def test_str(self, question_data):
        question = Question(**question_data)

        assert str(question) == f'Q{question_data["number"]}. {question_data["text"]}'

    @pytest.mark.usefixtures('questions')
    def test_get_possible_field_names_exclude_field_name_of_questions_without_choices(self, user):
        expected_result = Question.get_possible_field_names(user)

        # Check that user has question without choices
        assert any([True for q in user.questions.all() if not q.choices.exists()])
        # Check that that question field name is absent in possible field names
        assert expected_result == ['q1u', 'q2u', 'q3u']


class TestChoice:
    @pytest.mark.parametrize('text', ['Below 99', '100-299', '300+', '1'])
    def test_str(self, question, text):
        choice = Choice(question=question, text=text)
        assert str(choice) == text


class TestLead:
    def test_str(self):
        lead_id = 'f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288'

        lead = Lead(lead_id=lead_id)

        assert str(lead) == str(lead_id)


class TestAnswer:
    def test_str(self):
        field_name = 'test_field'
        response = 'Above 999'

        answer = Answer(field_name='test_field', response=response)

        assert str(answer) == f'{field_name}: {response}'
