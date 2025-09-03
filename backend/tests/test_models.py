import re

import pytest
from django.core.exceptions import ValidationError

from scoringengine.models import (
    Answer,
    Choice,
    Lead,
    Question,
    Recommendation,
    ScoringModel,
    ValueRange,
)

pytestmark = pytest.mark.django_db


class TestRecommendation:
    @pytest.mark.parametrize(
        "rule",
        [
            "{Rent} / {Income} > 0.5",
            "If Rent > 99",
            "If {---} > 0 and {Income} < 0",
            "If {---} > 0 && {Income} < 0",
        ],
    )
    def test_recommendation_raise_validation_error_rule_invalid(
        self, recommendation_data, rule
    ):
        recommendation_data["rule"] = rule

        recommendation = Recommendation(**recommendation_data)

        with pytest.raises(ValidationError, match="Rule is invalid"):
            recommendation.full_clean()

    @pytest.mark.parametrize(
        "rule,error_message",
        [
            (
                "If {Rent} not > 99",
                'Rule syntax invalid "If {Rent} not >>>here>>>> 99"',
            ),
            (
                "If {Rent} > not {Income}",
                'Rule syntax invalid "If {Rent} > >>>here>>>not {Income}"',
            ),
            (
                "If {Rent} > 99 not",
                'Rule syntax invalid "If {Rent} > 99 no>>>here>>>t"',
            ),
            (
                "If {Rent} +/ {Income}",
                re.escape('Rule syntax invalid "If {Rent} +>>>here>>>/ {Income}"'),
            ),
            (
                "If {Rent} + 99 -",
                re.escape('Rule syntax invalid "If {Rent} + 99 >>>here>>>-"'),
            ),
            (
                "If {Rent} + 99.99.9 > 0",
                re.escape('Rule syntax invalid "If {Rent} + 99.99>>>here>>>.9 > 0"'),
            ),
        ],
    )
    def test_recommendation_raise_validation_error_rule_syntax_invalid(
        self, recommendation_data, rule, error_message
    ):
        recommendation_data["rule"] = rule

        recommendation = Recommendation(**recommendation_data)

        with pytest.raises(ValidationError, match=error_message):
            recommendation.full_clean()

    @pytest.mark.parametrize(
        "rule",
        [
            "If {Rent} / {Income} > 0.5",
            "If {Rent} > 99",
            "If {Rent} > 0 and {Income} < 0",
            "If {A} + {B} - {C} * {D} / {E}",
            "If {A} > {B} < {C} == {D} != {E} >= {F} <= {G}",
            "If {A} and {B} or {C} and not {D} or not {E}",
            "If 0 + 12 + 0.99 + 2.222",
            "If 0 + 12 + (0.99 + 2.222)",
        ],
    )
    def test_rule_is_valid(self, recommendation_data, rule):
        recommendation_data["rule"] = rule

        recommendation = Recommendation(**recommendation_data)
        recommendation.full_clean()

    def test_str(self, question):
        rule = "If {Test} == {Rule}"

        recommendation = Recommendation(question=question, rule="If {Test} == {Rule}")

        assert str(recommendation) == f"Q{question.number}: {rule}"


class TestQuestion:
    @pytest.mark.parametrize(
        "field_name", ["Invalid Field Name", "Invalid Field_name", "---"]
    )
    def test_field_name_is_valid_rule_variable_raise_validation_error(
        self, question_data, field_name
    ):
        question_data["field_name"] = field_name

        question = Question(**question_data)

        with pytest.raises(
            ValidationError, match=f'"{field_name}" is not valid Field name'
        ):
            question.full_clean()

    @pytest.mark.parametrize(
        "field_name",
        ["Field_name", "field_name", "FieldName", "000", "Field4", "field_4"],
    )
    def test_field_name_is_valid_rule_variable(self, question_data, field_name):
        question_data["field_name"] = field_name

        question = Question(**question_data)

        question.full_clean()

    @pytest.mark.parametrize(
        "rule,data,expected_result",
        [
            ("If {field_name0} == 99", {"field_name0": 99}, True),
            (
                "If {field_name0} < {field_name1}",
                {"field_name0": 99, "field_name1": 299},
                True,
            ),
            (
                "If {field_name0} > 0 and not {field_name1} > 0",
                {"field_name0": 99, "field_name1": 299},
                False,
            ),
            ("If 0 > 1", {}, False),
            ("If 1 / 0", {}, False),
        ],
    )
    def test_eval_rule(self, rule, data, expected_result):
        assert Question.eval_rule(rule, data) == expected_result

    def test_eval_rule_raise_syntax_error(self):
        rule = "If 1 = 1"
        data = {}

        with pytest.raises(SyntaxError):
            Question.eval_rule(rule, data)

    def test_check_rule_question_with_no_recommendation(
        self, question_with_no_recommendation
    ):
        assert not question_with_no_recommendation.check_rule({})

    def test_check_rule_is_true(self, question):
        answers = {"Income": 3999.00, "Rent": 4999.00}

        assert question.check_rule(answers)

    def test_check_rule_is_false(self, question):
        answers = {"Income": 10000.01, "Rent": 999.99}

        assert not question.check_rule(answers)

    def test_get_recommendation_dict_question_with_no_recommendation(
        self, question_with_no_recommendation
    ):
        assert question_with_no_recommendation.get_recommendation_dict() == {}

    def test_get_recommendation_dict(self, question):
        expected_result = {
            "response_text": question.recommendation.response_text,
            "affiliate_name": question.recommendation.affiliate_name,
            "affiliate_image": question.recommendation.affiliate_image,
            "affiliate_link": question.recommendation.affiliate_link,
            "redirect_url": question.recommendation.redirect_url,
        }

        assert question.get_recommendation_dict() == expected_result

        question.recommendation.response_text = ""
        expected_result = {
            "response_text": "",
            "affiliate_name": question.recommendation.affiliate_name,
            "affiliate_image": question.recommendation.affiliate_image,
            "affiliate_link": question.recommendation.affiliate_link,
            "redirect_url": question.recommendation.redirect_url,
        }

        assert question.get_recommendation_dict() == expected_result

    def test_str(self, question_data):
        question = Question(**question_data)

        assert str(question) == f'Q{question_data["number"]}. {question_data["text"]}'

    @pytest.mark.usefixtures("questions")
    def test_get_possible_field_names_exclude_field_name_of_questions_that_can_not_be_used_in_rules_and_scoring_model_formula(
        self, user
    ):
        expected_result = Question.get_possible_field_names(user)

        assert expected_result == ["q1u", "q2u", "q3u", "zc", "q6u"]

    def test_types(self):
        assert Question.OPEN == "O"
        assert Question.CHOICES == "CH"
        assert Question.MULTIPLE_CHOICES == "MC"
        assert Question.SLIDER == "S"

    def test_calculate_points_question_with_no_scoring_model(
        self, question_with_no_recommendation
    ):
        assert question_with_no_recommendation.calculate_points({}) is None


class TestChoice:
    @pytest.mark.parametrize("text", ["Below 99", "100-299", "300+", "1"])
    def test_str(self, question, text):
        choice = Choice(question=question, text=text)
        assert str(choice) == text


class TestLead:
    def test_str(self):
        lead_id = "f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288"

        lead = Lead(lead_id=lead_id)

        assert str(lead) == str(lead_id)


class TestAnswer:
    def test_str(self):
        field_name = "test_field"
        response = "Above 999"

        answer = Answer(field_name="test_field", response=response)

        assert str(answer) == f"{field_name}: {response}"


class TestScoringModel:
    @pytest.mark.parametrize(
        "formula,expected_result",
        [
            ("{test_question} / 10", "Q99: {test_question} / 10"),
            ("", "Q99: {test_question}"),
        ],
    )
    def test_str(self, scoring_model_data, formula, expected_result):
        scoring_model_data["formula"] = formula
        scoring_model = ScoringModel(**scoring_model_data)

        assert str(scoring_model) == expected_result

    @pytest.mark.parametrize(
        "formula",
        [
            "{Rent} > 0.5",
            "Rent / 10 * 100",
            "{---} * 2",
        ],
    )
    def test_scoring_model_raise_validation_error_formula_invalid(
        self, scoring_model_data, formula
    ):
        scoring_model_data["formula"] = formula

        scoring_model = ScoringModel(**scoring_model_data)

        with pytest.raises(ValidationError, match="Formula is invalid"):
            scoring_model.full_clean()

    @pytest.mark.parametrize(
        "formula,error_message",
        [
            (
                "{Rent} +/ 99",
                re.escape('Formula syntax invalid "{Rent} +>>>here>>>/ 99"'),
            ),
            (
                "{Rent} + 99.99.9",
                re.escape('Formula syntax invalid "{Rent} + 99.99>>>here>>>.9"'),
            ),
        ],
    )
    def test_scoring_model_raise_validation_error_formula_syntax_invalid(
        self, scoring_model_data, formula, error_message
    ):
        scoring_model_data["formula"] = formula

        scoring_model = ScoringModel(**scoring_model_data)

        with pytest.raises(ValidationError, match=error_message):
            scoring_model.full_clean()

    @pytest.mark.parametrize(
        "formula",
        [
            "{Rent} / {Income} * 0.5",
            "{Rent} - 99",
            "{Rent} + (0.99 + 2.222)",
        ],
    )
    def test_formula_is_valid(self, scoring_model_data, formula):
        scoring_model_data["formula"] = formula

        scoring_model = ScoringModel(**scoring_model_data)
        scoring_model.full_clean()

    @pytest.mark.parametrize(
        "formula,data,expected_result",
        [
            ("{fn0} / {fn1} * 100", {"fn0": 9, "fn1": 8}, 112.5),
            ("{fn0}", {"fn0": 99}, 99),
            ("{fn0} / {fn1} * 100", {"fn0": 99, "fn1": 0}, None),
            ("{fn0} + {fn1} * 2", {"fn0": 2, "fn1": 2}, 6),
            ("({fn0} + {fn1}) * 2", {"fn0": 2, "fn1": 2}, 8),
        ],
    )
    def test_eval_formula(self, formula, data, expected_result):
        assert ScoringModel.eval_formula(formula, data) == expected_result

    def test_eval_formula_raise_syntax_error(self):
        formula = "{fn} / 2)"
        data = {"fn": 1}

        with pytest.raises(SyntaxError):
            ScoringModel.eval_formula(formula, data)

    @pytest.mark.parametrize(
        "formula,answers,expected_result",
        [
            ("", {"test_question": -1}, 0),
            ("", {"test_question": 0}, 1.1),
            ("", {"test_question": 2.1}, 1.1),
            ("", {"test_question": 3}, 2.2),
            ("", {"test_question": 10}, 3.3),
            ("1 / 0", {"test_question": 0}, None),
            ("{test_question} / 2", {"test_question": 4}, 1.1),
        ],
    )
    def test_calculate_points(self, formula, answers, expected_result, scoring_model):
        scoring_model.formula = formula
        scoring_model.weight = 1.1

        assert scoring_model.calculate_points(answers) == expected_result


class TestValueRange:
    @pytest.mark.parametrize(
        "start,end,expected_result",
        [
            (None, None, "[-inf, +inf)"),
            (1.1, None, "[1.1, +inf)"),
            (None, -3, "[-inf, -3)"),
            (1, 10, "[1, 10)"),
        ],
    )
    def test_str(self, scoring_model, start, end, expected_result):
        value_range = ValueRange(scoring_model=scoring_model, start=start, end=end)

        assert str(value_range) == expected_result
