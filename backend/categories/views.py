from app_config.permissions import UserBelongsToBudgetPermission
from categories.filters import ExpenseCategoryFilterSet, IncomeCategoryFilterSet
from categories.models import ExpenseCategory, IncomeCategory
from categories.serializers import (
    ExpenseCategorySerializer,
    IncomeCategorySerializer,
    TransferCategorySerializer,
)
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class TransferCategoryViewSet(ModelViewSet):
    """Base view for managing TransferCategories."""

    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated, UserBelongsToBudgetPermission)
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    ordering = ('id', 'group', 'name')

    def get_queryset(self) -> QuerySet:
        """
        Retrieve TransferCategories for Budget passed in URL.
        Returns:
            QuerySet: Filtered TransferCategory QuerySet.
        """
        return self.queryset.prefetch_related('owner').filter(budget__pk=self.kwargs.get('budget_pk')).distinct()

    def perform_create(self, serializer: TransferCategorySerializer) -> None:
        """
        Additionally save Budget from URL on TransferCategory instance during saving serializer.
        Args:
            serializer [TransferCategorySerializer]: Serializer for TransferCategory model.
        """
        serializer.save(budget_id=self.kwargs.get('budget_pk'))


class ExpenseCategoryViewSet(TransferCategoryViewSet):
    serializer_class = ExpenseCategorySerializer
    queryset = ExpenseCategory.objects.all()
    filterset_class = ExpenseCategoryFilterSet


class IncomeCategoryViewSet(TransferCategoryViewSet):
    serializer_class = IncomeCategorySerializer
    queryset = IncomeCategory.objects.all()
    filterset_class = IncomeCategoryFilterSet
