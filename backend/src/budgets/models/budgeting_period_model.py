from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class BudgetingPeriod(models.Model):
    """Model for period in which Budget data will be calculated and reported."""

    budget = models.ForeignKey('budgets.Budget', on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=128)
    date_start = models.DateField(null=False, blank=False)
    date_end = models.DateField(null=False, blank=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            'name',
            'budget',
        )

    def __str__(self) -> str:
        """
        Method for returning string representation of BudgetingPeriod model instance.

        Returns:
            str: String representation of BudgetingPeriod model instance.
        """
        return f'{self.name} ({self.budget.name})'

    def save(self, *args: list, **kwargs: dict) -> None:
        """
        Overrides .save() method to execute .clean() method before saving model in database.
        """
        self.clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """
        Validates BudgetingPeriod input data before saving in database.
        """
        self.clean_is_active()
        self.clean_dates()

    def clean_is_active(self) -> None:
        """
        Validates is_active field. If is_active not given, passes it to default model validation.

        Raises:
            ValidationError: Raised when is_active=True and another BudgetingPeriod with such flag
            already exists for Budget.
        """
        if self.is_active and self.budget.periods.filter(is_active=True).exclude(pk=self.pk).exists():
            raise ValidationError('is_active: Active period already exists.', code='active-invalid')

    def clean_dates(self) -> None:
        """
        Validates date_start and date_end fields. If date_start or date_end not given, passes them to default
        model validation.

        Raises:
            ValidationError: Raised when date_start and date_end not in logic order or collide with another
            BudgetingPeriod daterange.
        """
        if self.date_start >= self.date_end:
            raise ValidationError('start_date: Start date should be earlier than end date.', code='date-invalid')
        if (
            self.budget.periods.filter(
                Q(date_start__lte=self.date_start, date_end__gte=self.date_start)
                | Q(date_start__lte=self.date_end, date_end__gte=self.date_end)
                | Q(date_start__gte=self.date_start, date_end__lte=self.date_end)
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                'date_start: Period date range collides with other period in Budget.',
                code='period-range-invalid',
            )
