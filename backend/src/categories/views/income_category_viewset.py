from categories.filters.income_category_filterset import IncomeCategoryFilterSet
from categories.models.income_category_model import IncomeCategory
from categories.serializers.income_category_serializer import IncomeCategorySerializer
from categories.views.transfer_category_viewset import TransferCategoryViewSet


class IncomeCategoryViewSet(TransferCategoryViewSet):
    """View for managing IncomeCategories."""

    serializer_class = IncomeCategorySerializer
    queryset = IncomeCategory.objects.all()
    filterset_class = IncomeCategoryFilterSet
