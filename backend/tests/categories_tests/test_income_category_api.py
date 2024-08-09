from typing import Any

import pytest
from categories.models import IncomeCategory
from categories.serializers import IncomeCategorySerializer
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from factory.base import FactoryMetaClass
from rest_framework import status
from rest_framework.test import APIClient


def income_category_url(budget_id: int):
    """Create and return an IncomeCategory list URL."""
    return reverse('budgets:income_category-list', args=[budget_id])


def income_category_detail_url(budget_id: int, category_id: int):
    """Create and return an IncomeCategory detail URL."""
    return reverse('budgets:income_category-detail', args=[budget_id, category_id])


@pytest.mark.django_db
class TestIncomeCategoryApiAccess:
    """Tests for access to IncomeCategoryViewSet."""

    def test_auth_required_on_list_view(self, api_client: APIClient, income_category: IncomeCategory):
        """
        GIVEN: IncomeCategory model instance in database.
        WHEN: IncomeCategoryViewSet list method called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        response = api_client.get(income_category_url(income_category.budget.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_auth_required_on_detail_view(self, api_client: APIClient, income_category: IncomeCategory):
        """
        GIVEN: IncomeCategory model instance in database.
        WHEN: IncomeCategoryViewSet detail method called without authentication.
        THEN: Unauthorized HTTP 401 returned.
        """
        response = api_client.get(income_category_detail_url(income_category.budget.id, income_category.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_budget_member_on_list_view(
        self, api_client: APIClient, user_factory: FactoryMetaClass, income_category_factory: FactoryMetaClass
    ):
        """
        GIVEN: IncomeCategory model instance in database.
        WHEN: IncomeCategoryViewSet list method called by User not belonging to given Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        budget_owner = user_factory()
        other_user = user_factory()
        income_category = income_category_factory(budget__owner=budget_owner)
        api_client.force_authenticate(other_user)

        response = api_client.get(income_category_url(income_category.budget.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    def test_user_not_budget_member_on_detail_view(
        self,
        api_client: APIClient,
        user_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory model instance in database.
        WHEN: IncomeCategoryViewSet detail method called by User not belonging to given Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        budget_owner = user_factory()
        other_user = user_factory()
        income_category = income_category_factory(budget__owner=budget_owner)
        api_client.force_authenticate(other_user)

        response = api_client.get(income_category_detail_url(income_category.budget.id, income_category.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'


@pytest.mark.django_db
class TestIncomeCategoryApiList:
    """Tests for list view on IncomeCategoryViewSet."""

    def test_retrieve_category_list_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory model instances for single Budget created in database.
        WHEN: IncomeCategoryViewSet called by Budget owner.
        THEN: Response with serialized Budget IncomeCategory list returned.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        for _ in range(2):
            income_category_factory(budget=budget)

        response = api_client.get(income_category_url(budget.id))

        categories = IncomeCategory.objects.filter(budget=budget)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_retrieve_category_list_by_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory model instances for single Budget created in database.
        WHEN: IncomeCategoryViewSet called by Budget member.
        THEN: Response with serialized Budget IncomeCategory list returned.
        """
        budget = budget_factory(members=[base_user])
        api_client.force_authenticate(base_user)
        for _ in range(2):
            income_category_factory(budget=budget)

        response = api_client.get(income_category_url(budget.id))

        categories = IncomeCategory.objects.filter(budget=budget)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_category_list_limited_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory model instances for different Budgets created in database.
        WHEN: IncomeCategoryViewSet called by one of Budgets owner.
        THEN: Response with serialized IncomeCategory list (only from given Budget) returned.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget)
        income_category_factory()
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id))

        categories = IncomeCategory.objects.filter(budget=budget)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == category.id

    @pytest.mark.parametrize('sort_param', ('id', '-id', 'group', '-group', 'name', '-name'))
    def test_get_categories_list_sorted_by_param(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
        sort_param: str,
    ):
        """
        GIVEN: Three IncomeCategory objects created in database.
        WHEN: The IncomeCategoryViewSet list view is called with sorting by given param and without any filters.
        THEN: Response must contain all IncomeCategory existing in database sorted by given param.
        """
        budget = budget_factory(owner=base_user)
        for _ in range(3):
            income_category_factory(budget=budget)
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id), data={'ordering': sort_param})

        assert response.status_code == status.HTTP_200_OK
        categories = IncomeCategory.objects.all().order_by(sort_param)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == len(categories) == 3
        assert response.data['results'] == serializer.data

    @pytest.mark.parametrize(
        'filter_value', ('Test', 'TEST', 'test', 'name', 'NAME', 'Name', 'Test name', 'TEST NAME', 'test name')
    )
    def test_get_categories_list_filtered_by_name(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
        filter_value: str,
    ):
        """
        GIVEN: Two IncomeCategory objects for single Budget.
        WHEN: The IncomeCategoryViewSet list view is called with name filter.
        THEN: Response must contain all IncomeCategory existing in database assigned to Budget matching given
        name value.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(name='Test name', budget=budget)
        income_category_factory(name='Other category', budget=budget)
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id), data={'name': filter_value})

        assert response.status_code == status.HTTP_200_OK
        assert IncomeCategory.objects.all().count() == 2
        categories = IncomeCategory.objects.filter(budget=category.budget, name__icontains=filter_value)
        serializer = IncomeCategorySerializer(
            categories,
            many=True,
        )
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == category.id

    def test_get_categories_list_filtered_by_common_only_true(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory objects for single Budget.
        WHEN: The IncomeCategoryViewSet list view is called with True common_only filter.
        THEN: Response must contain only common IncomeCategory objects existing in database assigned to Budget.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget, owner=None)
        income_category_factory(budget=budget, owner=base_user)
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id), data={'common_only': True})

        assert response.status_code == status.HTTP_200_OK
        assert IncomeCategory.objects.all().count() == 2
        categories = IncomeCategory.objects.filter(budget=category.budget, owner__isnull=True)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == category.id

    def test_get_categories_list_filtered_by_common_only_false(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory objects for single Budget.
        WHEN: The IncomeCategoryViewSet list view is called with False common_only filter.
        THEN: Response must contain all IncomeCategory objects existing in database assigned to Budget.
        """
        budget = budget_factory(owner=base_user)
        income_category_factory(budget=budget, owner=base_user)
        income_category_factory(budget=budget, owner=None)
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id), data={'common_only': False})

        assert response.status_code == status.HTTP_200_OK
        assert IncomeCategory.objects.all().count() == 2
        categories = IncomeCategory.objects.filter(budget=budget)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 2
        assert response.data['results'] == serializer.data

    def test_get_categories_list_filtered_by_group(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory objects for single Budget.
        WHEN: The IncomeCategoryViewSet list view is called with group filter.
        THEN: Response must contain all IncomeCategory existing in database assigned to Budget matching given
        group value.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(group=IncomeCategory.IncomeGroups.REGULAR, budget=budget)
        income_category_factory(group=IncomeCategory.IncomeGroups.IRREGULAR, budget=budget)
        api_client.force_authenticate(base_user)

        response = api_client.get(
            income_category_url(budget.id), data={'group': IncomeCategory.IncomeGroups.REGULAR.value}
        )

        assert response.status_code == status.HTTP_200_OK
        assert IncomeCategory.objects.all().count() == 2
        categories = IncomeCategory.objects.filter(
            budget=category.budget, group=IncomeCategory.IncomeGroups.REGULAR.value
        )
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == category.id

    def test_get_categories_list_filtered_by_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two IncomeCategory objects for single Budget.
        WHEN: The IncomeCategoryViewSet list view is called with owner filter.
        THEN: Response must contain all IncomeCategory existing in database assigned to Budget matching given
        owner value.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget, owner=base_user)
        income_category_factory(budget=budget, owner=None)
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id), data={'owner': base_user.id})

        assert response.status_code == status.HTTP_200_OK
        assert IncomeCategory.objects.all().count() == 2
        categories = IncomeCategory.objects.filter(budget=category.budget, owner=base_user)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == category.id

    @pytest.mark.parametrize('is_active', (True, False))
    def test_get_categories_list_filtered_by_is_active(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
        is_active: bool,
    ):
        """
        GIVEN: Two IncomeCategory objects for single Budget.
        WHEN: The IncomeCategoryViewSet list view is called with is_active filter.
        THEN: Response must contain all IncomeCategory existing in database assigned to Budget matching given
        is_active value.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget, is_active=is_active)
        income_category_factory(budget=budget, is_active=not is_active)
        api_client.force_authenticate(base_user)

        response = api_client.get(income_category_url(budget.id), data={'is_active': is_active})

        assert response.status_code == status.HTTP_200_OK
        assert IncomeCategory.objects.all().count() == 2
        categories = IncomeCategory.objects.filter(budget=category.budget, is_active=is_active)
        serializer = IncomeCategorySerializer(categories, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == categories.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == category.id


@pytest.mark.django_db
class TestIncomeCategoryApiCreate:
    """Tests for create IncomeCategory on IncomeCategoryViewSet."""

    PAYLOAD = {
        'name': 'Salary',
        'group': IncomeCategory.IncomeGroups.REGULAR,
        'description': 'Monthly salary.',
        'is_active': True,
    }

    @pytest.mark.parametrize('user_type', ['owner', 'member'])
    def test_create_single_category(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        user_type: str,
    ):
        """
        GIVEN: Budget instances created in database. Valid payload prepared
        for IncomeCategory.
        WHEN: IncomeCategoryViewSet called with POST by User belonging to Budget with valid payload.
        THEN: IncomeCategory object created in database with given payload
        """
        other_user = user_factory()
        if user_type == 'owner':
            budget = budget_factory(owner=base_user, members=[other_user])
        else:
            budget = budget_factory(members=[base_user, other_user])
        api_client.force_authenticate(base_user)

        response = api_client.post(income_category_url(budget.id), self.PAYLOAD)

        assert response.status_code == status.HTTP_201_CREATED
        assert IncomeCategory.objects.filter(budget=budget).count() == 1
        category = IncomeCategory.objects.get(id=response.data['id'])
        for key in self.PAYLOAD:
            assert getattr(category, key) == self.PAYLOAD[key]
        serializer = IncomeCategorySerializer(category)
        assert response.data == serializer.data

    def test_create_category_with_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instances created in database. Valid payload with owner prepared
        for IncomeCategory.
        WHEN: IncomeCategoryViewSet called with POST by User belonging to Budget with valid payload.
        THEN: IncomeCategory object created in database with given payload
        """
        budget = budget_factory(owner=base_user)
        payload = self.PAYLOAD.copy()
        payload['owner'] = base_user.id
        api_client.force_authenticate(base_user)

        response = api_client.post(income_category_url(budget.id), payload)

        assert response.status_code == status.HTTP_201_CREATED
        category = IncomeCategory.objects.get(id=response.data['id'])
        assert category.owner == base_user
        assert base_user.personal_income_categories.filter(budget=budget).count() == 1
        serializer = IncomeCategorySerializer(category)
        assert response.data == serializer.data

    def test_create_two_categories_for_single_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instances created in database. Valid payloads prepared
        for two ExpenseCategories.
        WHEN: IncomeCategoryViewSet called twice with POST by User belonging to Budget with valid payloads.
        THEN: Two IncomeCategory objects created in database with given payloads.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        payload_1 = self.PAYLOAD.copy()
        payload_1['name'] = 'IncomeCategory name 1'
        payload_2 = self.PAYLOAD.copy()
        payload_2['name'] = 'IncomeCategory name 2'

        response_1 = api_client.post(income_category_url(budget.id), payload_1)
        response_2 = api_client.post(income_category_url(budget.id), payload_2)

        assert response_1.status_code == status.HTTP_201_CREATED
        assert response_2.status_code == status.HTTP_201_CREATED
        assert IncomeCategory.objects.filter(budget=budget).count() == 2
        for response, payload in [(response_1, payload_1), (response_2, payload_2)]:
            category = IncomeCategory.objects.get(id=response.data['id'])
            for key in payload:
                assert getattr(category, key) == payload[key]

    def test_create_same_category_for_two_budgets(self, api_client: APIClient, budget_factory: FactoryMetaClass):
        """
        GIVEN: Two Budget instances created in database. Valid payload prepared for two ExpenseCategories.
        WHEN: IncomeCategoryViewSet called twice with POST by different Users belonging to two different
        Budgets with valid payload.
        THEN: Two IncomeCategory objects created in database with given payload for separate Budgets.
        """
        payload = self.PAYLOAD.copy()
        budget_1 = budget_factory()
        budget_2 = budget_factory()

        api_client.force_authenticate(budget_1.owner)
        api_client.post(income_category_url(budget_1.id), payload)
        api_client.force_authenticate(budget_2.owner)
        api_client.post(income_category_url(budget_2.id), payload)

        assert IncomeCategory.objects.all().count() == 2
        assert IncomeCategory.objects.filter(budget=budget_1).count() == 1
        assert IncomeCategory.objects.filter(budget=budget_2).count() == 1

    @pytest.mark.parametrize('field_name', ['name', 'description'])
    def test_error_value_too_long(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        field_name: str,
    ):
        """
        GIVEN: Budget instance created in database. Payload for IncomeCategory with field value too long.
        WHEN: IncomeCategoryViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not created in database.
        """
        budget = budget_factory(owner=base_user)
        api_client.force_authenticate(base_user)
        max_length = IncomeCategory._meta.get_field(field_name).max_length
        payload = self.PAYLOAD.copy()
        payload[field_name] = (max_length + 1) * 'a'

        response = api_client.post(income_category_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert field_name in response.data['detail']
        assert response.data['detail'][field_name][0] == f'Ensure this field has no more than {max_length} characters.'
        assert not IncomeCategory.objects.filter(budget=budget).exists()

    def test_error_create_category_for_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. Valid payload for IncomeCategory.
        WHEN: IncomeCategoryViewSet called with POST by User not belonging to Budget with valid payload.
        THEN: Forbidden HTTP 403 returned. Object not created.
        """
        budget = budget_factory()
        payload = self.PAYLOAD.copy()
        api_client.force_authenticate(base_user)

        response = api_client.post(income_category_url(budget.id), payload)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
        assert not IncomeCategory.objects.filter(budget=budget).exists()

    def test_error_owner_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as
        'owner' in payload.
        WHEN: IncomeCategoryViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. No IncomeCategory created in database.
        """
        budget = budget_factory(owner=base_user)
        outer_user = user_factory()
        payload = self.PAYLOAD.copy()

        payload['owner'] = outer_user.id
        api_client.force_authenticate(base_user)

        api_client.post(income_category_url(budget.id), payload)
        response = api_client.post(income_category_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert response.data['detail']['non_field_errors'][0] == 'Provided owner does not belong to Budget.'
        assert not IncomeCategory.objects.filter(budget=budget).exists()

    def test_error_personal_category_name_already_used(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance with owner created in database. Name of existing personal IncomeCategory
        and owner of existing IncomeCategory in payload.
        WHEN: IncomeCategoryViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. No IncomeCategory created in database.
        """
        budget = budget_factory(owner=base_user)
        payload = self.PAYLOAD.copy()
        payload['owner'] = base_user.id
        api_client.force_authenticate(base_user)
        api_client.post(income_category_url(budget.id), payload)

        response = api_client.post(income_category_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Personal IncomeCategory with given name already exists in Budget for provided owner.'
        )
        assert IncomeCategory.objects.filter(budget=budget, owner__isnull=False).count() == 1

    def test_error_common_category_name_already_used(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance with owner created in database. Name of existing common
        IncomeCategory in payload.
        WHEN: IncomeCategoryViewSet called with POST by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. No IncomeCategory created in database.
        """
        budget = budget_factory(owner=base_user)
        payload = self.PAYLOAD.copy()
        api_client.force_authenticate(base_user)
        api_client.post(income_category_url(budget.id), payload)

        response = api_client.post(income_category_url(budget.id), payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Common IncomeCategory with given name already exists in Budget.'
        )
        assert IncomeCategory.objects.filter(budget=budget, owner__isnull=True).count() == 1


@pytest.mark.django_db
class TestIncomeCategoryApiDetail:
    """Tests for detail view on IncomeCategoryViewSet."""

    @pytest.mark.parametrize('user_type', ['owner', 'member'])
    def test_get_category_details(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
        user_type: str,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called by User belonging to Budget.
        THEN: HTTP 200, IncomeCategory details returned.
        """
        if user_type == 'owner':
            budget = budget_factory(owner=base_user)
        else:
            budget = budget_factory(members=[base_user])
        category = income_category_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(budget.id, category.id)

        response = api_client.get(url)
        serializer = IncomeCategorySerializer(category)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_error_get_category_details_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, income_category_factory: FactoryMetaClass
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called without authentication.
        THEN: Unauthorized HTTP 401.
        """
        category = income_category_factory()
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_get_details_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        category = income_category_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)

        url = income_category_detail_url(category.budget.id, category.id)
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'


@pytest.mark.django_db
class TestIncomeCategoryApiPartialUpdate:
    """Tests for partial update view on IncomeCategoryViewSet."""

    PAYLOAD = {
        'name': 'Salary',
        'group': IncomeCategory.IncomeGroups.REGULAR,
        'description': 'Monthly salary.',
        'is_active': True,
    }

    @pytest.mark.parametrize(
        'param, value',
        [
            ('name', 'New name'),
            ('group', IncomeCategory.IncomeGroups.IRREGULAR),
            ('description', 'New description'),
            ('is_active', False),
        ],
    )
    @pytest.mark.django_db
    def test_category_partial_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
        param: str,
        value: Any,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with PATCH by User belonging to Budget.
        THEN: HTTP 200, IncomeCategory updated.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget, owner=None, **self.PAYLOAD)
        update_payload = {param: value}
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(budget.id, category.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert getattr(category, param) == update_payload[param]
        assert category.owner is None

    def test_category_partial_update_owner(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database. Update payload with "owner" value prepared.
        WHEN: IncomeCategorySet detail view called with PATCH by User belonging to Budget with valid payload.
        THEN: HTTP 200, Deposit updated with "owner" value.
        """
        member = user_factory()
        budget = budget_factory(owner=base_user, members=[member])
        category = income_category_factory(budget=budget, owner=None, **self.PAYLOAD)
        update_payload = {'owner': member.id}
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(budget.id, category.id)

        response = api_client.patch(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.owner == member

    def test_error_partial_update_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, income_category_factory: FactoryMetaClass
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with PATCH without authentication.
        THEN: Unauthorized HTTP 401.
        """
        category = income_category_factory()
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.patch(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_partial_update_category_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with PATCH by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        category = income_category_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.patch(url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    def test_error_partial_update_owner_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as
        'owner' in payload.
        WHEN: IncomeCategoryViewSet called with PATCH by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not updated.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget)
        payload = {'owner': user_factory().id}
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert response.data['detail']['non_field_errors'][0] == 'Provided owner does not belong to Budget.'

    def test_error_partial_update_personal_category_name_already_used(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance with owner created in database. Name of existing personal IncomeCategory
        in payload.
        WHEN: IncomeCategoryViewSet called with PATCH by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not updated.
        """
        budget = budget_factory(owner=base_user)
        income_category_factory(budget=budget, owner=base_user, **self.PAYLOAD)
        category = income_category_factory(budget=budget, owner=base_user)
        payload = {'name': self.PAYLOAD['name']}
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Personal IncomeCategory with given name already exists in Budget for provided owner.'
        )

    def test_error_partial_update_common_category_name_already_used(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance with owner created in database. Name of existing personal IncomeCategory
        and owner of existing IncomeCategory in payload.
        WHEN: IncomeCategoryViewSet called with PATCH by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not updated.
        """
        budget = budget_factory(owner=base_user)
        income_category_factory(budget=budget, owner=None, **self.PAYLOAD)
        category = income_category_factory(budget=budget, owner=None)
        payload = {'name': self.PAYLOAD['name']}
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.patch(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Common IncomeCategory with given name already exists in Budget.'
        )


@pytest.mark.django_db
class TestIncomeCategoryApiFullUpdate:
    """Tests for full update view on IncomeCategoryViewSet."""

    INITIAL_PAYLOAD = {
        'name': 'Salary',
        'group': IncomeCategory.IncomeGroups.REGULAR,
        'description': 'Monthly salary.',
        'is_active': True,
    }

    UPDATE_PAYLOAD = {
        'name': 'Additional',
        'group': IncomeCategory.IncomeGroups.IRREGULAR,
        'description': 'Extra cash.',
        'is_active': False,
    }

    @pytest.mark.django_db
    def test_category_full_update(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with PUT by User belonging to Budget.
        THEN: HTTP 200, IncomeCategory updated.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget, owner=None, **self.INITIAL_PAYLOAD)
        update_payload = self.UPDATE_PAYLOAD.copy()
        update_payload['owner'] = base_user.id
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(budget.id, category.id)

        response = api_client.put(url, update_payload)

        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        for param in update_payload:
            if param == 'owner':
                assert getattr(category, param) == base_user
                continue
            assert getattr(category, param) == update_payload[param]

    def test_error_full_update_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, income_category_factory: FactoryMetaClass
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with PUT without authentication.
        THEN: Unauthorized HTTP 401.
        """
        category = income_category_factory()
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_full_update_category_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with PUT by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        category = income_category_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.put(url, {})

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'

    def test_error_full_update_owner_does_not_belong_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        user_factory: FactoryMetaClass,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Budget instance created in database. User not belonging to Budget as
        'owner' in payload.
        WHEN: IncomeCategoryViewSet called with PUT by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not updated.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget)
        payload = self.UPDATE_PAYLOAD.copy()
        payload['owner'] = user_factory().id
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.put(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert response.data['detail']['non_field_errors'][0] == 'Provided owner does not belong to Budget.'

    def test_error_full_update_personal_category_name_already_used(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance with owner created in database. Name of existing personal IncomeCategory
        in payload.
        WHEN: IncomeCategoryViewSet called with PUT by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not updated.
        """
        budget = budget_factory(owner=base_user)
        income_category_factory(budget=budget, owner=base_user, **self.INITIAL_PAYLOAD)
        category = income_category_factory(budget=budget, owner=base_user)
        payload = self.UPDATE_PAYLOAD.copy()
        payload['name'] = self.INITIAL_PAYLOAD['name']
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.put(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Personal IncomeCategory with given name already exists in Budget for provided owner.'
        )

    def test_error_full_update_common_category_name_already_used(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance with owner created in database. Name of existing personal IncomeCategory
        and owner of existing IncomeCategory in payload.
        WHEN: IncomeCategoryViewSet called with PUT by User belonging to Budget with invalid payload.
        THEN: Bad request HTTP 400 returned. IncomeCategory not updated.
        """
        budget = budget_factory(owner=base_user)
        income_category_factory(budget=budget, owner=None, **self.INITIAL_PAYLOAD)
        category = income_category_factory(budget=budget, owner=None)
        payload = self.UPDATE_PAYLOAD.copy()
        payload['name'] = self.INITIAL_PAYLOAD['name']
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.put(url, payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data['detail']
        assert (
            response.data['detail']['non_field_errors'][0]
            == 'Common IncomeCategory with given name already exists in Budget.'
        )


@pytest.mark.django_db
class TestIncomeCategoryApiDelete:
    """Tests for delete IncomeCategory on IncomeCategoryViewSet."""

    def test_delete_category(
        self,
        api_client: APIClient,
        base_user: Any,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with DELETE by User belonging to Budget.
        THEN: No content HTTP 204, IncomeCategory deleted.
        """
        budget = budget_factory(owner=base_user)
        category = income_category_factory(budget=budget)
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(budget.id, category.id)

        assert IncomeCategory.objects.filter(budget=budget).count() == 1

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not IncomeCategory.objects.filter(budget=budget).exists()

    def test_error_delete_unauthenticated(
        self, api_client: APIClient, base_user: AbstractUser, income_category_factory: FactoryMetaClass
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with DELETE without authentication.
        THEN: Unauthorized HTTP 401.
        """
        category = income_category_factory()
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_error_delete_category_from_not_accessible_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        income_category_factory: FactoryMetaClass,
    ):
        """
        GIVEN: IncomeCategory instance for Budget created in database.
        WHEN: IncomeCategoryViewSet detail view called with DELETE by User not belonging to Budget.
        THEN: Forbidden HTTP 403 returned.
        """
        category = income_category_factory(budget=budget_factory())
        api_client.force_authenticate(base_user)
        url = income_category_detail_url(category.budget.id, category.id)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'User does not have access to Budget.'
