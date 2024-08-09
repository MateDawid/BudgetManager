from categories.models.expense_category_model import ExpenseCategory
from django.contrib import admin


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """Custom admin view for ExpenseCategory model."""

    list_display = ('name', 'group', 'budget', 'owner', 'is_active')
    list_filter = ('budget', 'budget__owner__email', 'group')
