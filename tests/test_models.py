import re

import pytest
from django.core.exceptions import ValidationError

from scoringengine.models import Choice, Question, Lead, Answer, Rule

pytestmark = pytest.mark.django_db


class TestRule:

    @pytest.mark.parametrize('rule_text', [
        '{Rent} / {Income} > 0.5',
        'If Rent > 99',
        'If {---} > 0 and {Income} < 0',
        'If {---} > 0 && {Income} < 0',
    ])
    def test_rule_raise_validation_error_rule_invalid(self, rule_data, rule_text):
        rule_data['rule'] = rule_text

        rule = Rule(**rule_data)

        with pytest.raises(ValidationError, match='Rule is invalid'):
            rule.full_clean()

    @pytest.mark.parametrize('rule_text,error_message', [
        ('If {Rent} not > 99', 'Rule syntax invalid "If 1 not >>>here>>>> 99"'),
        ('If {Rent} > not 99', 'Rule syntax invalid "If 1 > >>>here>>>not 99"'),
        ('If {Rent} > 99 not', 'Rule syntax invalid "If 1 > 99 no>>>here>>>t"'),
        ('If {Rent} +/ 99', re.escape('Rule syntax invalid "If 1 +>>>here>>>/ 99"')),
        ('If {Rent} + 99.99.9 > 0', re.escape('Rule syntax invalid "If 1 + 99.99>>>here>>>.9 > 0"')),
    ])
    def test_rule_raise_validation_error_rule_syntax_invalid(self, rule_data, rule_text, error_message):
        rule_data['rule'] = rule_text

        rule = Rule(**rule_data)

        with pytest.raises(ValidationError, match=error_message):
            rule.full_clean()

    @pytest.mark.parametrize('rule_text', [
        'If {Rent} / {Income} > 0.5',
        'If {Rent} > 99',
        'If {Rent} > 0 and {Income} < 0',
        'If {A} + {B} - {C} * {D} / {E}',
        'If {A} > {B} < {C} == {D} != {E} >= {F} <= {G}',
        'If {A} and {B} or {C} and not {D} or not {E}',
        'If 0 + 12 + 0.99 + 2.222',
    ])
    def test_rule_is_valid(self, rule_data, rule_text):
        rule_data['rule'] = rule_text

        rule = Rule(**rule_data)
        rule.full_clean()

    def test_str(self, question):
        rule_text = 'If {Test} == {Rule}'

        rule = Rule(question=question, rule='If {Test} == {Rule}')

        assert str(rule) == f'Q{question.number}: {rule_text}'


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

    def test_check_rule_question_with_no_rule(self, question_with_no_rule):
        assert not question_with_no_rule.check_rule({})

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

    def test_get_recommendation_dict_question_with_no_rule(self, question_with_no_rule):
        assert question_with_no_rule.get_recommendation_dict() == {}

    def test_get_recommendation_dict(self, question):
        expected_result = {
            'response_text': f'Q{question.number}. {question.rule.response_text}',
            'affiliate_name': question.rule.affiliate_name,
            'affiliate_image': question.rule.affiliate_image,
            'affiliate_link': question.rule.affiliate_link,
            'redirect_url': question.rule.redirect_url
        }

        assert question.get_recommendation_dict() == expected_result

        question.rule.response_text = ''
        expected_result = {
            'response_text': '',
            'affiliate_name': question.rule.affiliate_name,
            'affiliate_image': question.rule.affiliate_image,
            'affiliate_link': question.rule.affiliate_link,
            'redirect_url': question.rule.redirect_url
        }

        assert question.get_recommendation_dict() == expected_result

    def test_str(self, question_data):
        question = Question(**question_data)

        assert str(question) == f'Q{question_data["number"]}. {question_data["text"]}'


class TestChoice:
    @pytest.mark.parametrize('text', ['Below 99', '100-299', '300+', '1'])
    def test_str(self, question, text):
        choice = Choice(question=question, text=text, points=1)
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
