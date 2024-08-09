import random

import factory.fuzzy
from app_users_tests.factories import UserFactory
from budgets_tests.factories import BudgetFactory
from categories.models import ExpenseCategory, IncomeCategory


class IncomeCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for IncomeCategory model."""

    class Meta:
        model = 'categories.IncomeCategory'

    budget = factory.SubFactory(BudgetFactory)
    name = factory.Faker('text', max_nb_chars=128)
    description = factory.Faker('text', max_nb_chars=255)
    is_active = factory.Faker('boolean')
    group = factory.fuzzy.FuzzyChoice([x[0] for x in IncomeCategory.IncomeGroups.choices])

    @factory.lazy_attribute
    def owner(self) -> str:
        """Generates user field value - User model instance or None."""
        options = [UserFactory(), None]
        return random.choice(options)


class ExpenseCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for ExpenseCategory model."""

    class Meta:
        model = 'categories.ExpenseCategory'

    budget = factory.SubFactory(BudgetFactory)
    name = factory.Faker('text', max_nb_chars=128)
    description = factory.Faker('text', max_nb_chars=255)
    is_active = factory.Faker('boolean')
    group = factory.fuzzy.FuzzyChoice([x[0] for x in ExpenseCategory.ExpenseGroups.choices])

    @factory.lazy_attribute
    def owner(self) -> str:
        """Generates user field value - User model instance or None."""
        options = [UserFactory(), None]
        return random.choice(options)
