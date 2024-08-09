import pytest
from budgets.models.budget_model import Budget
from django.contrib.auth.models import AbstractUser
from django.db import DataError, IntegrityError
from factory.base import FactoryMetaClass


@pytest.mark.django_db
class TestBudgetModel:
    """Tests for Budget model"""

    def test_create_object(self, user_factory: FactoryMetaClass):
        """
        GIVEN: User model instance in database.
        WHEN: Budget instance create attempt with valid data.
        THEN: Budget model instance exists in database with given data.
        """
        owner = user_factory()
        members = [user_factory() for _ in range(3)]
        payload = {
            'name': 'Home budget',
            'description': 'Budget with home expenses and incomes',
            'owner': owner,
            'currency': 'PLN',
        }
        budget = Budget.objects.create(**payload)
        budget.members.add(*members)
        for param, value in payload.items():
            assert getattr(budget, param) == value
        assert budget.members.all().count() == 4
        assert str(budget) == f'{budget.name} ({budget.owner.email})'

    def test_owner_in_members(self, user_factory: FactoryMetaClass):
        """
        GIVEN: User model instance in database.
        WHEN: Budget instance create attempt without owner in members list.
        THEN: Budget model instance exists in database with owner in members list.
        """
        owner = user_factory()
        members = [user_factory() for _ in range(3)]
        payload = {
            'name': 'Home budget',
            'description': 'Budget with home expenses and incomes',
            'owner': owner,
            'currency': 'PLN',
        }
        budget = Budget.objects.create(**payload)
        budget.members.add(*members)
        budget.members.add(owner)
        budget.save()

        assert owner in budget.members.all()
        assert budget.members.all().count() == len(members) + 1

    def test_creating_same_object_by_two_users(self, user_factory: FactoryMetaClass):
        """
        GIVEN: Two User model instances in database.
        WHEN: Two Budget instances create attempt with valid data - both for different Users as owners.
        THEN: Two Budget model instances exists in database with given data.
        """
        users = [user_factory(), user_factory()]
        payload = {'name': 'Home budget', 'description': 'Budget with home expenses and incomes', 'currency': 'PLN'}
        for user in users:
            payload['owner'] = user
            Budget.objects.create(**payload)

        assert Budget.objects.all().count() == 2
        for user in users:
            assert Budget.objects.filter(owner=user).count() == 1

    @pytest.mark.django_db(transaction=True)
    def test_error_name_too_long(self, user: AbstractUser):
        """
        GIVEN: User model instance in database.
        WHEN: Budget instance create attempt with name too long.
        THEN: DataError raised. Object not created in database.
        """
        max_length = Budget._meta.get_field('name').max_length
        payload = {
            'name': (max_length + 1) * 'a',
            'description': 'Budget with home expenses and incomes',
            'owner': user,
            'currency': 'PLN',
        }

        with pytest.raises(DataError) as exc:
            Budget.objects.create(**payload)
        assert str(exc.value) == f'value too long for type character varying({max_length})\n'
        assert not Budget.objects.filter(owner=user).exists()

    @pytest.mark.django_db(transaction=True)
    def test_error_name_already_used(self, user: AbstractUser):
        """
        GIVEN: Budget object instance with User as owner in database.
        WHEN: Budget instance create attempt with name already used for User's Budget..
        THEN: IntegrityError raised. Object not created in database.
        """
        payload = {
            'name': 'Home budget',
            'description': 'Budget with home expenses and incomes',
            'owner': user,
            'currency': 'PLN',
        }
        Budget.objects.create(**payload)

        with pytest.raises(IntegrityError) as exc:
            Budget.objects.create(**payload)

        assert f'DETAIL:  Key (name, owner_id)=({payload["name"]}, {user.id}) already exists.' in str(exc.value)
        assert Budget.objects.filter(owner=user).count() == 1

    @pytest.mark.django_db(transaction=True)
    def test_error_currency_too_long(self, user: AbstractUser):
        """
        GIVEN: User model instance in database.
        WHEN: Budget instance create attempt with currency too long.
        THEN: DataError raised. Object not created in database.
        """
        max_length = Budget._meta.get_field('currency').max_length
        payload = {
            'name': 'Home budget',
            'description': 'Budget with home expenses and incomes',
            'owner': user,
            'currency': (max_length + 100) * 'a',
        }
        with pytest.raises(DataError) as exc:
            Budget.objects.create(**payload)
        assert str(exc.value) == f'value too long for type character varying({max_length})\n'
        assert not Budget.objects.filter(owner=user).exists()
