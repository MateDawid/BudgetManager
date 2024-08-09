import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

TOKEN_URL: str = reverse('app_users:token')


@pytest.mark.django_db
class TestCreateTokenView:
    """Tests for CreateTokenView"""

    payload: dict = {
        'email': 'test@example.com',
        'password': 'test-user-password123',
    }

    def test_create_token_successful(self, api_client: APIClient):
        """
        GIVEN: User payload for AuthToken creation.
        WHEN: CreateTokenView.post() called with given data.
        THEN: AuthToken created for User.
        """
        get_user_model().objects.create_user(**self.payload, name='TEST_USER')

        response = api_client.post(TOKEN_URL, self.payload)

        assert 'token' in response.data
        assert response.status_code == status.HTTP_200_OK

    def test_create_token_bad_credentials(self, api_client: APIClient):
        """
        GIVEN: User invalid payload for AuthToken creation.
        WHEN: CreateTokenView.post() called with given data.
        THEN: HTTP 400 returned, AuthToken not created.
        """
        response = api_client.post(TOKEN_URL, self.payload)

        assert 'token' not in response.data
        assert (
            response.data['detail']['non_field_errors'][0] == 'Unable to authenticate user with provided credentials.'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
