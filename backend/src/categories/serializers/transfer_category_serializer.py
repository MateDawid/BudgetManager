from collections import OrderedDict

from app_users.models import User
from categories.models.expense_category_model import ExpenseCategory
from categories.models.income_category_model import IncomeCategory
from django.db.models import Model
from rest_framework import serializers

CATEGORY_NAME_ERRORS = {
    "PERSONAL": "Personal {class_name} with given name already exists in Budget for provided owner.",
    "COMMON": "Common {class_name} with given name already exists in Budget.",
}


class TransferCategorySerializer(serializers.ModelSerializer):
    """Base class for TransferCategorySerializers"""

    class Meta:
        model: Model = Model

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        """
        Validates TransferCategory.
        Args:
            attrs [OrderedDict]: Dictionary containing given TransferCategory params
        Returns:
            OrderedDict: Dictionary with validated attrs values.
        """
        name = attrs.get("name") or getattr(self.instance, "name")
        owner = attrs.get("owner") or getattr(self.instance, "owner", None)
        if owner:
            self._validate_owner(owner)
        self._validate_category_name(name, owner)

        return attrs

    def _validate_owner(self, owner: User) -> None:
        """
        Checks if provided owner belongs to Budget.
        Args:
            owner [User]: TransferCategory owner or None.
        Raises:
            ValidationError: Raised when given User does not belong to Budget.
        """
        if not owner.is_budget_member(self.context["view"].kwargs["budget_pk"]):
            raise serializers.ValidationError("Provided owner does not belong to Budget.")

    def _validate_category_name(self, name: str, owner: User | None) -> None:
        """
        Checks if TransferCategory with provided name already exists in Budget.
        Args:
            name [str]: Name for TransferCategory
            owner [User]: Owner of TransferCategory
        Raises:
            ValidationError: Raised when TransferCategory for particular owner already exists in Budget.
        """
        query_filters = {"budget": self.context["view"].kwargs["budget_pk"], "name__iexact": name, "owner": owner}
        if owner:
            query_filters["owner"] = owner
        else:
            query_filters["owner__isnull"] = True

        if self.Meta.model.objects.filter(**query_filters).exclude(id=getattr(self.instance, "id", None)).exists():
            if owner:
                raise serializers.ValidationError(
                    CATEGORY_NAME_ERRORS["PERSONAL"].format(class_name=self.Meta.model.__name__)
                )
            else:
                raise serializers.ValidationError(
                    CATEGORY_NAME_ERRORS["COMMON"].format(class_name=self.Meta.model.__name__)
                )

    def to_representation(self, instance: IncomeCategory | ExpenseCategory) -> OrderedDict:
        """
        Returns human-readable values of IncomeCategory group.
        Attributes:
            instance [IncomeCategory]: IncomeCategory model instance
        Returns:
            OrderedDict: Dictionary containing readable TransferCategory income_group.
        """
        representation = super().to_representation(instance)
        representation["group"] = instance.get_group_display()

        return representation
