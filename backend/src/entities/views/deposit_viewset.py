from app_infrastructure.permissions import UserBelongsToBudgetPermission
from django.db.models import QuerySet
from entities.models.deposit_model import Deposit
from entities.serializers.deposit_serializer import DepositSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class DepositViewSet(ModelViewSet):
    """View for managing Deposits."""

    serializer_class = DepositSerializer
    queryset = Deposit.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, UserBelongsToBudgetPermission]

    def get_queryset(self) -> QuerySet:
        """
        Retrieve Deposits for Budget passed in URL.

        Returns:
            QuerySet: Filtered Deposit QuerySet.
        """
        return self.queryset.filter(budget__pk=self.kwargs.get('budget_pk')).distinct()

    def perform_create(self, serializer: DepositSerializer) -> None:
        """
        Additionally save Budget from URL on Deposit instance during saving serializer. Create Entity object for
        Deposit representation in Transfers.

        Args:
            serializer [DepositSerializer]: Serializer for Deposit model.
        """
        serializer.save(budget_id=self.kwargs.get('budget_pk'), is_deposit=True)
