"""
Test fixtures for comprehensive testing.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from scoringengine.models import (
    Answer,
    Choice,
    DatesRange,
    Lead,
    Question,
    Recommendation,
    ScoringModel,
    ValueRange,
)

User = get_user_model()


@pytest.fixture
def api_client():
    """API client for testing."""
    return APIClient()


@pytest.fixture
def user():
    """Create a test user."""
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    return user


@pytest.fixture
def user_with_token(user):
    """Create a test user with API token."""
    token, _ = Token.objects.get_or_create(user=user)
    return user, token


@pytest.fixture
def authenticated_client(api_client, user_with_token):
    """Create an authenticated API client."""
    user, token = user_with_token
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def question(user):
    """Create a test question."""
    return Question.objects.create(
        owner=user,
        number=1,
        text="What is your age?",
        field_name="age",
        type=Question.INTEGER,
        multiple_values=False,
    )


@pytest.fixture
def choice_question(user):
    """Create a test choice question."""
    question = Question.objects.create(
        owner=user,
        number=2,
        text="What is your income level?",
        field_name="income",
        type=Question.CHOICES,
        multiple_values=False,
    )

    Choice.objects.create(
        question=question, text="Low", slug="low", value=Decimal("10.0")
    )
    Choice.objects.create(
        question=question, text="Medium", slug="medium", value=Decimal("20.0")
    )
    Choice.objects.create(
        question=question, text="High", slug="high", value=Decimal("30.0")
    )

    return question


@pytest.fixture
def slider_question(user):
    """Create a test slider question."""
    return Question.objects.create(
        owner=user,
        number=3,
        text="Rate your satisfaction (1-10)",
        field_name="satisfaction",
        type=Question.SLIDER,
        min_value=1,
        max_value=10,
        multiple_values=False,
    )


@pytest.fixture
def date_question(user):
    """Create a test date question."""
    return Question.objects.create(
        owner=user,
        number=4,
        text="When did you start?",
        field_name="start_date",
        type=Question.DATE,
        multiple_values=False,
    )


@pytest.fixture
def scoring_model(question):
    """Create a test scoring model."""
    return ScoringModel.objects.create(
        question=question,
        owner=question.owner,
        weight=Decimal("1.0"),
        x_axis=True,
        y_axis=False,
        formula="",
    )


@pytest.fixture
def scoring_model_with_ranges(scoring_model):
    """Create a test scoring model with value ranges."""
    ValueRange.objects.create(
        scoring_model=scoring_model, start=Decimal("0"), end=Decimal("25"), points=10
    )
    ValueRange.objects.create(
        scoring_model=scoring_model, start=Decimal("25"), end=Decimal("50"), points=20
    )
    ValueRange.objects.create(
        scoring_model=scoring_model, start=Decimal("50"), end=None, points=30
    )
    return scoring_model


@pytest.fixture
def scoring_model_with_date_ranges(date_question):
    """Create a test scoring model with date ranges."""
    scoring_model = ScoringModel.objects.create(
        question=date_question,
        owner=date_question.owner,
        weight=Decimal("1.0"),
        x_axis=False,
        y_axis=True,
        formula="",
    )

    DatesRange.objects.create(
        scoring_model=scoring_model,
        start=date.today() - timedelta(days=365),
        end=date.today() - timedelta(days=180),
        points=10,
    )
    DatesRange.objects.create(
        scoring_model=scoring_model,
        start=date.today() - timedelta(days=180),
        end=date.today(),
        points=20,
    )
    DatesRange.objects.create(
        scoring_model=scoring_model, start=date.today(), end=None, points=30
    )
    return scoring_model


@pytest.fixture
def recommendation(question):
    """Create a test recommendation."""
    return Recommendation.objects.create(
        question=question,
        owner=question.owner,
        rule="If {age} >= 25",
        response_text="You are eligible for premium features!",
        affiliate_name="Premium Partner",
        affiliate_link="https://example.com/premium",
    )


@pytest.fixture
def lead(user, question, choice_question, slider_question, date_question):
    """Create a test lead with answers."""
    lead = Lead.objects.create(
        owner=user,
        x_axis=Decimal("25.0"),
        y_axis=Decimal("15.0"),
        total_score=Decimal("40.0"),
    )

    # Create answers for all questions
    Answer.objects.create(
        lead=lead, field_name="age", response="30", value=Decimal("30.0")
    )

    Answer.objects.create(
        lead=lead, field_name="income", response="Medium", value=Decimal("20.0")
    )

    Answer.objects.create(
        lead=lead, field_name="satisfaction", response="8", value=Decimal("8.0")
    )

    Answer.objects.create(
        lead=lead,
        field_name="start_date",
        response="2024-01-15",
        date_value=date(2024, 1, 15),
    )

    return lead


@pytest.fixture
def multiple_leads(user, question, choice_question, slider_question, date_question):
    """Create multiple test leads for analytics testing."""
    leads = []

    for i in range(5):
        lead = Lead.objects.create(
            owner=user,
            x_axis=Decimal(f"{20 + i * 5}"),
            y_axis=Decimal(f"{10 + i * 3}"),
            total_score=Decimal(f"{30 + i * 8}"),
        )

        # Create answers for each lead
        Answer.objects.create(
            lead=lead,
            field_name="age",
            response=str(25 + i * 5),
            value=Decimal(f"{25 + i * 5}"),
        )

        Answer.objects.create(
            lead=lead,
            field_name="income",
            response=["Low", "Medium", "High"][i % 3],
            value=Decimal(f"{10 + i * 10}"),
        )

        Answer.objects.create(
            lead=lead,
            field_name="satisfaction",
            response=str(5 + i),
            value=Decimal(f"{5 + i}"),
        )

        Answer.objects.create(
            lead=lead,
            field_name="start_date",
            response=f"2024-{i+1:02d}-15",
            date_value=date(2024, i + 1, 15),
        )

        leads.append(lead)

    return leads


@pytest.fixture
def complete_test_data(
    user_with_token,
    question,
    choice_question,
    slider_question,
    date_question,
    scoring_model_with_ranges,
    scoring_model_with_date_ranges,
    recommendation,
    multiple_leads,
):
    """Create complete test data for integration testing."""
    return {
        "user": user_with_token[0],
        "token": user_with_token[1],
        "questions": [question, choice_question, slider_question, date_question],
        "scoring_models": [scoring_model_with_ranges, scoring_model_with_date_ranges],
        "recommendation": recommendation,
        "leads": multiple_leads,
    }
