from categories.filters.transfer_category_filterset import TransferCategoryFilterSet
from categories.models.income_category_model import IncomeCategory


class IncomeCategoryFilterSet(TransferCategoryFilterSet):
    """FilterSet for /income_categories endpoint."""

    class Meta(TransferCategoryFilterSet.Meta):
        model = IncomeCategory
