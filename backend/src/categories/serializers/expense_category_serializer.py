from categories.models.expense_category_model import ExpenseCategory
from categories.serializers.transfer_category_serializer import (
    TransferCategorySerializer,
)
from django.db.models import Model


class ExpenseCategorySerializer(TransferCategorySerializer):
    """Serializer for ExpenseCategory."""

    class Meta:
        model: Model = ExpenseCategory
        fields = ["id", "name", "group", "description", "owner", "is_active"]
        read_only_fields = ["id"]
