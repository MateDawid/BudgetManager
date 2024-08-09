from django.conf import settings
from django.db import models


class Budget(models.Model):
    """Model for object gathering all data like incomes, expenses and predictions for particular Budget."""

    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True, max_length=300)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_budgets')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='joined_budgets', blank=True)
    currency = models.CharField(max_length=3)

    class Meta:
        unique_together = (
            'name',
            'owner',
        )

    def __str__(self) -> str:
        """
        Method for returning string representation of Budget model instance.

        Returns:
            str: String representation of Budget model instance.
        """
        return f'{self.name} ({self.owner.email})'  # NOQA

    def save(self, *args, **kwargs) -> None:
        """
        Overrides .save() method to add Budget owner to Budget members if not added already.
        """
        super().save(*args, **kwargs)
        self.members.add(self.owner)  # NOQA
