import pytest
from django.contrib.auth.models import AbstractUser
from factory.base import FactoryMetaClass
from predictions.serializers import ExpensePredictionSerializer
from predictions_tests.api.urls import expense_prediction_detail_url
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExpensePredictionApiDetail:
    """Tests for detail view on ExpensePredictionViewSet."""

    @pytest.mark.parametrize('user_type', ['owner', 'member'])
    def test_get_prediction_details(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
        user_type: str,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called by User belonging to Budget.
        THEN: HTTP 200, ExpensePrediction details returned.
        """
        if user_type == 'owner':
            budget = budget_factory(owner=base_user)
        else:
            budget = budget_factory(members=[base_user])
        prediction = expense_prediction_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.get(url)
        serializer = ExpensePredictionSerializer(prediction)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_error_get_prediction_details_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, expense_prediction_factory: FactoryMetaClass
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called without authentication.
        THEN: Unauthorized HTTP 401.
        """
        prediction = expense_prediction_factory()
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_get_details_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        prediction = expense_prediction_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)

        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
