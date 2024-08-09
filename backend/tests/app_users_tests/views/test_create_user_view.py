import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('app_users:create')


@pytest.mark.django_db
class TestCreateUserView:
    """Tests for CreateUserView"""

    payload = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test Name',
    }

    def test_create_user_successful(self, api_client: APIClient):
        """
        GIVEN: Payload for User creation.
        WHEN: POST request on CreateUserView.
        THEN: HTTP 201 returned, User created.
        """
        response = api_client.post(CREATE_USER_URL, self.payload)

        assert response.status_code == status.HTTP_201_CREATED
        user = get_user_model().objects.get(email=self.payload['email'])
        assert user.check_password(self.payload['password'])
        assert 'password' not in response.data

    def test_user_with_email_exists_error(self, api_client: APIClient):
        """
        GIVEN: Payload for User creation with duplicated email.
        WHEN: POST request on CreateUserView.
        THEN: HTTP 400 returned.
        """
        get_user_model().objects.create_user(**self.payload)
        response = api_client.post(CREATE_USER_URL, self.payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['detail']['email'][0]) == 'user with this email already exists.'

    def test_password_too_short_error(self, api_client: APIClient):
        """
        GIVEN: Payload for User creation with password too short.
        WHEN: POST request on CreateUserView.
        THEN: HTTP 400 returned.
        """
        payload = self.payload.copy()
        payload['password'] = 'new'
        response = api_client.post(CREATE_USER_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['detail']['password'][0]) == 'Ensure this field has at least 5 characters.'
        assert not get_user_model().objects.filter(email=payload['email']).exists()
