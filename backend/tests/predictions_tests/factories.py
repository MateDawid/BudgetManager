import factory
from budgets.models import Budget, BudgetingPeriod
from budgets_tests.factories import BudgetFactory, BudgetingPeriodFactory
from categories.models import ExpenseCategory
from categories_tests.factories import ExpenseCategoryFactory


class ExpensePredictionFactory(factory.django.DjangoModelFactory):
    """Factory for ExpensePrediction model."""

    class Meta:
        model = 'predictions.ExpensePrediction'

    value = factory.Faker('pyint', min_value=0, max_value=99999999)
    description = factory.Faker('text', max_nb_chars=255)

    @factory.lazy_attribute
    def period(self, *args) -> ExpenseCategory:
        """
        Returns ExpenseCategory with the same Budget as prediction period.

        Returns:
            ExpenseCategory: ExpenseCategory with the same Budget as period.
        """
        budget = self._Resolver__step.builder.extras.get('budget')
        if not budget:
            budget = BudgetFactory()
        return BudgetingPeriodFactory(budget=budget)

    @factory.lazy_attribute
    def category(self, *args) -> BudgetingPeriod:
        """
        Returns BudgetingPeriod with the same Budget as prediction category.

        Returns:
            BudgetingPeriod: BudgetingPeriod with the same Budget as category.
        """
        budget = self._Resolver__step.builder.extras.get('budget')
        if not budget:
            budget = self.period.budget
        return ExpenseCategoryFactory(budget=budget)

    @factory.post_generation
    def budget(self, create: bool, budget: Budget, **kwargs) -> None:
        """
        Enables to pass "budget" as parameter to factory.

        Args:
            create [bool]: Indicates if object is created or updated.
            budget [Budget]: Budget model instance.
            **kwargs [dict]: Keyword arguments
        """
        pass
