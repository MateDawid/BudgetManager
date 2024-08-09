from typing import Any

import pytest
from app_users_tests.factories import UserFactory
from budgets_tests.factories import BudgetFactory, BudgetingPeriodFactory
from categories_tests.factories import ExpenseCategoryFactory, IncomeCategoryFactory
from django.contrib.auth import get_user_model
from entities_tests.factories import DepositFactory, EntityFactory
from predictions_tests.factories import ExpensePredictionFactory
from pytest_django.lazy_django import skip_if_no_django
from pytest_factoryboy import register
from rest_framework.test import APIClient

register(UserFactory)
register(BudgetFactory)
register(BudgetingPeriodFactory)
register(DepositFactory)
register(EntityFactory)
register(IncomeCategoryFactory)
register(ExpenseCategoryFactory)
register(ExpensePredictionFactory)


@pytest.fixture
def api_client() -> APIClient:
    """API Client for creating request."""
    skip_if_no_django()
    return APIClient()


@pytest.fixture
def base_user() -> Any:
    """User with base permissions."""
    return get_user_model().objects.create_user('user@example.com', 'user123!@#')


@pytest.fixture
def superuser() -> Any:
    """User with admin permissions."""
    return get_user_model().objects.create_superuser('admin@example.com', 'admin123!@#')
