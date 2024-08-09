from categories.filters.transfer_category_filterset import TransferCategoryFilterSet
from categories.models.expense_category_model import ExpenseCategory


class ExpenseCategoryFilterSet(TransferCategoryFilterSet):
    """FilterSet for /expense_categories endpoint."""

    class Meta(TransferCategoryFilterSet.Meta):
        model = ExpenseCategory
