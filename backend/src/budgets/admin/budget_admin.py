from budgets.models.budget_model import Budget
from django.contrib import admin


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Custom admin view for Budget model."""

    list_display = ('name', 'owner')
    list_filter = ('owner__email',)

    def save_related(self, request, form, formsets, change):  # pragma: no cover
        """Override save_related method to remove Budget owner from Budget members on saving model in admin panel."""
        super().save_related(request, form, formsets, change)
        form.instance.members.add(form.instance.owner)
