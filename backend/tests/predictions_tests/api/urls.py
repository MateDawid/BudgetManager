from django.urls import reverse


def expense_prediction_url(budget_id: int):
    """Create and return an ExpensePrediction list URL."""
    return reverse('budgets:expense_prediction-list', args=[budget_id])


def expense_prediction_detail_url(budget_id: int, prediction_id: int):
    """Create and return an ExpensePrediction detail URL."""
    return reverse('budgets:expense_prediction-detail', args=[budget_id, prediction_id])
