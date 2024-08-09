from app_users.managers.user_manager import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    """App User database model."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def is_budget_member(self, budget_id: str) -> bool:
        """
        Method to verify if User is member of Budget with given database ID.

        Args:
            budget_id [str]: Budget database id.

        Returns:
            bool: True if User is member of given Budget, False otherwise.
        """
        return bool(self.joined_budgets.filter(pk=budget_id).values('pk'))  # NOQA
