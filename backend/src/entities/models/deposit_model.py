from entities.managers import DepositManager
from entities.models.entity_model import Entity


class Deposit(Entity):
    """Deposit proxy model for Entity owned by Budget member representation."""

    objects = DepositManager()

    class Meta:
        proxy = True
        verbose_name_plural = 'deposits'

    def save(self, *args, **kwargs) -> None:
        """
        Overridden save method to make sure, that is_deposit is always True.
        """
        self.is_deposit = True
        super().save(*args, **kwargs)
