from django.contrib import admin
from entities.models.deposit_model import Deposit
from entities.models.entity_model import Entity


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    """Custom admin view for Deposit model."""

    list_display = ('name', 'budget', 'description', 'is_active', 'is_deposit')
    list_filter = ('budget__name', 'budget__owner__email', 'is_active')


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    """Custom admin view for Deposit model."""

    list_display = ('name', 'budget', 'description', 'is_active')
    list_filter = ('budget__name', 'budget__owner__email', 'is_active')
