import pytest
from django.contrib.auth.models import AbstractUser
from factory.base import FactoryMetaClass
from predictions.models import ExpensePrediction
from predictions.serializers import ExpensePredictionSerializer
from predictions_tests.api.urls import expense_prediction_url
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestExpensePredictionApiList:
    """Tests for list view on ExpensePredictionViewSet."""

    def test_retrieve_prediction_list_by_budget_member(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two ExpensePrediction model instances for single Budget created in database.
        WHEN: ExpensePredictionViewSet called by Budget member.
        THEN: Response with serialized Budget ExpensePrediction list returned.
        """
        api_client.force_authenticate(base_user)
        budget = budget_factory(owner=base_user)
        for _ in range(2):
            expense_prediction_factory(budget=budget)

        response = api_client.get(expense_prediction_url(budget.id))

        predictions = ExpensePrediction.objects.filter(period__budget=budget)
        serializer = ExpensePredictionSerializer(predictions, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == serializer.data

    def test_prediction_list_limited_to_budget(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two ExpensePrediction model instances for different Budgets created in database.
        WHEN: ExpensePredictionViewSet called by one of Budgets owner.
        THEN: Response with serialized ExpensePrediction list (only from given Budget) returned.
        """
        budget = budget_factory(owner=base_user)
        prediction = expense_prediction_factory(budget=budget)
        expense_prediction_factory()
        api_client.force_authenticate(base_user)

        response = api_client.get(expense_prediction_url(budget.id))

        predictions = ExpensePrediction.objects.filter(period__budget=budget)
        serializer = ExpensePredictionSerializer(predictions, many=True)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == len(serializer.data) == predictions.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == prediction.id

    @pytest.mark.parametrize(
        'sort_param',
        (
            'id',
            '-id',
            'period',
            '-period',
            'category',
            '-category',
            'period__name',
            '-period__name',
            'category__name',
            '-category__name',
        ),
    )
    def test_get_predictions_list_sorted_by_param(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
        sort_param: str,
    ):
        """
        GIVEN: Three ExpensePrediction objects created in database.
        WHEN: The ExpensePredictionViewSet list view is called with sorting by given param and without any filters.
        THEN: Response must contain all ExpensePrediction existing in database sorted by given param.
        """
        budget = budget_factory(owner=base_user)
        for _ in range(5):
            expense_prediction_factory(budget=budget)
        api_client.force_authenticate(base_user)

        response = api_client.get(expense_prediction_url(budget.id), data={'ordering': sort_param})

        assert response.status_code == status.HTTP_200_OK
        predictions = ExpensePrediction.objects.all().order_by(sort_param)
        serializer = ExpensePredictionSerializer(predictions, many=True)
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == len(predictions) == 5
        assert response.data['results'] == serializer.data

    def test_get_predictions_list_filtered_by_period_id(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two ExpensePrediction objects for single Budget.
        WHEN: The ExpensePredictionViewSet list view is called with period_id filter.
        THEN: Response must contain all ExpensePrediction existing in database assigned to Budget matching given
        period_id value.
        """
        budget = budget_factory(owner=base_user)
        period = budgeting_period_factory(budget=budget, name='Test name')
        prediction = expense_prediction_factory(budget=budget, period=period)
        expense_prediction_factory(budget=budget, period=budgeting_period_factory(budget=budget, name='Other period'))
        api_client.force_authenticate(base_user)

        response = api_client.get(expense_prediction_url(budget.id), data={'period_id': period.id})

        assert response.status_code == status.HTTP_200_OK
        assert ExpensePrediction.objects.all().count() == 2
        predictions = ExpensePrediction.objects.filter(period__budget=budget, period__id=period.id)
        serializer = ExpensePredictionSerializer(
            predictions,
            many=True,
        )
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == predictions.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == prediction.id

    @pytest.mark.parametrize(
        'filter_value', ('Test', 'TEST', 'test', 'name', 'NAME', 'Name', 'Test name', 'TEST NAME', 'test name')
    )
    def test_get_predictions_list_filtered_by_period_name(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        budgeting_period_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
        filter_value: str,
    ):
        """
        GIVEN: Two ExpensePrediction objects for single Budget.
        WHEN: The ExpensePredictionViewSet list view is called with period_name filter.
        THEN: Response must contain all ExpensePrediction existing in database assigned to Budget matching given
        period_name value.
        """
        budget = budget_factory(owner=base_user)
        period = budgeting_period_factory(budget=budget, name='Test name')
        prediction = expense_prediction_factory(budget=budget, period=period)
        expense_prediction_factory(budget=budget, period=budgeting_period_factory(budget=budget, name='Other'))
        api_client.force_authenticate(base_user)

        response = api_client.get(expense_prediction_url(budget.id), data={'period_name': filter_value})

        assert response.status_code == status.HTTP_200_OK
        assert ExpensePrediction.objects.all().count() == 2
        predictions = ExpensePrediction.objects.filter(period__budget=budget, period__name__icontains=filter_value)
        serializer = ExpensePredictionSerializer(
            predictions,
            many=True,
        )
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == predictions.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == prediction.id

    def test_get_predictions_list_filtered_by_category_id(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
    ):
        """
        GIVEN: Two ExpensePrediction objects for single Budget.
        WHEN: The ExpensePredictionViewSet list view is called with category_id filter.
        THEN: Response must contain all ExpensePrediction existing in database assigned to Budget matching given
        category_id value.
        """
        budget = budget_factory(owner=base_user)
        category = expense_category_factory(budget=budget, name='Test name')
        prediction = expense_prediction_factory(budget=budget, category=category)
        expense_prediction_factory(budget=budget, category=expense_category_factory(budget=budget, name='Other'))
        api_client.force_authenticate(base_user)

        response = api_client.get(expense_prediction_url(budget.id), data={'category_id': category.id})

        assert response.status_code == status.HTTP_200_OK
        assert ExpensePrediction.objects.all().count() == 2
        predictions = ExpensePrediction.objects.filter(period__budget=budget, category__id=category.id)
        serializer = ExpensePredictionSerializer(
            predictions,
            many=True,
        )
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == predictions.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == prediction.id

    @pytest.mark.parametrize(
        'filter_value', ('Test', 'TEST', 'test', 'name', 'NAME', 'Name', 'Test name', 'TEST NAME', 'test name')
    )
    def test_get_predictions_list_filtered_by_category_name(
        self,
        api_client: APIClient,
        base_user: AbstractUser,
        budget_factory: FactoryMetaClass,
        expense_category_factory: FactoryMetaClass,
        expense_prediction_factory: FactoryMetaClass,
        filter_value: str,
    ):
        """
        GIVEN: Two ExpensePrediction objects for single Budget.
        WHEN: The ExpensePredictionViewSet list view is called with category_name filter.
        THEN: Response must contain all ExpensePrediction existing in database assigned to Budget matching given
        category_name value.
        """
        budget = budget_factory(owner=base_user)
        category = expense_category_factory(budget=budget, name='Test name')
        prediction = expense_prediction_factory(budget=budget, category=category)
        expense_prediction_factory(budget=budget, category=expense_category_factory(budget=budget, name='Other'))
        api_client.force_authenticate(base_user)

        response = api_client.get(expense_prediction_url(budget.id), data={'category_name': filter_value})

        assert response.status_code == status.HTTP_200_OK
        assert ExpensePrediction.objects.all().count() == 2
        predictions = ExpensePrediction.objects.filter(category__budget=budget, category__name__icontains=filter_value)
        serializer = ExpensePredictionSerializer(
            predictions,
            many=True,
        )
        assert response.data['results'] and serializer.data
        assert len(response.data['results']) == len(serializer.data) == predictions.count() == 1
        assert response.data['results'] == serializer.data
        assert response.data['results'][0]['id'] == prediction.id
