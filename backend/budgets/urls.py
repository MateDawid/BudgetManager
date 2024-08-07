from budgets.views import BudgetingPeriodViewSet, BudgetViewSet
from categories.views import ExpenseCategoryViewSet, IncomeCategoryViewSet
from deposits.views import DepositViewSet
from django.urls import include, path
from entities.views import EntityViewSet
from predictions.views import ExpensePredictionViewSet
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

app_name = 'budgets'


router = routers.DefaultRouter()
router.register(r'', BudgetViewSet)

budget_router = NestedSimpleRouter(router, r'', lookup='budget')
budget_router.register(r'periods', BudgetingPeriodViewSet, basename='period')
budget_router.register(r'deposits', DepositViewSet, basename='deposit')
budget_router.register(r'entities', EntityViewSet, basename='entity')
budget_router.register(r'income_categories', IncomeCategoryViewSet, basename='income_category')
budget_router.register(r'expense_categories', ExpenseCategoryViewSet, basename='expense_category')
budget_router.register(r'expense_predictions', ExpensePredictionViewSet, basename='expense_prediction')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(budget_router.urls)),
]
