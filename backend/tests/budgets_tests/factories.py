import random
import string
from datetime import date

import factory
from app_users_tests.factories import UserFactory
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser


class BudgetFactory(factory.django.DjangoModelFactory):
    """Factory for Budget model."""

    class Meta:
        model = 'budgets.Budget'

    name = factory.Faker('text', max_nb_chars=128)
    description = factory.Faker('text', max_nb_chars=255)
    owner = factory.SubFactory(UserFactory)

    @factory.lazy_attribute
    def currency(self) -> str:
        """Generates currency."""
        return ''.join(random.choice(string.ascii_letters) for _ in range(3))

    @factory.post_generation
    def members(self, create: bool, users: list[AbstractUser], **kwargs) -> None:
        """
        Populates Budgets.members ManyToMany field with passed Users list.

        Args:
            create [bool]: Indicates if object is created or updated.
            users [list[AbstractUser]]:
            **kwargs [dict]: Keyword arguments
        """
        if not create or not users:
            return
        self.members.add(*users, self.owner)


class BudgetingPeriodFactory(factory.django.DjangoModelFactory):
    """Factory for BudgetingPeriod model."""

    class Meta:
        model = 'budgets.BudgetingPeriod'

    budget = factory.SubFactory(BudgetFactory)
    is_active = factory.Sequence(lambda _: False)

    @factory.lazy_attribute
    def date_start(self) -> date:
        """Generates date_start field."""
        last_date_start = self.budget.periods.all().order_by('date_start').values_list('date_start', flat=True).last()
        if not last_date_start:
            return date(2023, 1, 1)
        return last_date_start + relativedelta(months=1)

    @factory.lazy_attribute
    def date_end(self) -> date:
        """Generates date_end field."""
        last_date_start = self.budget.periods.all().order_by('date_start').values_list('date_start', flat=True).last()
        if not last_date_start:
            return date(2023, 1, 31)
        return last_date_start + relativedelta(months=2) - relativedelta(days=1)

    @factory.lazy_attribute
    def name(self) -> str:
        """Generates period name basing on provided date_range."""
        year_start, year_end = self.date_start.year, self.date_end.year
        month_start, month_end = self.date_start.month, self.date_end.month
        if year_start == year_end and month_start == month_end:
            return f'{year_start}_{month_start:02d}'
        else:
            return f'{year_start}_{month_start:02d} - {year_end}_{month_end:02d}'  # pragma: no cover
