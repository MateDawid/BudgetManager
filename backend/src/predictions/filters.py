from django.db.models import QuerySet
from django_filters import rest_framework as filters
from predictions.models import ExpensePrediction


class ExpensePredictionFilterSet(filters.FilterSet):
    """FilterSet for ExpensePrediction endpoints."""

    period_name = filters.CharFilter(method='get_period_name')
    period_id = filters.NumberFilter(method='get_period_id')
    category_name = filters.CharFilter(method='get_category_name')
    category_id = filters.NumberFilter(method='get_category_id')

    class Meta:
        model = ExpensePrediction
        fields = ['period_id', 'period_name', 'category_id', 'category_name']

    def get_period_name(self, queryset: QuerySet, name: str, value: str):
        """
        Filtering QuerySet with period name or its part.

        Args:
            queryset [QuerySet]: Input QuerySet.
            name [str]: Name of filtered param.
            value [str]: Period name or its part.
        Returns:
            QuerySet: QuerySet filtered with period name.
        """
        return queryset.filter(period__name__icontains=value)

    def get_period_id(self, queryset: QuerySet, name: str, value: int):
        """
        Filtering QuerySet with period id.

        Args:
            queryset [QuerySet]: Input QuerySet.
            name [str]: Name of filtered param.
            value [str]: Period id.
        Returns:
            QuerySet: QuerySet filtered with period id.
        """
        return queryset.filter(period__id=value)

    def get_category_name(self, queryset: QuerySet, name: str, value: str):
        """
        Filtering QuerySet with category name or its part.

        Args:
            queryset [QuerySet]: Input QuerySet.
            name [str]: Name of filtered param.
            value [str]: Category name or its part.
        Returns:
            QuerySet: QuerySet filtered with category name.
        """
        return queryset.filter(category__name__icontains=value)

    def get_category_id(self, queryset: QuerySet, name: str, value: int):
        """
        Filtering QuerySet with category id.

        Args:
            queryset [QuerySet]: Input QuerySet.
            name [str]: Name of filtered param.
            value [str]: Category id.
        Returns:
            QuerySet: QuerySet filtered with category id.
        """
        return queryset.filter(category__id=value)
