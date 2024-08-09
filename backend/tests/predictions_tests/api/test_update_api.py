from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth.models import AbstractUser
from factory.base import FactoryMetaClass
from predictions_tests.api.urls import expense_prediction_detail_url
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExpensePredictionApiPartialUpdate:
    """Tests for partial update view on ExpensePredictionViewSet."""

    PAYLOAD = {
        'value': Decimal('100.00'),
        'description': 'Expense prediction.',
    }

    @pytest.mark.parametrize(
        'param, value',
        [
            ('value', Decimal('200.00')),
            ('description', 'New description'),
        ],
    )
    @pytest.mark.django_db
    def test_prediction_partial_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with PATCH by User belonging to Budget.
        THEN: HTTP 200, ExpensePrediction updated.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget, **self.PAYLOAD)
        update_payload = {param: value}
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        prediction.refresh_from_db()
        assert getattr(prediction, param) == update_payload[param]

    def test_prediction_partial_update_period(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database. Update payload with "period" value prepared.
        WHEN: ExpensePredictionSet detail view called with PATCH by User belonging to Budget with valid payload.
        THEN: HTTP 200, Deposit updated with "period" value.
        """
        budget = budget_factory(owner=base_user)
        period = budgeting_period_factory(budget=budget)
        prediction = expense_prediction_factory(budget=budget, **self.PAYLOAD)
        update_payload = {'period': period.id}
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        prediction.refresh_from_db()
        assert prediction.period == period

    def test_prediction_partial_update_category(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database. Update payload with "category" value prepared.
        WHEN: ExpensePredictionSet detail view called with PATCH by User belonging to Budget with valid payload.
        THEN: HTTP 200, Deposit updated with "category" value.
        """
        budget = budget_factory(owner=base_user)
        category = expense_category_factory(budget=budget)
        prediction = expense_prediction_factory(budget=budget, **self.PAYLOAD)
        update_payload = {'category': category.id}
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        prediction.refresh_from_db()
        assert prediction.category == category

    def test_error_partial_update_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, expense_prediction_factory: FactoryMetaClass
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with PATCH without authentication.
        THEN: Unauthorized HTTP 401.
        """
        prediction = expense_prediction_factory()
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.patch(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_partial_update_prediction_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with PATCH by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        prediction = expense_prediction_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.patch(url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    def test_error_partial_update_period_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as
        'period' in payload.
        WHEN: ExpensePredictionViewSet called with PATCH by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. ExpensePrediction not updated.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget)
        payload = {'period': budgeting_period_factory().id}
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0] == 'Budget for period and category fields is not the same.'
        )

    def test_error_partial_update_category_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as
        'category' in payload.
        WHEN: ExpensePredictionViewSet called with PATCH by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. ExpensePrediction not updated.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget)
        payload = {'category': expense_category_factory().id}
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0] == 'Budget for period and category fields is not the same.'
        )


@pytest.mark.django_db
class TestExpensePredictionApiFullUpdate:
    """Tests for full update view on ExpensePredictionViewSet."""

    INITIAL_PAYLOAD = {
        'value': Decimal('100.00'),
        'description': 'Expense prediction.',
    }

    UPDATE_PAYLOAD = {
        'value': Decimal('200.00'),
        'description': 'Updated prediction.',
    }

    @pytest.mark.django_db
    def test_prediction_full_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with PUT by User belonging to Budget.
        THEN: HTTP 200, ExpensePrediction updated.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget, **self.INITIAL_PAYLOAD)
        update_payload = self.UPDATE_PAYLOAD.copy()
        update_period = budgeting_period_factory(budget=budget)
        update_payload['period'] = update_period.id
        update_category = expense_category_factory(budget=budget)
        update_payload['category'] = update_category.id
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.put(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        prediction.refresh_from_db()
        for param in update_payload:
            if param == 'period':
                assert getattr(prediction, param) == update_period
                continue
            elif param == 'category':
                assert getattr(prediction, param) == update_category
                continue
            assert getattr(prediction, param) == update_payload[param]

    def test_error_full_update_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, expense_prediction_factory: FactoryMetaClass
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with PUT without authentication.
        THEN: Unauthorized HTTP 401.
        """
        prediction = expense_prediction_factory()
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_full_update_prediction_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: ExpensePrediction instance for Budget created in database.
        WHEN: ExpensePredictionViewSet detail view called with PUT by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        prediction = expense_prediction_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(prediction.period.budget.id, prediction.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    def test_error_full_update_period_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as 'period' in payload.
        WHEN: ExpensePredictionViewSet called with PUT by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. ExpensePrediction not updated.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget, **self.INITIAL_PAYLOAD)
        update_payload = self.UPDATE_PAYLOAD.copy()
        # Outer BudgetingPeriod in payload
        update_payload['period'] = budgeting_period_factory().id
        update_payload['category'] = expense_category_factory(budget=budget).id
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.put(url, update_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0] == 'Budget for period and category fields is not the same.'
        )

    def test_error_full_update_category_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as 'category' in payload.
        WHEN: ExpensePredictionViewSet called with PUT by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. ExpensePrediction not updated.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget, **self.INITIAL_PAYLOAD)
        update_payload = self.UPDATE_PAYLOAD.copy()
        # Outer ExpenseCategory in payload
        update_payload['category'] = expense_category_factory().id
        update_payload['period'] = budgeting_period_factory(budget=budget).id
        api_client.force_authenticate(base_user)
        url = expense_prediction_detail_url(budget.id, prediction.id)

        response = api_client.put(url, update_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0] == 'Budget for period and category fields is not the same.'
        )
