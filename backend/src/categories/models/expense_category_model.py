from django.conf import settings
from django.db import models


class ExpenseCategory(models.Model):
    """ExpenseCategory model for grouping Income model instances."""

    class ExpenseGroups(models.IntegerChoices):
        """Choices for group value."""

        MOST_IMPORTANT = 1, 'Most important'
        DEBTS = 2, 'Debts'
        SAVINGS = 3, 'Savings'
        OTHERS = 4, 'Others'

    budget = models.ForeignKey('budgets.Budget', on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='personal_expense_categories',
    )
    is_active = models.BooleanField(default=True)
    group = models.PositiveSmallIntegerField(choices=ExpenseGroups.choices, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'expense categories'

    def __str__(self) -> str:
        """
        Returns string representation of ExpenseCategory model instance.

        Returns:
            str: Custom string representation of instance.
        """
        return f'{self.name} ({self.budget.name})'
