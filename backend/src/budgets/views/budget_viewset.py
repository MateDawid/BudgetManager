from budgets.models import Budget
from budgets.serializers.budget_serializer import BudgetSerializer
from categories.budget_defaults import (
    DEFAULT_EXPENSE_CATEGORIES,
    DEFAULT_INCOME_CATEGORIES,
)
from categories.models import ExpenseCategory, IncomeCategory
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


class BudgetViewSet(ModelViewSet):
    """View for manage Budgets."""

    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Retrieves Budgets membered by authenticated User.

        Returns:
            QuerySet: QuerySet containing Budgets containing authenticated User as member.
        """
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return self.queryset.filter(members=user).order_by('id').distinct()
        return self.queryset.none()  # pragma: no cover

    @action(detail=False, methods=['GET'])
    def owned(self, request: Request, **kwargs: dict) -> Response:
        """
        Retrieves Budgets owned by authenticated User.

        Args:
            request [Request]: User request.

        Returns:
            Response: Budgets owned by authenticated User.
        """
        owned_budgets = self.queryset.filter(owner=self.request.user).order_by('id').distinct()
        serializer = self.get_serializer(owned_budgets, many=True)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['GET'])
    def membered(self, request: Request, **kwargs: dict) -> Response:
        """
        Retrieves Budgets in which authenticated User is a member.

        Args:
            request [Request]: User request.

        Returns:
            Response: Budgets in which authenticated User is a member.
        """
        membered_budgets = self.queryset.filter(members=self.request.user).order_by('id').distinct()
        serializer = self.get_serializer(membered_budgets, many=True)
        return Response({'results': serializer.data})

    def perform_create(self, serializer: BudgetSerializer) -> None:
        """
        Saves request User as owner of Budget model and creates default ExpenseCategory and IncomeCategory objects.

        Args:
            serializer [BudgetSerializer]: Budget data serializer.
        """
        with transaction.atomic():
            budget = serializer.save(owner=self.request.user)
            for expense_category in DEFAULT_EXPENSE_CATEGORIES:
                ExpenseCategory.objects.create(budget=budget, **expense_category)
            for income_category in DEFAULT_INCOME_CATEGORIES:
                IncomeCategory.objects.create(budget=budget, **income_category)
