import pytest
from budgets.models.budget_model import Budget
from django.core.exceptions import ValidationError
from django.db import DataError, IntegrityError
from entities.models.deposit_model import Deposit


@pytest.mark.django_db
class TestDepositModel:
    """Tests for Deposit model"""

    PAYLOAD: dict = {'name': 'Bank account', 'description': 'My own bank account', 'is_active': True}

    def test_save_deposit(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Deposit instance save attempt with valid data.
        THEN: Deposit model instance exists in database with given data.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget

        deposit = Deposit(**payload)
        deposit.full_clean()
        deposit.save()

        for key in payload:
            assert getattr(deposit, key) == payload[key]
        assert Deposit.objects.filter(budget=budget).count() == 1
        assert deposit.is_deposit is True
        assert str(deposit) == f'{deposit.name} ({deposit.budget.name})'

    def test_create_deposit(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Deposit instance create attempt with valid data.
        THEN: Deposit model instance exists in database with given data.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget

        deposit = Deposit.objects.create(**payload)

        for key in payload:
            assert getattr(deposit, key) == payload[key]
        assert Deposit.objects.filter(budget=budget).count() == 1
        assert deposit.is_deposit is True
        assert str(deposit) == f'{deposit.name} ({deposit.budget.name})'

    def test_is_deposit_true_on_deposit_save(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Deposit instance save attempt with is_deposit=False in payload.
        THEN: Deposit model instance exists in database with is_deposit=True.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        payload['is_deposit'] = False

        deposit = Deposit(**payload)
        deposit.full_clean()
        deposit.save()

        assert Deposit.objects.filter(budget=budget).count() == 1
        assert deposit.is_deposit is True

    def test_is_deposit_true_on_deposit_create(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Deposit instance create attempt with is_deposit=False in payload.
        THEN: Deposit model instance exists in database with is_deposit=True.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        payload['is_deposit'] = False

        deposit = Deposit.objects.create(**payload)

        assert Deposit.objects.filter(budget=budget).count() == 1
        assert deposit.is_deposit is True

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('field_name', ['name', 'description'])
    def test_error_value_too_long(self, budget: Budget, field_name: str):
        """
        GIVEN: Budget model instances in database.
        WHEN: Deposit instance for different Budgets create attempt with field value too long.
        THEN: ValidationError on .full_clean() or DataError on .create() raised.
        """
        max_length = Deposit._meta.get_field(field_name).max_length
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        payload[field_name] = (max_length + 1) * 'a'

        # .full_clean() & .save() scenario
        with pytest.raises(ValidationError) as exc:
            deposit = Deposit(**payload)
            deposit.full_clean()

        assert (
            f'Ensure this value has at most {max_length} characters' in exc.value.error_dict[field_name][0].messages[0]
        )
        assert not Deposit.objects.filter(budget=budget).exists()

        # .create() scenario
        with pytest.raises(DataError) as exc:
            Deposit.objects.create(**payload)

        assert str(exc.value) == f'value too long for type character varying({max_length})\n'
        assert not Deposit.objects.filter(budget=budget).exists()

    @pytest.mark.django_db(transaction=True)
    def test_error_name_already_used(self, budget: Budget):
        """
        GIVEN: Budget model instances in database.
        WHEN: Deposit instance for different Budgets create attempt with name already used in particular Budget.
        THEN: ValidationError on .full_clean() or IntegrityError on .create() raised.
        """
        payload = self.PAYLOAD.copy()
        payload['budget'] = budget
        Deposit.objects.create(**payload)

        # .full_clean() & .save() scenario
        with pytest.raises(ValidationError) as exc:
            deposit = Deposit(**payload)
            deposit.full_clean()

        assert 'Entity with this Name and Budget already exists.' in exc.value.error_dict['__all__'][0].messages[0]
        assert Deposit.objects.filter(budget=budget).count() == 1

        # .create() scenario
        with pytest.raises(IntegrityError) as exc:
            Deposit.objects.create(**payload)
        assert f'DETAIL:  Key (name, budget_id)=({payload["name"]}, {budget.id}) already exists.' in str(exc.value)
        assert Deposit.objects.filter(budget=budget).count() == 1
