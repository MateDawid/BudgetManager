from decimal import Decimal

import pytest
from django.contrib.auth.models import AbstractUser
from factory.base import FactoryMetaClass
from predictions.models import ExpensePrediction
from predictions.serializers import ExpensePredictionSerializer
from predictions_tests.api.urls import expense_prediction_url
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExpensePredictionApiCreate:
    """Tests for create ExpensePrediction on ExpensePredictionViewSet."""

    PAYLOAD = {
        'value': Decimal('100.00'),
        'description': 'Expense prediction.',
    }

    def test_create_single_prediction(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget, BudgetingPeriod and ExpenseCategory instances created in database. Valid payload prepared
        for ExpensePrediction.
        WHEN: ExpensePredictionViewSet called with POST by User belonging to Budget with valid payload.
        THEN: ExpensePrediction object created in database with given payload
        """
        other_user = user_factory()
        budget = budget_factory(owner=base_user, members=[other_user])
        period = budgeting_period_factory(budget=budget)
        category = expense_category_factory(budget=budget)
        payload = self.PAYLOAD.copy()
        payload['period'] = period.id
        payload['category'] = category.id
        api_client.force_authenticate(base_user)

        response = api_client.post(expense_prediction_url(budget.id), payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert ExpensePrediction.objects.filter(period__budget=budget).count() == 1
        prediction = ExpensePrediction.objects.get(id=response.data['id'])
        for key in self.PAYLOAD:
            assert getattr(prediction, key) == self.PAYLOAD[key]
        assert prediction.category == category
        assert prediction.period == period
        serializer = ExpensePredictionSerializer(prediction)
        assert response.data == serializer.data

    def test_error_description_too_long(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget, BudgetingPeriod and ExpenseCategory instances created in database. Payload for ExpensePrediction
        with field value too long.
        WHEN: ExpensePredictionViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. ExpensePrediction not created in database.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        max_length = ExpensePrediction._meta.get_field('description').max_length
        payload = self.PAYLOAD.copy()
        payload['description'] = (max_length + 1) * 'a'

        response = api_client.post(expense_prediction_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'description' in response.data['detail']
        assert (
            response.data['detail']['description'][0] == f'Ensure this field has no more than {max_length} characters.'
        )
        assert not ExpensePrediction.objects.filter(period__budget=budget).exists()

    def test_error_create_prediction_for_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget, BudgetingPeriod and ExpenseCategory instances created in database. Valid payload
        for ExpensePrediction.
        WHEN: ExpensePredictionViewSet called with POST by User not belonging to Budget with valid payload.
        THEN: Forbidden HTTP 403 returned. Object not created.
        """
        budget = budget_factory()
        payload = self.PAYLOAD.copy()
        api_client.force_authenticate(base_user)

        response = api_client.post(expense_prediction_url(budget.id), payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
        assert not ExpensePrediction.objects.filter(period__budget=budget).exists()

    @pytest.mark.parametrize('value', [Decimal('0.00'), Decimal('-0.01')])
    def test_error_value_lower_than_min(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        value: Decimal,
    ):
        """
        GIVEN: Budget, BudgetingPeriod and ExpenseCategory instances created in database. Payload for ExpensePrediction
        with field value too long.
        WHEN: ExpensePredictionViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. ExpensePrediction not created in database.
        """
        budget = budget_factory(owner=base_user)
        period = budgeting_period_factory(budget=budget)
        category = expense_category_factory(budget=budget)
        api_client.force_authenticate(base_user)
        payload = self.PAYLOAD.copy()
        payload['period'] = period.id
        payload['category'] = category.id
        payload['value'] = value

        response = api_client.post(expense_prediction_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'value' in response.data['detail']
        assert response.data['detail']['value'][0] == 'Value should be higher than 0.00.'
        assert not ExpensePrediction.objects.filter(period__budget=budget).exists()
