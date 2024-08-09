from typing import Any

import pytest
from budgets.models.budget_model import Budget
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from entities.models.deposit_model import Deposit
from entities.serializers.deposit_serializer import DepositSerializer
from factory.base import FactoryMetaClass
from rest_framework import status
from rest_framework.test import APIClient


def deposits_url(budget_id):
    """Create and return an Deposit detail URL."""
    return reverse('budgets:deposit-list', args=[budget_id])


def deposit_detail_url(budget_id, deposit_id):
    """Create and return an Deposit detail URL."""
    return reverse('budgets:deposit-detail', args=[budget_id, deposit_id])


@pytest.mark.django_db
class TestDepositApiAccess:
    """Tests for access to DepositViewSet."""

    def test_auth_required(self, api_client: APIClient, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: DepositViewSet called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        res = api_client.get(deposits_url(budget.id))

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_budget_member(
        self, api_client: APIClient, user_factory: FactoryMetaClass, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget model instance in database.
        WHEN: DepositViewSet called by User not belonging to given Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        budget_owner = user_factory()
        other_user = user_factory()
        budget = budget_factory(owner=budget_owner)
        api_client.force_authenticate(other_user)

        response = api_client.get(deposits_url(budget.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'


@pytest.mark.django_db
class TestDepositApiList:
    """Tests for list view on DepositViewSet."""

    def test_retrieve_deposit_list(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two Deposit model instances for single Budget created in database.
        WHEN: DepositViewSet called by Budget owner.
        THEN: Response with serialized Budget Deposit list returned.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        for _ in range(2):
            deposit_factory(budget=budget)

        response = api_client.get(deposits_url(budget.id))

        deposits = Deposit.objects.filter(budget=budget)
        serializer = DepositSerializer(deposits, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_deposits_list_limited_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two Deposit model instances for different Budgets created in database.
        WHEN: DepositViewSet called by one of Budgets owner.
        THEN: Response with serialized Deposit list (only from given Budget) returned.
        """
        budget = budget_factory(owner=base_user)
        deposit = deposit_factory(budget=budget)
        deposit_factory()
        api_client.force_authenticate(base_user)

        response = api_client.get(deposits_url(budget.id))

        deposits = Deposit.objects.filter(budget=budget)
        serializer = DepositSerializer(deposits, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(serializer.data) == deposits.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == deposit.id

    def test_deposits_in_deposits_list(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: One Deposit and one Deposit models instances for the same Budget created in database.
        WHEN: DepositViewSet called by one of Budgets owner.
        THEN: Response with serialized Deposit list (only from given Budget) returned including Deposit.
        """
        budget = budget_factory(owner=base_user)
        deposit_factory(budget=budget)
        deposit = deposit_factory(budget=budget)
        api_client.force_authenticate(base_user)

        response = api_client.get(deposits_url(budget.id))

        deposits = Deposit.objects.filter(budget=budget)
        serializer = DepositSerializer(deposits, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(serializer.data) == deposits.count() == 2
        assert response.data['results'] == serializer.data
        assert deposit.id in [deposit['id'] for deposit in response.data['results']]


@pytest.mark.django_db
class TestDepositApiCreate:
    """Tests for create Deposit on DepositViewSet."""

    PAYLOAD = {
        'name': 'Supermarket',
        'description': 'Supermarket in which I buy food.',
        'is_active': True,
    }

    def test_create_single_deposit(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget instance created in database. Valid payload prepared for Deposit.
        WHEN: DepositViewSet called with POST by User belonging to Budget with valid payload.
        THEN: Deposit object created in database with given payload
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)

        response = api_client.post(deposits_url(budget.id), self.PAYLOAD)

        assert response.status_code == status.HTTP_201_CREATED
        assert Deposit.objects.filter(budget=budget).count() == 1
        deposit = Deposit.objects.get(id=response.data['id'])
        assert deposit.budget == budget
        for key in self.PAYLOAD:
            assert getattr(deposit, key) == self.PAYLOAD[key]
        assert deposit.is_deposit is True
        serializer = DepositSerializer(deposit)
        assert response.data == serializer.data

    @pytest.mark.parametrize('field_name', ['name', 'description'])
    def test_error_value_too_long(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass, field_name: str
    ):
        """
        GIVEN: Budget instance created in database. Payload for Deposit with field value too long.
        WHEN: DepositViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. Deposit not created in database.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        max_length = Deposit._meta.get_field(field_name).max_length
        payload = self.PAYLOAD.copy()
        payload[field_name] = (max_length + 1) * 'a'

        response = api_client.post(deposits_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert field_name in response.data['detail']
        assert response.data['detail'][field_name][0] == f'Ensure this field has no more than {max_length} characters.'
        assert not Deposit.objects.filter(budget=budget).exists()

    def test_error_name_already_used(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget instance created in database. Valid payload for Deposit.
        WHEN: DepositViewSet called twice with POST by User belonging to Budget with the same payload.
        THEN: Bad request HTTP 400 returned. Only one Deposit created in database.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload = self.PAYLOAD.copy()

        api_client.post(deposits_url(budget.id), payload)
        response = api_client.post(deposits_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data['detail']
        assert response.data['detail']['name'][0] == 'Entity with given name already exists in Budget.'
        assert Deposit.objects.filter(budget=budget).count() == 1

    def test_error_create_deposit_for_not_accessible_budget(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget instance created in database. Valid payload for Deposit.
        WHEN: DepositViewSet called with POST by User not belonging to Budget with valid payload.
        THEN: Forbidden HTTP 403 returned. Object not created.
        """
        budget = budget_factory()
        api_client.force_authenticate(base_user)

        response = api_client.post(deposits_url(budget.id), self.PAYLOAD)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
        assert not Deposit.objects.filter(budget=budget).exists()


@pytest.mark.django_db
class TestDepositApiDetail:
    """Tests for detail view on DepositViewSet."""

    def test_get_deposit_details(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called by User belonging to Budget.
        THEN: HTTP 200, Deposit details returned.
        """
        budget = budget_factory(owner=base_user)
        deposit = deposit_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(budget.id, deposit.id)

        response = api_client.get(url)
        serializer = DepositSerializer(deposit)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_error_get_deposit_details_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, deposit_factory: FactoryMetaClass
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called without authentication.
        THEN: Unauthorized HTTP 401.
        """
        deposit = deposit_factory()
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_get_details_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        deposit = deposit_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)

        url = deposit_detail_url(deposit.budget.id, deposit.id)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'


@pytest.mark.django_db
class TestDepositApiPartialUpdate:
    """Tests for partial update view on DepositViewSet."""

    PAYLOAD = {
        'name': 'Supermarket',
        'description': 'Supermarket in which I buy food.',
        'is_active': True,
        'is_deposit': False,
    }

    @pytest.mark.parametrize(
        'param, value',
        [
            ('name', 'New name'),
            ('description', 'New description'),
            ('is_active', not PAYLOAD['is_active']),
            ('is_deposit', not PAYLOAD['is_deposit']),
        ],
    )
    @pytest.mark.django_db
    def test_deposit_partial_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PATCH by User belonging to Budget.
        THEN: HTTP 200, Deposit updated.
        """
        budget = budget_factory(owner=base_user)
        deposit = deposit_factory(budget=budget, **self.PAYLOAD)
        update_payload = {param: value}
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(budget.id, deposit.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        deposit.refresh_from_db()
        assert getattr(deposit, param) == update_payload[param]

    def test_error_partial_update_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, deposit_factory: FactoryMetaClass
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PATCH without authentication.
        THEN: Unauthorized HTTP 401.
        """
        deposit = deposit_factory()
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.patch(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_partial_update_deposit_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PATCH by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        deposit = deposit_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.patch(url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    @pytest.mark.parametrize('param, value', [('name', PAYLOAD['name'])])
    def test_error_on_deposit_partial_update(
        self,
        api_client: APIClient,
        base_user: Any,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: Deposit instance for Budget created in database. Update payload with invalid value.
        WHEN: DepositViewSet detail view called with PATCH by User belonging to Budget
        with invalid payload.
        THEN: Bad request HTTP 400, Deposit not updated.
        """
        budget = budget_factory(owner=base_user)
        deposit_factory(budget=budget, **self.PAYLOAD)
        deposit = deposit_factory(budget=budget)
        old_value = getattr(deposit, param)
        update_payload = {param: value}
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(budget.id, deposit.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        deposit.refresh_from_db()
        assert getattr(deposit, param) == old_value


@pytest.mark.django_db
class TestDepositApiFullUpdate:
    """Tests for full update view on DepositViewSet."""

    INITIAL_PAYLOAD = {
        'name': 'Supermarket',
        'description': 'Supermarket in which I buy food.',
        'is_active': True,
        'is_deposit': False,
    }

    UPDATE_PAYLOAD = {
        'name': 'Some market',
        'description': 'Updated supermarket description.',
        'is_active': False,
        'is_deposit': True,
    }

    @pytest.mark.django_db
    def test_deposit_full_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PUT by User belonging to Budget.
        THEN: HTTP 200, Deposit updated.
        """
        budget = budget_factory(owner=base_user)
        deposit = deposit_factory(budget=budget, **self.INITIAL_PAYLOAD)
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(budget.id, deposit.id)

        response = api_client.put(url, self.UPDATE_PAYLOAD)

        assert response.status_code == status.HTTP_200_OK
        deposit.refresh_from_db()
        for param in self.UPDATE_PAYLOAD:
            assert getattr(deposit, param) == self.UPDATE_PAYLOAD[param]

    def test_error_full_update_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, deposit_factory: FactoryMetaClass
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PUT without authentication.
        THEN: Unauthorized HTTP 401.
        """
        deposit = deposit_factory()
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_full_update_deposit_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PUT by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        deposit = deposit_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    @pytest.mark.parametrize('param, value', [('name', INITIAL_PAYLOAD['name'])])
    def test_error_on_deposit_full_update(
        self,
        api_client: APIClient,
        base_user: Any,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: Deposit instance for Budget created in database. Update payload with invalid value.
        WHEN: DepositViewSet detail view called with PUT by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400, Deposit not updated.
        """
        budget = budget_factory(owner=base_user)
        deposit_factory(budget=budget, **self.INITIAL_PAYLOAD)
        deposit = deposit_factory(budget=budget)
        old_value = getattr(deposit, param)
        update_payload = self.UPDATE_PAYLOAD.copy()
        update_payload[param] = value
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(budget.id, deposit.id)

        response = api_client.put(url, update_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        deposit.refresh_from_db()
        assert getattr(deposit, param) == old_value


@pytest.mark.django_db
class TestDepositApiDelete:
    """Tests for delete Deposit on DepositViewSet."""

    def test_delete_deposit(
        self,
        api_client: APIClient,
        base_user: Any,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with DELETE by User belonging to Budget.
        THEN: No content HTTP 204, Deposit deleted.
        """
        budget = budget_factory(owner=base_user)
        deposit = deposit_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(budget.id, deposit.id)

        assert budget.entities.filter(is_deposit=True).count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not budget.entities.filter(is_deposit=True).exists()

    def test_error_delete_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, deposit_factory: FactoryMetaClass
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with PUT without authentication.
        THEN: Unauthorized HTTP 401.
        """
        deposit = deposit_factory()
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_delete_deposit_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        deposit_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Deposit instance for Budget created in database.
        WHEN: DepositViewSet detail view called with DELETE by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        deposit = deposit_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = deposit_detail_url(deposit.budget.id, deposit.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
