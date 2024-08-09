from categories.models import ExpenseCategory, IncomeCategory

DEFAULT_EXPENSE_CATEGORIES = [
    {'name': 'Food', 'description': 'Expenses for food.', 'group': ExpenseCategory.ExpenseGroups.MOST_IMPORTANT},
    {
        'name': 'Bills',
        'description': 'Expenses for all bills like accommodation, electricity, etc.',
        'group': ExpenseCategory.ExpenseGroups.MOST_IMPORTANT,
    },
    {'name': 'Taxes', 'description': 'Expenses for taxes.', 'group': ExpenseCategory.ExpenseGroups.DEBTS},
    {'name': 'Savings', 'description': 'Expenses for savings.', 'group': ExpenseCategory.ExpenseGroups.SAVINGS},
    {'name': 'Unexpected', 'description': 'Unexpected expenses.', 'group': ExpenseCategory.ExpenseGroups.OTHERS},
]
DEFAULT_INCOME_CATEGORIES = [
    {'name': 'Salary', 'description': 'Salary.', 'group': IncomeCategory.IncomeGroups.REGULAR},
    {'name': 'Bonuses', 'description': 'Extra bonuses.', 'group': IncomeCategory.IncomeGroups.IRREGULAR},
]
