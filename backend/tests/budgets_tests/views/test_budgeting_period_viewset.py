"""
Tests for BudgetingPeriodViewSet:
* TestBudgetingPeriodViewSetList - GET on list view.
* TestBudgetingPeriodViewSetCreate - POST on list view.
* TestBudgetingPeriodViewSetDetail - GET on detail view.
* TestBudgetingPeriodViewSetUpdate - PATCH on detail view.
* TestBudgetingPeriodViewSetDelete - DELETE on detail view.
"""

from datetime import date
from typing import Any

import pytest
from budgets.models.budget_model import Budget
from budgets.models.budgeting_period_model import BudgetingPeriod
from budgets.serializers.budgeting_period_serializer import BudgetingPeriodSerializer
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from factory.base import FactoryMetaClass
from rest_framework import status
from rest_framework.test import APIClient


def periods_url(budget_id):
    """Creates and returns Budget BudgetingPeriods URL."""
    return reverse('budgets:period-list', args=[budget_id])


def period_detail_url(budget_id, period_id):
    """Creates and returns BudgetingPeriod detail URL."""
    return reverse('budgets:period-detail', args=[budget_id, period_id])


@pytest.mark.django_db
class TestBudgetingPeriodViewSetList:
    """Tests for BudgetingPeriodViewSet list view."""

    def test_auth_required(self, budget: Budget, api_client: APIClient):
        """
        GIVEN: Budget model instance in database created.
        WHEN: BudgetingPeriodViewSet list view called without authentication.
        THEN: Unauthorized HTTP status returned.
        """
        url = periods_url(budget.id)

        res = api_client.get(url)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_periods_list_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two BudgetingPeriods for Budget in database created.
        WHEN: BudgetingPeriodViewSet list view for Budget id called by authenticated Budget owner.
        THEN: List of BudgetingPeriods for given Budget id sorted from newest to oldest returned.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        budgeting_period_factory(
            budget=budget, date_start=date(2023, 1, 1), date_end=date(2023, 1, 31), is_active=False
        )
        budgeting_period_factory(budget=budget, date_start=date(2023, 2, 1), date_end=date(2023, 2, 28), is_active=True)
        url = periods_url(budget.id)

        response = api_client.get(url)

        periods = BudgetingPeriod.objects.filter(budget=budget).order_by('-date_start')
        serializer = BudgetingPeriodSerializer(periods, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(serializer.data) == periods.count() == 2
        assert response.data['results'] == serializer.data

    def test_retrieve_periods_list_by_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two BudgetingPeriods for Budget in database created.
        WHEN: BudgetingPeriodViewSet list view for Budget id called by authenticated Budget member.
        THEN: List of BudgetingPeriods for given Budget id sorted from newest to oldest returned.
        """
        budget = budget_factory(members=[base_user])
        api_client.force_authenticate(base_user)
        budgeting_period_factory(
            budget=budget, date_start=date(2023, 1, 1), date_end=date(2023, 1, 31), is_active=False
        )
        budgeting_period_factory(budget=budget, date_start=date(2023, 2, 1), date_end=date(2023, 2, 28), is_active=True)
        url = periods_url(budget.id)

        response = api_client.get(url)

        periods = BudgetingPeriod.objects.filter(budget=budget).order_by('-date_start')
        serializer = BudgetingPeriodSerializer(periods, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(serializer.data) == periods.count() == 2
        assert response.data['results'] == serializer.data

    def test_periods_list_limited_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two BudgetingPeriods for two different Budgets in database created.
        WHEN: BudgetingPeriodViewSet list view for Budget id called by authenticated User.
        THEN: List of BudgetingPeriods containing only declared Budget periods returned.
        """
        # Other period
        budgeting_period_factory()
        # Auth User period
        budget = budget_factory(owner=base_user)
        period = budgeting_period_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = periods_url(budget.id)

        response = api_client.get(url)

        periods = BudgetingPeriod.objects.filter(budget=budget)
        serializer = BudgetingPeriodSerializer(periods, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert BudgetingPeriod.objects.all().count() == 2
        assert len(response.data['results']) == len(serializer.data) == periods.count() == 1
        assert periods.first() == period
        assert response.data['results'] == serializer.data


@pytest.mark.django_db
class TestBudgetingPeriodViewSetCreate:
    """Tests for creating BudgetingPeriod via BudgetingPeriodViewSet."""

    def test_auth_required(self, budget: Budget, api_client: APIClient):
        """
        GIVEN: Budget model instance in database created.
        WHEN: BudgetingPeriodViewSet list view called with POST without authentication.
        THEN: Unauthorized HTTP 401 status returned.
        """
        url = periods_url(budget.id)

        res = api_client.post(url, data={})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_single_period_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view for Budget id called by authenticated Budget owner by POST with
        valid data.
        THEN: BudgetingPeriod for Budget created in database.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload = {'name': '2023_01', 'date_start': date(2023, 1, 1), 'date_end': date(2023, 1, 31)}
        url = periods_url(budget.id)

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 1
        period = BudgetingPeriod.objects.get(id=response.data['id'])
        for key in payload:
            assert getattr(period, key) == payload[key]
        serializer = BudgetingPeriodSerializer(period)
        assert response.data == serializer.data

    def test_create_single_period_by_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view for Budget id called by Budget member by POST with valid data.
        THEN: BudgetingPeriod for Budget created in database.
        """
        budget = budget_factory(members=[base_user])
        api_client.force_authenticate(base_user)
        payload = {'name': '2023_01', 'date_start': date(2023, 1, 1), 'date_end': date(2023, 1, 31)}
        url = periods_url(budget.id)

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 1
        period = BudgetingPeriod.objects.get(id=response.data['id'])
        for key in payload:
            assert getattr(period, key) == payload[key]
        serializer = BudgetingPeriodSerializer(period)
        assert response.data == serializer.data

    def test_create_two_periods_for_one_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view for Budget id called by authenticated User by POST
        with valid data two times.
        THEN: Two BudgetingPeriod for Budget created in database.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload_1 = {
            'name': '2023_01',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
        }
        payload_2 = {
            'name': '2023_02',
            'date_start': date(2023, 2, 1),
            'date_end': date(2023, 2, 28),
        }
        url = periods_url(budget.id)

        response_1 = api_client.post(url, payload_1)
        response_2 = api_client.post(url, payload_2)

        assert response_1.status_code == status.HTTP_201_CREATED
        assert response_2.status_code == status.HTTP_201_CREATED
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 2
        for response, payload in [(response_1, payload_1), (response_2, payload_2)]:
            period = BudgetingPeriod.objects.get(id=response.data['id'])
            for key in payload:
                assert getattr(period, key) == payload[key]

    def test_create_same_period_for_two_budgets(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Two Budgets in database created.
        WHEN: BudgetingPeriodViewSet list view called for two Budgets by authenticated User by POST with valid data.
        THEN: Two BudgetingPeriod, every for different Budget created in database.
        """
        payload = {
            'name': '2023_01',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
        }
        api_client.force_authenticate(base_user)
        budget_1 = budget_factory(owner=base_user)
        url = periods_url(budget_1.id)
        api_client.post(url, payload)
        budget_2 = budget_factory(owner=base_user)
        url = periods_url(budget_2.id)
        api_client.post(url, payload)

        all_periods_queryset = BudgetingPeriod.objects.all()
        assert all_periods_queryset.count() == 2
        for budget in (budget_1, budget_2):
            budget_periods_queryset = all_periods_queryset.filter(budget=budget)
            assert budget_periods_queryset.count() == 1

    def test_error_name_too_long(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST with name
        too long in passed data.
        THEN: Bad request 400 returned, no object in database created.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        max_length = BudgetingPeriod._meta.get_field('name').max_length
        payload = {
            'name': (max_length + 1) * 'a',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
        }
        url = periods_url(budget.id)

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data['detail']
        assert response.data['detail']['name'][0] == f'Ensure this field has no more than {max_length} characters.'
        assert not BudgetingPeriod.objects.filter(budget=budget).exists()

    def test_error_name_already_used(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: BudgetingPeriod for Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST with name already used
        for existing BudgetingPeriod in passed data.
        THEN: Bad request 400 returned, no object in database created.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload = {
            'name': '2023_01',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 2),
        }
        BudgetingPeriod.objects.create(budget=budget, **payload)
        payload['date_start'] = date(2023, 1, 3)
        payload['date_end'] = date(2023, 1, 4)
        url = periods_url(budget.id)

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data['detail']
        assert response.data['detail']['name'][0] == f'Period with name "{payload["name"]}" already exists in Budget.'
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 1

    def test_create_active_period_successfully(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called twice for Budget by authenticated User by POST to create active
        and inactive BudgetingPeriods.
        THEN: Two BudgetingPeriods for Budget in database create - one active, one inactive.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload_inactive = {
            'name': '2023_01',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'is_active': False,
        }
        payload_active = {
            'name': '2023_02',
            'date_start': date(2023, 2, 1),
            'date_end': date(2023, 2, 28),
            'is_active': True,
        }
        url = periods_url(budget.id)

        response_inactive = api_client.post(url, payload_inactive)
        response_active = api_client.post(url, payload_active)

        assert BudgetingPeriod.objects.all().count() == 2
        budget_periods = BudgetingPeriod.objects.filter(budget=budget)
        assert budget_periods.count() == 2
        for response, payload in [(response_inactive, payload_inactive), (response_active, payload_active)]:
            assert response.status_code == status.HTTP_201_CREATED
            period = budget_periods.get(id=response.data['id'])
            assert period.is_active == payload['is_active']

    def test_error_create_period_when_is_active_set_already(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Active BudgetingPeriod for Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST
        to create active BudgetingPeriod.
        THEN: Bad request 400 returned, no object in database created.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload_1 = {
            'name': '2023_01',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'is_active': True,
        }
        active_period = BudgetingPeriod.objects.create(budget=budget, **payload_1)
        payload_2 = {
            'name': '2023_02',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'is_active': True,
        }
        url = periods_url(budget.id)

        response = api_client.post(url, payload_2)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'is_active' in response.data['detail']
        assert response.data['detail']['is_active'][0] == 'Active period already exists in Budget.'
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 1
        assert BudgetingPeriod.objects.filter(budget=budget).first() == active_period

    def test_is_active_default_value(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST to create
        BudgetingPeriod without declaring if it's active or not.
        THEN: BudgetingPeriod for Budget in database created with 'is_active' set to False by default.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload = {
            'name': '2023_02',
            'date_start': date(2023, 1, 1),
            'date_end': date(2023, 1, 31),
            'is_active': '',
        }
        url = periods_url(budget.id)

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert BudgetingPeriod.objects.all().count() == 1
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 1
        assert response.data['is_active'] is False

    @pytest.mark.parametrize('date_start, date_end', (('', date.today()), (date.today(), ''), ('', '')))
    def test_error_date_blank(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        date_start: date | str,
        date_end: date | str,
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST to create
        BudgetingPeriod with one of or both dates blank.
        THEN: Bad request 400 returned, no object in database created.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload = {'name': '2023_01', 'date_start': date_start, 'date_end': date_end, 'is_active': False}
        url = periods_url(budget.id)
        error_message = 'Date has wrong format. Use one of these formats instead: YYYY-MM-DD.'

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'date_start' in response.data['detail'] or 'date_end' in response.data['detail']
        assert (
            response.data['detail'].get('date_start', [''])[0] == error_message
            or response.data['detail'].get('date_end', [''])[0] == error_message
        )
        assert not BudgetingPeriod.objects.filter(budget=budget).exists()

    def test_error_date_end_before_date_start(
        self, api_client: APIClient, base_user: AbstractUser, budget_factory: FactoryMetaClass
    ):
        """
        GIVEN: Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST to create
        BudgetingPeriod with date_end before date_start.
        THEN: Bad request 400 returned, no object in database created.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload = {'name': '2023_01', 'date_start': date(2023, 5, 1), 'date_end': date(2023, 4, 30), 'is_active': False}
        url = periods_url(budget.id)

        response = api_client.post(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert response.data['detail']['non_field_errors'][0] == 'Start date should be earlier than end date.'
        assert not BudgetingPeriod.objects.filter(budget=budget).exists()

    @pytest.mark.parametrize(
        'date_start, date_end',
        (
            # Date start before first existing period
            (date(2023, 5, 1), date(2023, 6, 1)),
            (date(2023, 5, 1), date(2023, 6, 15)),
            (date(2023, 5, 1), date(2023, 6, 30)),
            (date(2023, 5, 1), date(2023, 7, 1)),
            (date(2023, 5, 1), date(2023, 7, 15)),
            (date(2023, 5, 1), date(2023, 7, 31)),
            (date(2023, 5, 1), date(2023, 8, 1)),
            # Date start same as in first existing period
            (date(2023, 6, 1), date(2023, 6, 15)),
            (date(2023, 6, 1), date(2023, 6, 30)),
            (date(2023, 6, 1), date(2023, 7, 1)),
            (date(2023, 6, 1), date(2023, 7, 15)),
            (date(2023, 6, 1), date(2023, 7, 31)),
            (date(2023, 6, 1), date(2023, 8, 1)),
            # Date start between first existing period daterange
            (date(2023, 6, 15), date(2023, 6, 30)),
            (date(2023, 6, 15), date(2023, 7, 1)),
            (date(2023, 6, 15), date(2023, 7, 15)),
            (date(2023, 6, 15), date(2023, 7, 31)),
            (date(2023, 6, 15), date(2023, 8, 1)),
            # Date start same as first existing period's end date
            (date(2023, 6, 30), date(2023, 7, 1)),
            (date(2023, 6, 30), date(2023, 7, 15)),
            (date(2023, 6, 30), date(2023, 7, 31)),
            (date(2023, 6, 30), date(2023, 8, 1)),
            # Date start same as in second existing period
            (date(2023, 7, 1), date(2023, 7, 15)),
            (date(2023, 7, 1), date(2023, 7, 31)),
            (date(2023, 7, 1), date(2023, 8, 1)),
            # Date start between second existing period daterange
            (date(2023, 7, 15), date(2023, 7, 31)),
            # Date start same as second existing period's end date
            (date(2023, 7, 31), date(2023, 8, 1)),
        ),
    )
    def test_error_date_invalid(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        date_start: date,
        date_end: date,
    ):
        """
        GIVEN: Two BudgetingPeriods for Budget in database created.
        WHEN: BudgetingPeriodViewSet list view called for Budget by authenticated User by POST to create
        BudgetingPeriod with dates colliding with existing BudgetingPeriods.
        THEN: Bad request 400 returned, no object in database created.
        """
        budget = budget_factory(owner=base_user)
        payload_1 = {
            'name': '2023_06',
            'date_start': date(2023, 6, 1),
            'date_end': date(2023, 6, 30),
        }
        payload_2 = {
            'name': '2023_07',
            'date_start': date(2023, 7, 1),
            'date_end': date(2023, 7, 31),
        }
        payload_invalid = {
            'name': 'invalid',
            'date_start': date_start,
            'date_end': date_end,
        }
        BudgetingPeriod.objects.create(budget=budget, **payload_1)
        BudgetingPeriod.objects.create(budget=budget, **payload_2)
        api_client.force_authenticate(base_user)
        url = periods_url(budget.id)

        response = api_client.post(url, payload_invalid)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Budgeting period date range collides with other period in Budget.'
        )
        assert BudgetingPeriod.objects.filter(budget=budget).count() == 2


@pytest.mark.django_db
class TestBudgetingPeriodViewSetDetail:
    """Tests for detail view in BudgetingPeriodViewSet."""

    def test_auth_required(self, budgeting_period: BudgetingPeriod, api_client: APIClient):
        """
        GIVEN: BudgetingPeriod model instance in database created.
        WHEN: BudgetingPeriodViewSet detail view called with GET without authentication.
        THEN: Unauthorized HTTP 401 status returned.
        """
        url = period_detail_url(budgeting_period.budget.id, budgeting_period.id)

        res = api_client.post(url)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_period_details_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (owner of Budget).
        THEN: BudgetingPeriod details returned.
        """
        budget = budget_factory(owner=base_user)
        period = budgeting_period_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = period_detail_url(budget.id, period.id)

        response = api_client.get(url)
        serializer = BudgetingPeriodSerializer(period)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_get_period_details_by_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (member of Budget).
        THEN: BudgetingPeriod details returned.
        """
        budget = budget_factory(members=[base_user])
        period = budgeting_period_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = period_detail_url(budget.id, period.id)

        response = api_client.get(url)
        serializer = BudgetingPeriodSerializer(period)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_error_get_period_details_unauthenticated(
        self, api_client: APIClient, budgeting_period_factory: FactoryMetaClass
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        period = budgeting_period_factory()
        url = period_detail_url(period.budget.id, period.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_get_other_user_period_details(
        self,
        api_client: APIClient,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (not Budget owner
        nor member).
        THEN: Forbidden HTTP 403 returned.
        """
        user_1 = user_factory()
        user_2 = user_factory()
        period = budgeting_period_factory(budget=budget_factory(owner=user_1))
        api_client.force_authenticate(user_2)

        url = period_detail_url(period.budget.id, period.id)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBudgetingPeriodViewSetUpdate:
    """Tests for partial update BudgetingPeriod via BudgetingPeriodViewSet."""

    def test_auth_required(self, budgeting_period: BudgetingPeriod, api_client: APIClient):
        """
        GIVEN: BudgetingPeriod model instance in database created.
        WHEN: BudgetingPeriodViewSet detail view called with PATCH without authentication.
        THEN: Unauthorized HTTP 401 status returned.
        """
        url = period_detail_url(budgeting_period.budget.id, budgeting_period.id)

        res = api_client.patch(url, data={})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        'param, value', [('date_start', date(2024, 1, 2)), ('date_end', date(2024, 1, 30)), ('is_active', True)]
    )
    def test_update_single_field_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (Budget owner) by
        PATCH with valid data.
        THEN: BudgetingPeriod updated in database.
        """
        api_client.force_authenticate(base_user)
        period = budgeting_period_factory(
            budget=budget_factory(owner=base_user),
            date_start=date(2024, 1, 1),
            date_end=date(2024, 1, 31),
            is_active=False,
        )
        payload = {param: value}
        url = period_detail_url(period.budget.id, period.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        period.refresh_from_db()
        assert getattr(period, param) == payload[param]

    @pytest.mark.parametrize(
        'param, value', [('date_start', date(2024, 1, 2)), ('date_end', date(2024, 1, 30)), ('is_active', True)]
    )
    def test_update_single_field_by_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (Budget member) by
        PATCH with valid data.
        THEN: BudgetingPeriod updated in database.
        """
        api_client.force_authenticate(base_user)
        period = budgeting_period_factory(
            budget=budget_factory(members=[base_user]),
            date_start=date(2024, 1, 1),
            date_end=date(2024, 1, 31),
            is_active=False,
        )
        payload = {param: value}
        url = period_detail_url(period.budget.id, period.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        period.refresh_from_db()
        assert getattr(period, param) == payload[param]

    def test_update_many_fields(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (Budget member) by
        PATCH with valid data.
        THEN: BudgetingPeriod updated in database.
        """
        api_client.force_authenticate(base_user)
        period = budgeting_period_factory(
            budget=budget_factory(members=[base_user]),
            date_start=date(2024, 1, 1),
            date_end=date(2024, 1, 31),
            is_active=False,
        )
        payload = {
            'name': '2023_07',
            'date_start': date(2023, 7, 1),
            'date_end': date(2023, 7, 31),
            'is_active': True,
        }
        url = period_detail_url(period.budget.id, period.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_200_OK
        period.refresh_from_db()
        for param, value in payload.items():
            assert getattr(period, param) == value

    @pytest.mark.parametrize(
        'param, value', [('date_start', date(2023, 12, 31)), ('date_end', date(2024, 2, 1)), ('is_active', True)]
    )
    def test_error_on_period_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (Budget owner) by
        PATCH with invalid data.
        THEN: Bad request HTTP 400 returned.
        """
        api_client.force_authenticate(base_user)
        budget = budget_factory(owner=base_user)
        budgeting_period_factory(budget=budget, date_start=date(2024, 1, 1), date_end=date(2024, 1, 31), is_active=True)
        period = budgeting_period_factory(
            budget=budget, date_start=date(2024, 2, 1), date_end=date(2024, 2, 29), is_active=False
        )
        old_value = getattr(period, param)
        payload = {param: value}
        url = period_detail_url(budget.id, period.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        period.refresh_from_db()
        assert getattr(period, param) == old_value


@pytest.mark.django_db
class TestBudgetingPeriodViewSetDelete:
    """Tests for delete BudgetingPeriod via BudgetingPeriodViewSet."""

    def test_auth_required(self, budgeting_period: BudgetingPeriod, api_client: APIClient):
        """
        GIVEN: BudgetingPeriod model instance in database created.
        WHEN: BudgetingPeriodViewSet detail view called with DELETE without authentication.
        THEN: Unauthorized HTTP 401 status returned.
        """
        url = period_detail_url(budgeting_period.budget.id, budgeting_period.id)

        res = api_client.delete(url)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_period_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (Budget owner)
        by DELETE.
        THEN: BudgetingPeriod deleted from database.
        """
        api_client.force_authenticate(base_user)
        period = budgeting_period_factory(budget=budget_factory(owner=base_user))
        url = period_detail_url(period.budget.id, period.id)

        assert BudgetingPeriod.objects.all().count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not BudgetingPeriod.objects.all().exists()

    def test_delete_period_by_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (Budget member)
        by DELETE.
        THEN: BudgetingPeriod deleted from database.
        """
        api_client.force_authenticate(base_user)
        period = budgeting_period_factory(budget=budget_factory(members=[base_user]))
        url = period_detail_url(period.budget.id, period.id)

        assert BudgetingPeriod.objects.all().count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not BudgetingPeriod.objects.all().exists()

    def test_error_delete_not_accessible_period(
        self,
        api_client: APIClient,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
    ):
        """
        GIVEN: BudgetingPeriod created in database.
        WHEN: BudgetingPeriodViewSet detail view called for BudgetingPeriod by authenticated User (not Budget owner
        nor member) by DELETE.
        THEN: Forbidden HTTP 403 returned, BudgetingPeriod not deleted.
        """
        period = budgeting_period_factory(budget=budget_factory(owner=user_factory()))
        url = period_detail_url(period.budget.id, period.id)
        api_client.force_authenticate(user_factory())

        assert BudgetingPeriod.objects.all().count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert BudgetingPeriod.objects.filter(id=period.id).exists()
