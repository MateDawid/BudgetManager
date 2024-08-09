import pytest
from budgets.models.budget_model import Budget
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError
from entities.models.entity_model import Entity


@pytest.mark.django_db
class TestEntityModel:
    """Tests for Entity model"""

    PAYLOAD: dict = {
        'name': 'Supermarket',
        'description': 'Supermarket in which I buy food.',
        'is_active': True,
        'is_deposit': False,
    }

    def test_save_entity(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Deposit instance save attempt with valid data.
        THEN: Deposit model instance exists in database with given data.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget

        deposit = Entity(**payload)
        deposit.full_clean()
        deposit.save()

        for key in payload:
            assert getattr(deposit, key) == payload[key]
        assert Entity.objects.filter(budget=budget).count() == 1
        assert Entity.deposits.filter(budget=budget).count() == 0
        assert deposit.is_deposit is False
        assert str(deposit) == f'{deposit.name} ({deposit.budget.name})'

    def test_create_entity(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Entity instance create attempt with valid data.
        THEN: Entity model instance exists in database with given data.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget

        entity = Entity.objects.create(**payload)

        for key in payload:
            assert getattr(entity, key) == payload[key]
        assert Entity.objects.filter(budget=budget).count() == 1
        assert Entity.deposits.filter(budget=budget).count() == 0
        assert entity.is_deposit is False
        assert str(entity) == f'{entity.name} ({entity.budget.name})'

    def test_save_deposit(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Entity instance save attempt with valid data and is_deposit=True.
        THEN: Entity model instance exists in database with given data.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        payload['is_deposit'] = True

        entity = Entity(**payload)
        entity.full_clean()
        entity.save()

        for key in payload:
            assert getattr(entity, key) == payload[key]
        assert Entity.objects.filter(budget=budget).count() == 1
        assert Entity.deposits.filter(budget=budget).count() == 1
        assert entity.is_deposit is True
        assert str(entity) == f'{entity.name} ({entity.budget.name})'

    def test_create_deposit(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Entity instance create attempt with valid data and is_deposit=True.
        THEN: Entity model instance exists in database with given data.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        payload['is_deposit'] = True

        entity = Entity.objects.create(**payload)

        for key in payload:
            assert getattr(entity, key) == payload[key]
        assert Entity.objects.filter(budget=budget).count() == 1
        assert Entity.deposits.filter(budget=budget).count() == 1
        assert entity.is_deposit is True
        assert str(entity) == f'{entity.name} ({entity.budget.name})'

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('field_name', ['name', 'description'])
    def test_error_value_too_long(self, budget: Budget, field_name: str):
        """
        GIVEN: Budget model instances in database.
        WHEN: Entity instance for different Budgets create attempt with field value too long.
        THEN: DataError raised.
        """
        max_length = Entity._meta.get_field(field_name).max_length
        payload = self.PAYLOAD.copy()
        payload[field_name] = (max_length + 1) * 'a'

        # .full_clean() & .save() scenario
        with pytest.raises(ValidationError) as exc:
            deposit = Entity(**payload)
            deposit.full_clean()

        assert (
            f'Ensure this value has at most {max_length} characters' in exc.value.error_dict[field_name][0].messages[0]
        )
        assert not Entity.objects.filter(budget=budget).exists()

        # .create() scenario
        with pytest.raises(DataError) as exc:
            Entity.objects.create(**payload)

        assert str(exc.value) == f'value too long for type character varying({max_length})\n'
        assert not Entity.objects.filter(budget=budget).exists()

    @pytest.mark.django_db(transaction=True)
    def test_error_name_already_used(self, budget: Budget):
        """
        GIVEN: Budget model instances in database.
        WHEN: Entity instance for different Budgets create attempt with name already used in particular Budget.
        THEN: DataError raised.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        Entity.objects.create(**payload)

        # .full_clean() & .save() scenario
        with pytest.raises(ValidationError) as exc:
            deposit = Entity(**payload)
            deposit.full_clean()

        assert 'Entity with this Name and Budget already exists.' in exc.value.error_dict['__all__'][0].messages[0]
        assert Entity.objects.filter(budget=budget).count() == 1

        # .create() scenario
        with pytest.raises(IntegrityError) as exc:
            Entity.objects.create(**payload)
        assert f'DETAIL:  Key (name, budget_id)=({payload["name"]}, {budget.id}) already exists.' in str(exc.value)
        assert Entity.objects.filter(budget=budget).count() == 1
