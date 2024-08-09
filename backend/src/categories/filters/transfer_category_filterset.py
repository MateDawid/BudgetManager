from django.db.models import QuerySet
from django_filters import rest_framework as filters


class TransferCategoryFilterSet(filters.FilterSet):
    """Base FilterSet for TransferCategory endpoints."""

    name = filters.CharFilter(lookup_expr="icontains", field_name="name")
    common_only = filters.BooleanFilter(method="get_common_categories")

    class Meta:
        abstract = True
        fields = ["group", "owner", "is_active"]

    def get_common_categories(self, queryset: QuerySet, name: str, value: str):
        """
        Filtering QuerySet TransferCategories with or without owner.

        Args:
            queryset [QuerySet]: Input QuerySet
            name [str]: Name of filtered param
            value [str]: Value of filtered param

        Returns:
            QuerySet: Filtered QuerySet.
        """
        if value:
            return queryset.filter(owner__isnull=True)
        return queryset
