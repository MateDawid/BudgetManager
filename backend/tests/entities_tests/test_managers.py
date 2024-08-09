import pytest
from budgets.models.budget_model import Budget
from entities.models.entity_model import Entity
from entities_tests.factories import EntityFactory
from factory.base import FactoryMetaClass


@pytest.mark.django_db
class TestDepositManager:
    def test_get_queryset(self, budget: Budget, entity_factory: FactoryMetaClass, deposit_factory: FactoryMetaClass):
        """
        GIVEN: Budget and two Entities (with is_deposit=False and is_deposit=True) models instances in database.
        WHEN: Calling DepositManager for get_queryset.
        THEN: Manager returns only object with is_deposit=True.
        """
        entity_factory(budget=budget)
        deposit = deposit_factory(budget=budget)

        qs = Entity.deposits.all()

        assert qs.count() == 1
        assert deposit in qs

    def test_create(self, budget: Budget):
        """
        GIVEN: Budget model instance in database.
        WHEN: Calling DepositManager for create.
        THEN: Manager creates object always with is_deposit set to True.
        """
        payload = {
            'budget': budget,
            'name': 'Test',
            'description': 'Some description',
            'is_deposit': False,  # intentionally set to False
            'is_active': True,
        }

        entity = Entity.deposits.create(**payload)

        assert entity.is_deposit is True
        for param in payload:
            if param == 'is_deposit':
                continue
            assert getattr(entity, param) == payload[param]

    def test_update(self):
        """
        GIVEN: Budget model instance in database.
        WHEN: Calling DepositManager for update.
        THEN: Manager updates object always with is_deposit set to True.
        """
        entity = EntityFactory.create(is_deposit=True)
        assert Entity.deposits.all().count() == 1

        Entity.deposits.update(is_deposit=False)

        entity.refresh_from_db()
        assert Entity.deposits.all().count() == 1
        assert entity.is_deposit is True
