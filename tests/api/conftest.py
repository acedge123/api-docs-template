import pytest
from rest_framework.test import APIClient


@pytest.fixture()
def api_client_for_user():
    def get_api_client(user):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {user.auth_token}')

        return client

    return get_api_client


@pytest.fixture()
def api_client(user, api_client_for_user):
    return api_client_for_user(user)
