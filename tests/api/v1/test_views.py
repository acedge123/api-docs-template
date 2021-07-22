import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestLeadViewSet:

    @pytest.mark.usefixtures('questions')
    def test_get_lead(self, api_client, lead):
        url = reverse('api:v1:lead-detail', kwargs={'pk': str(lead.lead_id)})

        expected_result = {
            'lead_id': str(lead.lead_id),
            'x_axis': '1.10',
            'y_axis': '2.30',
            'recommendations': {
                'q1u': {
                    'response_text': 'Response',
                    'affiliate_name': 'Example affiliate',
                    'affiliate_image': 'https://example.com/image.jpeg',
                    'affiliate_link': 'https://example.com/',
                    'redirect_url': 'https://example.com/redirect'
                }
            }
        }

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_get_lead_wrong_owner_404(self, api_client_for_user, lead, user1):
        url = reverse('api:v1:lead-detail', kwargs={'pk': str(lead.lead_id)})

        api_client = api_client_for_user(user1)

        expected_result = {'detail': 'Not found.'}

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_create_lead_bad_request_not_all_answers_provided(self, api_client):
        url = reverse('api:v1:lead-list')
        data = {
            'answers': {
                'q1u': '2+'
            }
        }

        expected_result = {
            'answers': ['Not all answers provided']
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_create_lead_bad_request_not_existing_question(self, api_client):
        url = reverse('api:v1:lead-list')
        data = {
            'answers': {
                'q1u': '2',
                'q2u': '1',
                'q3u': '1',
                'zc': 'ZC29076',
                'non_existing_field_id': '2'
            }
        }

        expected_result = {
            'answers': {
                'field_name': ["There are no question with 'non_existing_field_id' field name"]
            }
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_create_lead_bad_request_for_choice_question_non_existing_question_choice(self, api_client):
        url = reverse('api:v1:lead-list')
        data = {
            'answers': {
                'q1u': '2',
                'q2u': 'wrong-choice',
                'q3u': '1',
                'zc': 'ZC29076'
            }
        }

        expected_result = {
            'answers': {
                'response': ["There are no choice with 'wrong-choice' response in question with 'q2u' field name"]
            }
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_create_lead_bad_request_response_for_slider_question_invalid(self, api_client):
        url = reverse('api:v1:lead-list')
        data = {
            'answers': {
                'q1u': '2',
                'q2u': '1',
                'q3u': 'invalid-value',
                'zc': 'ZC29076'
            }
        }

        expected_result = {
            'answers': {
                'response': ["Response 'invalid-value' is invalid response for question with 'q3u' field name"]
            }
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    @pytest.mark.parametrize('value', ['-100', '100'])
    def test_create_lead_bad_request_response_for_slider_question_value_not_in_allowed_range(self, api_client, value):
        url = reverse('api:v1:lead-list')
        data = {
            'answers': {
                'q1u': '2',
                'q2u': '1',
                'q3u': value,
                'zc': 'ZC29076'
            }
        }

        expected_result = {
            'answers': {
                'response': ["Response for question with 'q3u' field name should be within [0, 10] range"]
            }
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_create_lead_pass_lead_id(self, api_client):
        url = reverse('api:v1:lead-list')

        data = {
            'lead_id': 'f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288',
            'answers': {
                'q1u': '1-2',
                'q2u': '1',
                'q3u': '5',
                'zc': 'ZC29076'
            }
        }

        expected_result = {
            'lead_id': 'f6aaf29c-deb9-42db-b8d0-b2dcc1bb3288',
            'x_axis': '12.80',
            'y_axis': '1.10',
            'recommendations': {
                'q2u': {
                    'response_text': 'Rule is True',
                    'affiliate_name': 'Example affiliate',
                    'affiliate_image': 'https://example.com/image.jpeg',
                    'affiliate_link': 'https://example.com/',
                    'redirect_url': ''
                }
            }
        }

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == expected_result

    @pytest.mark.usefixtures('questions')
    def test_create_lead_not_pass_lead_id(self, api_client):
        url = reverse('api:v1:lead-list')

        # Do not pass lead_id
        data = {
            'answers': {
                'q1u': 'below-1',
                'q2u': '1',
                'q3u': '5',
                'zc': 'ZC29076'
            }
        }

        response = api_client.post(url, data=data, format='json')

        result = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert result['lead_id']
        assert result['x_axis'] == '12.80'
        assert result['y_axis'] == '1.10'

    @pytest.mark.usefixtures('questions')
    def test_create_lead_check_owner(self, generate_lead_id, api_client_for_user, user, user1):
        url = reverse('api:v1:lead-list')

        lead_id = generate_lead_id()
        data = {
            'lead_id': lead_id,
            'answers': {
                'q1u': '2',
                'q2u': '1',
                'q3u': '5',
                'zc': 'ZC29076'
            }
        }

        # Create lead for user
        api_client = api_client_for_user(user)

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert user.leads.filter(lead_id=lead_id).exists()
        assert not user1.leads.filter(lead_id=lead_id).exists()

        lead_id = generate_lead_id()
        data = {
            'lead_id': lead_id,
            'answers': {
                'q1u1': 'below-1'
            }
        }

        # Create lead for user1
        api_client = api_client_for_user(user1)

        response = api_client.post(url, data=data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert not user.leads.filter(lead_id=lead_id).exists()
        assert user1.leads.filter(lead_id=lead_id).exists()
