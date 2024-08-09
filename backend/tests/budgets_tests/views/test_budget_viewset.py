"""
Tests for BudgetViewSet:
* TestBudgetViewSetList - GET on list view.
* TestBudgetViewSetOwnedList - GET on owned view.
* TestBudgetViewSetMemberedList - GET on membered view.
* TestBudgetViewSetCreate - POST on list view.
* TestBudgetViewSetDetail - GET on detail view.
* TestBudgetViewSetUpdate - PATCH on detail view.
* TestBudgetViewSetDelete - DELETE on detail view.
"""

from typing import Any

import pytest
from budgets.models.budget_model import Budget
from budgets.serializers.budget_serializer import BudgetSerializer
from categories.budget_defaults import (
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_CATEGORIES,
)
from categories.models import ExpenseCategory, IncomeCategory
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from django.urls import reverse
from factory.base import FactoryMetaClass
from rest_framework import status
from rest_framework.test import APIClient

BUDGETS_URL = reverse('budgets:budget-list')
OWNED_BUDGETS_URL = reverse('budgets:budget-owned')
MEMBERED_BUDGETS_URL = reverse('budgets:budget-membered')


def budget_detail_url(budget_id):
    """Creates and returns Budget detail URL."""
    return reverse('budgets:budget-detail', args=[budget_id])


@pytest.mark.django_db
class TestBudgetViewSetList:
    """Tests for list view on BudgetViewSet."""

    def test_auth_required(self, api_client: APIClient):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: BudgetViewSet list endpoint called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        res = api_client.get(BUDGETS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_budgets_list(
        self, api_client: APIClient, user_factory: FactoryMetaClass, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Authenticated request.user.
        WHEN: BudgetViewSet called.
        THEN: HTTP 200. List of User Budgets returned.
        """
        auth_user = user_factory()
        api_client.force_authenticate(auth_user)
        budget_factory(owner=auth_user, name='Budget 1', description='Some budget', currency='PLN')
        budget_factory(
            owner=user_factory(), name='Budget 2', description='Other budget', currency='eur', members=[auth_user]
        )

        response = api_client.get(BUDGETS_URL)

        budgets = Budget.objects.filter(Q(owner=auth_user) | Q(members=auth_user)).order_by('id').distinct()
        serializer = BudgetSerializer(budgets, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_budgets_list_limited_to_user(
        self, api_client: APIClient, user_factory: FactoryMetaClass, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Two Budgets created for different Users in database.
        WHEN: BudgetViewSet called by authenticated User.
        THEN: HTTP 200. List of User Budgets only returned.
        """
        auth_user = user_factory()
        budget_factory(owner=auth_user)
        budget_factory(owner=user_factory(), members=[auth_user])
        budget_factory()
        api_client.force_authenticate(auth_user)

        response = api_client.get(BUDGETS_URL)

        budgets = Budget.objects.filter(Q(owner=auth_user) | Q(members=auth_user)).order_by('id').distinct()
        serializer = BudgetSerializer(budgets, many=True)
        assert Budget.objects.all().count() == 3
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data
        assert len(response.data['results']) == budgets.count() == 2


@pytest.mark.django_db
class TestBudgetViewSetOwnedList:
    """Tests for owned list view on BudgetViewSet."""

    def test_auth_required(self, api_client: APIClient):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: BudgetViewSet owned endpoint called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        res = api_client.get(OWNED_BUDGETS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_owned_list(
        self, api_client: APIClient, user_factory: FactoryMetaClass, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Three Budgets created in database - two owned by authenticated User.
        WHEN: BudgetViewSet owned endpoint called by authenticated User.
        THEN: HTTP 200. List of Budgets owned by authenticated User returned.
        """
        auth_user = user_factory()
        api_client.force_authenticate(auth_user)
        budget_factory(owner=auth_user)
        budget_factory(owner=auth_user)
        budget_factory(owner=user_factory(), members=[auth_user])

        response = api_client.get(OWNED_BUDGETS_URL)

        owned_budgets = Budget.objects.filter(owner=auth_user).order_by('id').distinct()
        serializer = BudgetSerializer(owned_budgets, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data


@pytest.mark.django_db
class TestBudgetViewSetMemberedList:
    """Tests for membered list view on BudgetViewSet."""

    def test_auth_required(self, api_client: APIClient):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: BudgetViewSet membered endpoint called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        res = api_client.get(MEMBERED_BUDGETS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_membered_list(
        self, api_client: APIClient, user_factory: FactoryMetaClass, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Three Budgets created in database - one owned by authenticated User.
        WHEN: BudgetViewSet membered endpoint called by authenticated User.
        THEN: HTTP 200. List of Budgets membered by authenticated User returned.
        """
        auth_user = user_factory()
        api_client.force_authenticate(auth_user)
        budget_factory(owner=auth_user)
        budget_factory(owner=user_factory(), members=[auth_user])
        budget_factory(owner=user_factory(), members=[auth_user, user_factory()])

        response = api_client.get(MEMBERED_BUDGETS_URL)

        membered_budgets = Budget.objects.filter(members=auth_user).order_by('id').distinct()
        serializer = BudgetSerializer(membered_budgets, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data


@pytest.mark.django_db
class TestBudgetViewSetCreate:
    """Tests for create view on BudgetViewSet."""

    def test_auth_required(self, api_client: APIClient, base_user: AbstractUser):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: BudgetViewSet list endpoint called with POST without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        response = api_client.post(BUDGETS_URL, data={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_budget(self, api_client: APIClient, base_user: AbstractUser, user_factory: FactoryMetaClass):
        """
        GIVEN: Authenticated User as request.user. Valid payload.
        WHEN: BudgetViewSet list endpoint called with POST.
        THEN: HTTP 201 returned. Budget created in database.
        """
        api_client.force_authenticate(base_user)
        payload = {
            'name': 'Budget 1',
            'description': 'Some budget',
            'currency': 'PLN',
            'members': [user_factory().id, user_factory().id],
        }

        response = api_client.post(BUDGETS_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Budget.objects.filter(owner=base_user).count() == 1
        budget = Budget.objects.get(id=response.data['id'])
        for key in payload:
            if key == 'members':
                members = getattr(budget, key)
                assert members.count() == len(payload[key])
                for member_id in payload[key]:
                    assert members.filter(id=member_id).exists()
            else:
                assert getattr(budget, key) == payload[key]
        serializer = BudgetSerializer(budget)
        assert response.data == serializer.data
        default_expense_categories = ExpenseCategory.objects.filter(budget=budget)
        for expense_category in DEFAULT_EXPENSE_CATEGORIES:
            assert default_expense_categories.filter(**expense_category).exists()
        default_income_categories = IncomeCategory.objects.filter(budget=budget)
        for income_category in DEFAULT_INCOME_CATEGORIES:
            assert default_income_categories.filter(**income_category).exists()

    def test_error_name_too_long(self, api_client: APIClient, base_user: AbstractUser, user_factory: AbstractUser):
        """
        GIVEN: Authenticated User as request.user. Too long name in payload.
        WHEN: BudgetViewSet list endpoint called with POST.
        THEN: HTTP 400 returned. Budget not created in database.
        """
        api_client.force_authenticate(base_user)
        max_length = Budget._meta.get_field('name').max_length
        payload = {
            'name': (max_length + 1) * 'a',
            'description': 'Some budget',
            'currency': 'PLN',
            'members': [user_factory().id, user_factory().id],
        }

        response = api_client.post(BUDGETS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data['detail']
        assert response.data['detail']['name'][0] == f'Ensure this field has no more than {max_length} characters.'
        assert not Budget.objects.filter(owner=base_user).exists()

    def test_error_name_already_used(self, api_client: APIClient, base_user: AbstractUser):
        """
        GIVEN: Authenticated User as request.user. Name of Budget already owned by User in payload.
        WHEN: BudgetViewSet list endpoint called with POST.
        THEN: HTTP 400 returned. Budget not created in database.
        """
        api_client.force_authenticate(base_user)
        payload = {'name': 'Budget', 'description': 'Some budget', 'currency': 'eur'}
        Budget.objects.create(owner=base_user, **payload)

        response = api_client.post(BUDGETS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data['detail']
        assert response.data['detail']['name'][0] == f'User already owns Budget with name "{payload["name"]}".'
        assert Budget.objects.filter(owner=base_user).count() == 1


@pytest.mark.django_db
class TestBudgetViewSetDetail:
    """Tests for detail view on BudgetViewSet."""

    def test_auth_required(self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass):
        """
        GIVEN: AnonymousUser as request.user.
        WHEN: BudgetViewSet detail endpoint called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        budget = budget_factory(owner=base_user)
        url = budget_detail_url(budget.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_budget_details(self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass):
        """
        GIVEN: Budget owned by authenticated User created in database.
        WHEN: BudgetViewSet detail endpoint called by authenticated User.
        THEN: HTTP 200. List of Budgets membered by authenticated User returned.
        """
        api_client.force_authenticate(base_user)
        budget = budget_factory(owner=base_user)
        url = budget_detail_url(budget.id)

        response = api_client.get(url)
        serializer = BudgetSerializer(budget)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_error_get_other_user_budget_details(
        self, api_client: APIClient, user_factory: FactoryMetaClass, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget owned by some User created in database.
        WHEN: BudgetViewSet detail endpoint for another Users Budget called by authenticated User.
        THEN: HTTP 404 returned.
        """
        user_1 = user_factory()
        user_2 = user_factory()
        budget = budget_factory(owner=user_1)
        api_client.force_authenticate(user_2)

        url = budget_detail_url(budget.id)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBudgetViewSetUpdate:
    """Tests for update view on BudgetViewSet."""

    def test_put_not_allowed(self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass):
        """
        GIVEN: Budget owner as a request.user.
        WHEN: BudgetViewSet detail endpoint called with PUT.
        THEN: Method not allowed. HTTP 405 returned.
        """
        api_client.force_authenticate(base_user)
        budget = budget_factory(owner=base_user)
        url = budget_detail_url(budget.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_auth_required(self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass):
        """
        GIVEN: AnonymousUser as request.user. Budget created in database.
        WHEN: BudgetViewSet detail endpoint called with PATCH without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        budget = budget_factory(owner=base_user)
        url = budget_detail_url(budget.id)

        response = api_client.patch(url, data={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        'param, value',
        [('name', 'New name'), ('description', 'New description'), ('currency', 'PLN')],
    )
    def test_budget_update_single_field(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: Budget owner as request.user. Valid update param in payload.
        WHEN: BudgetViewSet detail endpoint called with PATCH.
        THEN: HTTP 200 returned. Budget updated in database.
        """
        api_client.force_authenticate(base_user)
        payload = {'name': 'Budget', 'description': 'Some budget', 'currency': 'eur'}
        budget = budget_factory(owner=base_user, **payload)
        update_payload = {param: value}
        url = budget_detail_url(budget.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        budget.refresh_from_db()
        assert getattr(budget, param) == value

    def test_update_with_members(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget owner as request.user. New members list as update param in payload.
        WHEN: BudgetViewSet detail endpoint called with PATCH.
        THEN: HTTP 200 returned. Budget updated in database.
        """
        user_1 = user_factory()
        user_2 = user_factory()
        api_client.force_authenticate(base_user)
        payload = {'name': 'Budget', 'description': 'Some budget', 'currency': 'eur', 'members': [user_1.id]}
        budget = budget_factory(owner=base_user, **payload)
        update_payload = {'members': [user_1.id, user_2.id]}
        url = budget_detail_url(budget.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        budget.refresh_from_db()
        assert list(budget.members.all().values_list('id', flat=True)) == update_payload['members']

    def test_budget_update_many_fields(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget owner as request.user. Valid update params in payload.
        WHEN: BudgetViewSet detail endpoint called with PATCH.
        THEN: HTTP 200 returned. Budget updated in database.
        """
        user_1 = user_factory()
        user_2 = user_factory()
        api_client.force_authenticate(base_user)
        payload = {'name': 'Budget', 'description': 'Some budget', 'currency': 'eur', 'members': [user_1.id]}
        budget = budget_factory(owner=base_user, **payload)
        update_payload = {'name': 'UPDATE', 'description': 'Updated budget', 'currency': 'pln', 'members': [user_2.id]}
        url = budget_detail_url(budget.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        budget.refresh_from_db()
        for param, value in update_payload.items():
            if param == 'members':
                assert list(budget.members.all().values_list('id', flat=True)) == update_payload['members']
            else:
                assert getattr(budget, param) == value

    @pytest.mark.parametrize(
        'param, value',
        [
            ('name', (Budget._meta.get_field('name').max_length + 1) * 'A'),
            ('name', 'Old budget'),
            ('currency', (Budget._meta.get_field('currency').max_length + 1) * 'A'),
        ],
    )
    def test_error_on_budget_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: Budget owner as request.user. Invalid value as update param in payload.
        WHEN: BudgetViewSet detail endpoint called with PATCH.
        THEN: HTTP 400 returned. Budget not updated in database.
        """
        user_factory()
        api_client.force_authenticate(base_user)
        old_payload = {'name': 'Old budget', 'description': 'Some budget', 'currency': 'eur'}
        budget_factory(owner=base_user, **old_payload)
        new_payload = {'name': 'New budget', 'description': 'Some budget', 'currency': 'eur'}
        budget = budget_factory(owner=base_user, **new_payload)
        old_value = getattr(budget, param)
        payload = {param: value}
        url = budget_detail_url(budget.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        budget.refresh_from_db()
        assert getattr(budget, param) == old_value

    def test_owner_unchangeable(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget owner as request.user. Owner as update param in payload.
        WHEN: BudgetViewSet detail endpoint called with PATCH.
        THEN: HTTP 200 returned. Budget owner not updated in database.
        """
        other_user = user_factory()
        api_client.force_authenticate(base_user)
        budget = budget_factory(owner=base_user)

        payload = {'owner': other_user.id}
        url = budget_detail_url(budget.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        budget.refresh_from_db()
        assert budget.owner == base_user


@pytest.mark.django_db
class TestBudgetViewSetDelete:
    """Tests for delete view on BudgetViewSet."""

    def test_auth_required(self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass):
        """
        GIVEN: AnonymousUser as request.user. Budget created in database.
        WHEN: BudgetViewSet detail endpoint called with DELETE without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        budget = budget_factory(owner=base_user)
        url = budget_detail_url(budget.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_budget(self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass):
        """
        GIVEN: Budget owner as request.user. Budget created in database.
        WHEN: BudgetViewSet detail endpoint called with DELETE.
        THEN: HTTP 204 returned. Budget deleted from database.
        """
        api_client.force_authenticate(base_user)
        budget = budget_factory(owner=base_user)
        url = budget_detail_url(budget.id)

        assert Budget.objects.all().count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Budget.objects.all().exists()
