from app_infrastructure.permissions import UserBelongsToBudgetPermission
from budgets.models import BudgetingPeriod
from budgets.serializers.budgeting_period_serializer import BudgetingPeriodSerializer
from django.db.models import Q, QuerySet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class BudgetingPeriodViewSet(ModelViewSet):
    """View for manage BudgetingPeriods."""

    serializer_class = BudgetingPeriodSerializer
    queryset = BudgetingPeriod.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, UserBelongsToBudgetPermission]

    def get_queryset(self) -> QuerySet:
        """
        Retrieves BudgetingPeriods for Budgets to which authenticated User belongs.

        Returns:
            QuerySet: Filtered BudgetingPeriod QuerySet.
        """
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            budget_pk = self.kwargs.get('budget_pk')
            if budget_pk:
                return (
                    self.queryset.filter(Q(budget__owner=user) | Q(budget__members=user), budget__pk=budget_pk)
                    .order_by('-date_start')
                    .distinct()
                )
        return self.queryset.none()  # pragma: no cover

    def perform_create(self, serializer: BudgetingPeriodSerializer) -> None:
        """
        Extended with saving Budget in BudgetingPeriod model.

        Args:
            serializer [BudgetingPeriodSerializer]: Serializer for BudgetingPeriod
        """
        serializer.save(budget_id=self.kwargs.get('budget_pk'))
