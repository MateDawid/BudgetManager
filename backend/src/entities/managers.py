from django.db import models
from django.db.models import Model, QuerySet


class DepositManager(models.Manager):
    """Manager for Deposit Entities."""

    def get_queryset(self) -> QuerySet:
        """
        Filters out Entities not being Deposits.

        Returns:
            QuerySet: QuerySet containing only Entities with is_deposit=True.
        """
        return super().get_queryset().filter(is_deposit=True)

    def create(self, *args, **kwargs) -> Model:
        """
        Sets is_deposit param to True on object creation.

        Returns:
            Model: Deposit model instance.
        """
        kwargs['is_deposit'] = True
        return super().create(*args, **kwargs)

    def update(self, *args, **kwargs) -> int:
        """
        Sets is_deposit param to True on objects update.

        Returns:
            int: Number of affected database rows.
        """
        kwargs['is_deposit'] = True
        return super().update(**kwargs)
