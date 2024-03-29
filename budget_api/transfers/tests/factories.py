import random

import factory
from app_users.tests.factories import UserFactory
from transfers.models import TransferCategory


class TransferCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for TransferCategory model."""

    class Meta:
        model = 'transfers.TransferCategory'

    name = factory.Faker('text', max_nb_chars=128)
    description = factory.Faker('text', max_nb_chars=255)
    category_type = factory.Faker('random_element', elements=[TransferCategory.EXPENSE, TransferCategory.INCOME])
    is_active = factory.Faker('boolean')

    @factory.lazy_attribute
    def user(self) -> str:
        """Generates user field value - User model instance or None."""
        options = [UserFactory(), None]
        return random.choice(options)

    @factory.lazy_attribute
    def scope(self) -> str:
        """Generates type field value basing on user field value."""
        if self.user is None:
            return TransferCategory.GLOBAL
        else:
            return TransferCategory.PERSONAL
