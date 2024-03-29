from typing import Any

import pytest
from deposits.models import Deposit
from deposits.serializers import DepositSerializer
from django.urls import reverse
from factory.base import FactoryMetaClass
from rest_framework import status
from rest_framework.test import APIClient

DEPOSITS_URL = reverse('deposits:deposit-list')


def deposit_detail_url(deposit_id):
    """Create and return a deposit detail URL."""
    return reverse('deposits:deposit-detail', args=[deposit_id])


@pytest.mark.django_db
class TestDepositApi:
    """Tests for DepositViewSet."""

    def test_auth_required(self, api_client: APIClient):
        """Test auth is required to call endpoint."""
        res = api_client.get(DEPOSITS_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_deposits_list(self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass):
        """Test retrieving list of deposits."""
        api_client.force_authenticate(base_user)
        deposit_factory(user=base_user)
        deposit_factory(user=base_user)

        response = api_client.get(DEPOSITS_URL)

        deposits = Deposit.objects.all()
        serializer = DepositSerializer(deposits, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_deposits_list_limited_to_user(
        self, api_client: APIClient, user_factory: FactoryMetaClass, deposit_factory: FactoryMetaClass
    ):
        """Test retrieved list of deposits is limited to authenticated user."""
        user = user_factory()
        deposit_factory(user=user)
        deposit_factory()
        api_client.force_authenticate(user)

        response = api_client.get(DEPOSITS_URL)

        deposits = Deposit.objects.filter(user=user)
        serializer = DepositSerializer(deposits, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_create_single_deposit(self, api_client: APIClient, base_user: Any):
        """Test creating single Deposit."""
        api_client.force_authenticate(base_user)
        payload = {'name': 'My account', 'description': 'Account that I use.', 'is_active': True}

        response = api_client.post(DEPOSITS_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Deposit.objects.filter(user=base_user).count() == 1
        deposit = Deposit.objects.get(id=response.data['id'])
        for key in payload:
            assert getattr(deposit, key) == payload[key]
        serializer = DepositSerializer(deposit)
        assert response.data == serializer.data

    def test_create_two_deposits_by_one_user(self, api_client: APIClient, base_user: Any):
        """Test creating two valid Deposits by single user."""
        api_client.force_authenticate(base_user)
        payload_1 = {'name': 'My account', 'description': 'Account that I use.', 'is_active': True}
        payload_2 = {'name': 'Old account', 'description': 'Not used account.', 'is_active': False}

        response_1 = api_client.post(DEPOSITS_URL, payload_1)
        response_2 = api_client.post(DEPOSITS_URL, payload_2)

        assert response_1.status_code == status.HTTP_201_CREATED
        assert response_2.status_code == status.HTTP_201_CREATED
        assert Deposit.objects.filter(user=base_user).count() == 2
        for response, payload in [(response_1, payload_1), (response_2, payload_2)]:
            deposit = Deposit.objects.get(id=response.data['id'])
            for key in payload:
                assert getattr(deposit, key) == payload[key]

    def test_create_same_deposit_by_two_users(self, api_client: APIClient, user_factory: Any):
        """Test creating deposit with the same params by two users."""
        payload = {'name': 'My account', 'description': 'Account that I use.', 'is_active': True}
        user_1 = user_factory()
        api_client.force_authenticate(user_1)
        api_client.post(DEPOSITS_URL, payload)

        user_2 = user_factory()
        api_client.force_authenticate(user_2)
        api_client.post(DEPOSITS_URL, payload)

        assert Deposit.objects.all().count() == 2
        assert Deposit.objects.filter(user=user_1).count() == 1
        assert Deposit.objects.filter(user=user_2).count() == 1

    def test_error_name_too_long(self, api_client: APIClient, base_user: Any):
        """Test error on creating Deposit with name too long."""
        api_client.force_authenticate(base_user)
        max_length = Deposit._meta.get_field('name').max_length
        payload = {'name': (max_length + 1) * 'a', 'description': 'Account that I use.', 'is_active': True}

        response = api_client.post(DEPOSITS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
        assert response.data['name'][0] == f'Ensure this field has no more than {max_length} characters.'
        assert not Deposit.objects.filter(user=base_user).exists()

    def test_error_name_already_used(self, api_client: APIClient, base_user: Any):
        """Test error on creating Deposit with already used name by the same user."""
        api_client.force_authenticate(base_user)
        payload = {'name': 'My account', 'description': 'Account that I use.', 'is_active': True}
        Deposit.objects.create(user=base_user, **payload)

        response = api_client.post(DEPOSITS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data
        assert response.data['name'][0] == f"Users deposit with name {payload['name']} already exists."
        assert Deposit.objects.filter(user=base_user).count() == 1

    def test_error_description_too_long(self, api_client: APIClient, base_user: Any):
        """Test error on creating Deposit with description too long."""
        api_client.force_authenticate(base_user)
        max_length = Deposit._meta.get_field('description').max_length
        payload = {'name': 'My account', 'description': (max_length + 1) * 'a', 'is_active': True}

        response = api_client.post(DEPOSITS_URL, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'description' in response.data
        assert response.data['description'][0] == f'Ensure this field has no more than {max_length} characters.'
        assert not Deposit.objects.filter(user=base_user).exists()

    def test_is_active_default_value(self, api_client: APIClient, base_user: Any):
        """Test creating Deposit without passing is_active ends with default value."""
        api_client.force_authenticate(base_user)
        default = Deposit._meta.get_field('is_active').default
        payload = {'name': 'My account', 'description': 'Account that I use.'}

        response = api_client.post(DEPOSITS_URL, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert Deposit.objects.all().count() == 1
        assert Deposit.objects.filter(user=base_user).count() == 1
        assert response.data['is_active'] == default

    def test_get_deposit_details(self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass):
        """Test get Deposit details."""
        api_client.force_authenticate(base_user)
        deposit = deposit_factory(user=base_user)
        url = deposit_detail_url(deposit.id)

        response = api_client.get(url)
        serializer = DepositSerializer(deposit)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_error_get_deposit_details_unauthenticated(
        self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass
    ):
        """Test error on getting Deposit details being unauthenticated."""
        deposit = deposit_factory(user=base_user)
        url = deposit_detail_url(deposit.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_get_other_user_deposit_details(
        self, api_client: APIClient, user_factory: FactoryMetaClass, deposit_factory: FactoryMetaClass
    ):
        """Test error on getting other user's Deposit details."""
        user_1 = user_factory()
        user_2 = user_factory()
        deposit = deposit_factory(user=user_1)
        api_client.force_authenticate(user_2)

        url = deposit_detail_url(deposit.id)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        'param, value', [('name', 'New name'), ('description', 'New description'), ('is_active', True)]
    )
    def test_deposit_partial_update(
        self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass, param: str, value: Any
    ):
        """Test partial update of a Deposit"""
        api_client.force_authenticate(base_user)
        deposit = deposit_factory(user=base_user, name='Account', description='My account', is_active=False)
        payload = {param: value}
        url = deposit_detail_url(deposit.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        deposit.refresh_from_db()
        assert getattr(deposit, param) == payload[param]

    @pytest.mark.parametrize('param, value', [('name', 'Old account')])
    def test_error_on_deposit_partial_update(
        self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass, param: str, value: Any
    ):
        """Test error on partial update of a Deposit."""
        api_client.force_authenticate(base_user)
        deposit_factory(user=base_user, name='Old account', description='My old account', is_active=True)
        deposit = deposit_factory(user=base_user, name='New account', description='My new account', is_active=True)
        old_value = getattr(deposit, param)
        payload = {param: value}
        url = deposit_detail_url(deposit.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        deposit.refresh_from_db()
        assert getattr(deposit, param) == old_value

    def test_deposit_full_update(self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass):
        """Test successful full update of a Deposit"""
        api_client.force_authenticate(base_user)
        payload_old = {
            'name': 'Old account',
            'description': 'My old account',
            'is_active': False,
        }
        payload_new = {
            'name': 'New account',
            'description': 'My new account',
            'is_active': True,
        }
        deposit = deposit_factory(user=base_user, **payload_old)
        url = deposit_detail_url(deposit.id)

        response = api_client.put(url, payload_new)

        assert response.status_code == status.HTTP_200_OK
        deposit.refresh_from_db()
        for k, v in payload_new.items():
            assert getattr(deposit, k) == v

    @pytest.mark.parametrize(
        'payload_new',
        [
            {'name': 'Old account', 'description': 'My new account', 'is_active': True},
        ],
    )
    def test_error_on_deposit_full_update(
        self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass, payload_new: dict
    ):
        """Test error on full update of a Deposit."""
        api_client.force_authenticate(base_user)
        deposit_factory(user=base_user, name='Old account', description='My old account', is_active=True)
        payload_old = {
            'name': 'New account',
            'description': 'My new account',
            'is_active': True,
        }

        deposit = deposit_factory(user=base_user, **payload_old)
        url = deposit_detail_url(deposit.id)

        response = api_client.patch(url, payload_new)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        deposit.refresh_from_db()
        for k, v in payload_old.items():
            assert getattr(deposit, k) == v

    def test_delete_deposit(self, api_client: APIClient, base_user: Any, deposit_factory: FactoryMetaClass):
        """Test deleting Deposit."""
        api_client.force_authenticate(base_user)
        deposit = deposit_factory(user=base_user)
        url = deposit_detail_url(deposit.id)

        assert Deposit.objects.all().count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Deposit.objects.all().exists()
