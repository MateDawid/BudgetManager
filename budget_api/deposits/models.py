from django.conf import settings
from django.db import models


class Deposit(models.Model):
    """Deposit model where revenues are collected and from which payments are made."""

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deposits')
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            'name',
            'user',
        )

    def __str__(self) -> str:
        """
        Returns string representation of Deposit model instance.

        Returns:
        str: Custom string representation of instance.
        """
        return f'{self.name} ({self.user.email})'
