from django.db import models
from entities.managers import DepositManager


class Entity(models.Model):
    """Entity model for Transfer actor (payer or receiver) representation."""

    budget = models.ForeignKey(
        'budgets.Budget', on_delete=models.CASCADE, related_name='entities', null=False, blank=False
    )
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_deposit = models.BooleanField(default=False)

    objects = models.Manager()
    deposits = DepositManager()

    class Meta:
        verbose_name_plural = 'entities'
        unique_together = (
            'name',
            'budget',
        )

    def __str__(self):
        return f'{self.name} ({self.budget.name})'
