from categories.filters.expense_category_filterset import ExpenseCategoryFilterSet
from categories.models.expense_category_model import ExpenseCategory
from categories.serializers.expense_category_serializer import ExpenseCategorySerializer
from categories.views.transfer_category_viewset import TransferCategoryViewSet


class ExpenseCategoryViewSet(TransferCategoryViewSet):
    """View for managing ExpenseCategories."""

    serializer_class = ExpenseCategorySerializer
    queryset = ExpenseCategory.objects.all()
    filterset_class = ExpenseCategoryFilterSet
