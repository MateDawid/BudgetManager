from categories.models.income_category_model import IncomeCategory
from categories.serializers.transfer_category_serializer import (
    TransferCategorySerializer,
)
from django.db.models import Model


class IncomeCategorySerializer(TransferCategorySerializer):
    """Serializer for IncomeCategory."""

    class Meta:
        model: Model = IncomeCategory
        fields = ["id", "name", "group", "description", "owner", "is_active"]
        read_only_fields = ["id"]
