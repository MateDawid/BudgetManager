from typing import Any

import pytest
from django.contrib.auth.models import AbstractUser
from factory.base import FactoryMetaClass
from predictions.models import ExpensePrediction
from predictions_tests.api.urls import expense_prediction_detail_url
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExpensePredictionApiDelete:
    """Tests for delete ExpensePrediction on ExpensePredictionViewSet."""

    def test_delete_prediction(
        self,
        api_client: APIClient,
        base_user: Any,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with DELETE by User belonging to Budget.
        THEN: No content HTTP 204, ExpensePrediction deleted.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        assert ExpensePrediction.objects.filter(period__budget=budget).count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ExpensePrediction.objects.filter(period__budget=budget).exists()

    def test_error_delete_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, expense_prediction_factory: FactoryMetaClass
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with DELETE without authentication.
        THEN: Unauthorized HTTP 401.
        """
        prediction = expense_prediction_factory()
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_delete_prediction_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with DELETE by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        prediction = expense_prediction_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
