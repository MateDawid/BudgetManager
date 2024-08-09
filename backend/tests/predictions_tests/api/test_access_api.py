import pytest
from factory.base import FactoryMetaClass
from predictions.models import ExpensePrediction
from predictions_tests.api.urls import (
    expense_prediction_detail_url,
    expense_prediction_url,
)
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExpensePredictionApiAccess:
    """Tests for access to ExpensePredictionViewSet."""

    def test_auth_required_on_list_view(self, api_client: APIClient, expense_prediction: ExpensePrediction):
        """
        GIVEN: ExpensePrediction model instance in database.
        WHEN: ExpensePredictionViewSet list method called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        response = api_client.get(expense_prediction_url(expense_prediction.period.budget.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_required_on_detail_view(self, api_client: APIClient, expense_prediction: ExpensePrediction):
        """
        GIVEN: ExpensePrediction model instance in database.
        WHEN: ExpensePredictionViewSet detail method called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        response = api_client.get(
            expense_prediction_detail_url(expense_prediction.period.budget.id, expense_prediction.id)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_budget_member_on_list_view(
        self,
        api_client: APIClient,
        user_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction model instance in database.
        WHEN: ExpensePredictionViewSet list method called by User not belonging to given Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        other_user = user_factory()
        expense_prediction = expense_prediction_factory()

        api_client.force_authenticate(other_user)

        response = api_client.get(expense_prediction_url(expense_prediction.period.budget.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    def test_user_not_budget_member_on_detail_view(
        self,
        api_client: APIClient,
        user_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction model instance in database.
        WHEN: ExpensePredictionViewSet detail method called by User not belonging to given Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        other_user = user_factory()
        expense_prediction = expense_prediction_factory()
        api_client.force_authenticate(other_user)

        response = api_client.get(
            expense_prediction_detail_url(expense_prediction.period.budget.id, expense_prediction.id)
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
