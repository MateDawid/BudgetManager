import factory
from budgets_tests.factories import BudgetFactory


class EntityFactory(factory.django.DjangoModelFactory):
    """Factory for Entity model."""

    class Meta:
        model = 'entities.Entity'

    budget = factory.SubFactory(BudgetFactory)
    name = factory.Faker('text', max_nb_chars=128)
    description = factory.Faker('text', max_nb_chars=255)
    is_active = factory.Faker('boolean')
    is_deposit = factory.LazyAttribute(lambda _: False)


class DepositFactory(EntityFactory):
    """Factory for Deposit model."""

    is_deposit = factory.LazyAttribute(lambda _: True)

    class Meta:
        model = 'entities.Deposit'
