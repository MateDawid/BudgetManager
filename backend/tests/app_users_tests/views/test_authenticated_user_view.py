import pytest
from app_users.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

ME_URL = reverse('app_users:me')


class TestAuthenticatedUserView:
    """Tests for AuthenticatedUserView"""

    def test_retrieve_user_unauthorized(self, api_client: APIClient):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: GET request on AuthenticatedUserView.
        THEN: HTTP 401 returned.
        """
        response = api_client.get(ME_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert str(response.data['detail']) == 'Authentication credentials were not provided.'

    @pytest.mark.django_db
    def test_retrieve_profile_success(self, api_client: APIClient, base_user: User):
        """
        GIVEN: Authenticated user as request.user.
        WHEN: GET request on AuthenticatedUserView.
        THEN: HTTP 200 returned.
        """
        api_client.force_authenticate(base_user)
        response = api_client.get(ME_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'name': base_user.name, 'email': base_user.email}

    @pytest.mark.django_db
    def test_post_not_allowed(self, api_client: APIClient, base_user: User):
        """
        GIVEN: Authenticated user as request.user.
        WHEN: POST request on AuthenticatedUserView.
        THEN: HTTP 405 returned.
        """
        api_client.force_authenticate(base_user)
        response = api_client.post(ME_URL, {})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_put_not_allowed(self, api_client: APIClient, base_user: User):
        """
        GIVEN: Authenticated user as request.user.
        WHEN: PUT request on AuthenticatedUserView.
        THEN: HTTP 405 returned.
        """
        api_client.force_authenticate(base_user)
        response = api_client.put(ME_URL, {})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_update_user_profile(self, api_client: APIClient, base_user: User):
        """
        GIVEN: Authenticated user as request.user.
        WHEN: PATCH request on AuthenticatedUserView.
        THEN: HTTP 200 returned, details updated.
        """
        api_client.force_authenticate(base_user)
        payload = {'name': 'Updated name', 'password': 'newpassword123'}

        response = api_client.patch(ME_URL, payload)
        base_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert base_user.name, payload['name']
        assert base_user.check_password(payload['password'])
