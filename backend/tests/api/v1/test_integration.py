"""
Integration tests for API endpoints.
"""

from django.urls import reverse
from rest_framework import status

from scoringengine.models import Lead, Question, ScoringModel


class TestLeadIntegration:
    """Integration tests for lead creation and retrieval."""

    def test_create_lead_with_complete_data(
        self, authenticated_client, complete_test_data
    ):
        """Test creating a lead with all required data."""
        url = reverse("api:v1:leads-list")

        data = {
            "answers": {
                "age": "35",
                "income": "High",
                "satisfaction": "9",
                "start_date": "2024-06-15",
            }
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "lead_id" in response.data
        assert "x_axis" in response.data
        assert "y_axis" in response.data
        assert "total_score" in response.data
        assert "recommendations" in response.data

        # Verify lead was created in database
        lead = Lead.objects.get(lead_id=response.data["lead_id"])
        assert lead.owner == complete_test_data["user"]
        assert lead.total_score > 0

        # Verify answers were created
        assert lead.answers.count() == 4

    def test_create_lead_missing_answers(
        self, authenticated_client, complete_test_data
    ):
        """Test creating a lead with missing answers."""
        url = reverse("api:v1:leads-list")

        data = {
            "answers": {
                "age": "35",
                # Missing other required answers
            }
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "answers" in response.data

    def test_retrieve_lead(self, authenticated_client, lead):
        """Test retrieving a specific lead."""
        url = reverse("api:v1:leads-detail", kwargs={"pk": lead.lead_id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["lead_id"] == str(lead.lead_id)
        assert response.data["total_score"] == float(lead.total_score)

    def test_lead_owner_isolation(self, api_client, user, lead):
        """Test that users can only access their own leads."""
        # Create another user
        other_user = user.__class__.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        # Create token for other user
        from rest_framework.authtoken.models import Token

        token, _ = Token.objects.get_or_create(user=other_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        url = reverse("api:v1:leads-detail", kwargs={"pk": lead.lead_id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestQuestionIntegration:
    """Integration tests for question management."""

    def test_create_question(self, authenticated_client, complete_test_data):
        """Test creating a new question."""
        url = reverse("api:v1:questions-list")

        data = {
            "number": 5,
            "text": "What is your favorite color?",
            "field_name": "favorite_color",
            "type": "O",  # Open question
            "multiple_values": False,
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["text"] == data["text"]
        assert response.data["field_name"] == data["field_name"]

        # Verify question was created in database
        question = Question.objects.get(id=response.data["id"])
        assert question.owner == complete_test_data["user"]

    def test_create_question_with_choices(
        self, authenticated_client, complete_test_data
    ):
        """Test creating a question with choices."""
        url = reverse("api:v1:questions-list")

        data = {
            "number": 6,
            "text": "What is your experience level?",
            "field_name": "experience",
            "type": "CH",  # Choices question
            "multiple_values": False,
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        # Add choices to the question
        question_id = response.data["id"]
        choice_url = reverse("api:v1:choices-list")

        choices_data = [
            {
                "question": question_id,
                "text": "Beginner",
                "slug": "beginner",
                "value": "10.0",
            },
            {
                "question": question_id,
                "text": "Intermediate",
                "slug": "intermediate",
                "value": "20.0",
            },
            {
                "question": question_id,
                "text": "Advanced",
                "slug": "advanced",
                "value": "30.0",
            },
        ]

        for choice_data in choices_data:
            choice_response = authenticated_client.post(
                choice_url, choice_data, format="json"
            )
            assert choice_response.status_code == status.HTTP_201_CREATED

        # Verify choices were created
        question = Question.objects.get(id=question_id)
        assert question.choices.count() == 3

    def test_question_choices_endpoint(self, authenticated_client, choice_question):
        """Test the question choices endpoint."""
        url = reverse("api:v1:questions-choices", kwargs={"pk": choice_question.id})

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert all("text" in choice for choice in response.data)
        assert all("value" in choice for choice in response.data)

    def test_question_scoring_model_endpoint(self, authenticated_client, scoring_model):
        """Test the question scoring model endpoint."""
        url = reverse(
            "api:v1:questions-scoring-model", kwargs={"pk": scoring_model.question.id}
        )

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["weight"] == float(scoring_model.weight)
        assert response.data["x_axis"] == scoring_model.x_axis
        assert response.data["y_axis"] == scoring_model.y_axis

    def test_question_recommendation_endpoint(
        self, authenticated_client, recommendation
    ):
        """Test the question recommendation endpoint."""
        url = reverse(
            "api:v1:questions-recommendation", kwargs={"pk": recommendation.question.id}
        )

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["rule"] == recommendation.rule
        assert response.data["response_text"] == recommendation.response_text


class TestScoringModelIntegration:
    """Integration tests for scoring model management."""

    def test_create_scoring_model(self, authenticated_client, question):
        """Test creating a scoring model."""
        url = reverse("api:v1:scoringmodels-list")

        data = {
            "question": question.id,
            "weight": "1.5",
            "x_axis": True,
            "y_axis": False,
            "formula": "",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["weight"] == 1.5
        assert response.data["x_axis"] is True
        assert response.data["y_axis"] is False

        # Verify scoring model was created
        scoring_model = ScoringModel.objects.get(id=response.data["id"])
        assert scoring_model.question == question
        assert scoring_model.owner == question.owner

    def test_scoring_model_with_value_ranges(self, authenticated_client, scoring_model):
        """Test creating value ranges for a scoring model."""
        url = reverse("api:v1:valueranges-list")

        ranges_data = [
            {
                "scoring_model": scoring_model.id,
                "start": "0",
                "end": "25",
                "points": 10,
            },
            {
                "scoring_model": scoring_model.id,
                "start": "25",
                "end": "50",
                "points": 20,
            },
            {
                "scoring_model": scoring_model.id,
                "start": "50",
                "end": None,
                "points": 30,
            },
        ]

        for range_data in ranges_data:
            response = authenticated_client.post(url, range_data, format="json")
            assert response.status_code == status.HTTP_201_CREATED

        # Verify ranges were created
        assert scoring_model.ranges.count() == 3

        # Test the value ranges endpoint
        ranges_url = reverse(
            "api:v1:scoringmodels-value-ranges", kwargs={"pk": scoring_model.id}
        )
        ranges_response = authenticated_client.get(ranges_url)

        assert ranges_response.status_code == status.HTTP_200_OK
        assert len(ranges_response.data) == 3


class TestAnalyticsIntegration:
    """Integration tests for analytics endpoints."""

    def test_lead_summary_analytics(self, authenticated_client, multiple_leads):
        """Test lead summary analytics endpoint."""
        url = reverse("api:v1:analytics-lead-summary")

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_leads" in response.data
        assert "average_scores" in response.data
        assert "score_distribution" in response.data

        assert response.data["total_leads"] == 5
        assert "x_axis" in response.data["average_scores"]
        assert "y_axis" in response.data["average_scores"]
        assert "total" in response.data["average_scores"]

        # Verify score distribution
        distribution = response.data["score_distribution"]
        assert "low" in distribution
        assert "medium" in distribution
        assert "high" in distribution

    def test_question_analytics(
        self, authenticated_client, multiple_leads, complete_test_data
    ):
        """Test question analytics endpoint."""
        url = reverse("api:v1:analytics-question-analytics")

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4  # 4 questions

        # Check each question has analytics
        for question_data in response.data:
            assert "id" in question_data
            assert "text" in question_data
            assert "answer_distribution" in question_data
            assert "total_answers" in question_data
            assert question_data["total_answers"] == 5  # 5 leads

    def test_recommendation_effectiveness(
        self, authenticated_client, recommendation, multiple_leads
    ):
        """Test recommendation effectiveness analytics."""
        url = reverse("api:v1:analytics-recommendation-effectiveness")

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # 1 recommendation

        rec_data = response.data[0]
        assert "id" in rec_data
        assert "question_text" in rec_data
        assert "rule" in rec_data
        assert "triggered_count" in rec_data


class TestAuthenticationIntegration:
    """Integration tests for authentication and permissions."""

    def test_unauthenticated_access(self, api_client):
        """Test that unauthenticated requests are rejected."""
        urls = [
            reverse("api:v1:leads-list"),
            reverse("api:v1:questions-list"),
            reverse("api:v1:analytics-lead-summary"),
        ]

        for url in urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_token(self, api_client):
        """Test that invalid tokens are rejected."""
        api_client.credentials(HTTP_AUTHORIZATION="Token invalid-token")

        url = reverse("api:v1:leads-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_isolation(self, api_client, complete_test_data):
        """Test that users can only access their own data."""
        # Create another user
        other_user = complete_test_data["user"].__class__.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        # Create a question for the other user
        other_question = Question.objects.create(
            owner=other_user,
            number=1,
            text="Other user's question",
            field_name="other_field",
            type=Question.INTEGER,
        )

        # Try to access it with the first user's token
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Token {complete_test_data["token"].key}'
        )
        url = reverse("api:v1:questions-detail", kwargs={"pk": other_question.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    def test_invalid_data_handling(self, authenticated_client):
        """Test handling of invalid data."""
        url = reverse("api:v1:leads-list")

        # Test with invalid JSON
        response = authenticated_client.post(
            url, "invalid json", content_type="application/json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with missing required fields
        response = authenticated_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_not_found_handling(self, authenticated_client):
        """Test handling of not found resources."""
        # Test non-existent lead
        url = reverse(
            "api:v1:leads-detail", kwargs={"pk": "00000000-0000-0000-0000-000000000000"}
        )
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test non-existent question
        url = reverse("api:v1:questions-detail", kwargs={"pk": 99999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
