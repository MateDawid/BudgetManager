from django.conf import settings
from django.db import models


class IncomeCategory(models.Model):
    """IncomeCategory model for grouping Income model instances."""

    class IncomeGroups(models.IntegerChoices):
        """Choices for group value."""

        REGULAR = 1, 'Regular'
        IRREGULAR = 2, 'Irregular'

    budget = models.ForeignKey('budgets.Budget', on_delete=models.CASCADE, related_name='income_categories')
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='personal_income_categories',
    )
    is_active = models.BooleanField(default=True)
    group = models.PositiveSmallIntegerField(choices=IncomeGroups.choices, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'income categories'

    def __str__(self) -> str:
        """
        Returns string representation of IncomeCategory model instance.

        Returns:
            str: Custom string representation of instance.
        """
        return f'{self.name} ({self.budget.name})'
