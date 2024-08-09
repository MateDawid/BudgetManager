from typing import Any

import pytest
from app_users.serializers.user_serializer import UserSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

LIST_USER_URL = reverse('app_users:list')


class TestListUserView:
    """Tests for ListUserView"""

    @pytest.mark.django_db
    def test_getting_user_list_as_admin(self, api_client: APIClient, superuser: Any, base_user: Any):
        """
        GIVEN: Authenticated admin User as request.user.
        WHEN: GET request on ListUserView.
        THEN: HTTP 200 returned.
        """
        response = api_client.get(LIST_USER_URL)
        api_client.force_authenticate(superuser)

        users = get_user_model().objects.all().order_by('id')
        serializer = UserSerializer(users, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    @pytest.mark.django_db
    def test_getting_user_list_as_base_user(self, api_client: APIClient, base_user: Any):
        """
        GIVEN: Authenticated non-admin User as request.user.
        WHEN: GET request on ListUserView.
        THEN: HTTP 403 returned.
        """
        api_client.force_authenticate(base_user)
        response = api_client.get(LIST_USER_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    def test_getting_user_list_not_authenticated(self, api_client: APIClient):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: GET request on ListUserView.
        THEN: HTTP 401 returned.
        """
        response = api_client.get(LIST_USER_URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert str(response.data['detail']) == 'Authentication credentials were not provided.'
