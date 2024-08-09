from budgets.models import Budget
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer


class BudgetSerializer(ModelSerializer):
    """Serializer for Budget model."""

    class Meta:
        model = Budget
        fields = ['id', 'name', 'description', 'currency', 'members']
        read_only_fields = ['id']

    def validate_name(self, value: str) -> str:
        """
        Validates if Budget with given name and request.user as owner exists already.

        Returns:
            str: Validated Budget name.

        Raises:
            ValidationError: Raised when Budget with given name and request.user as owner exists already.
        """
        try:
            self.Meta.model.objects.get(owner=self.context['request'].user, name=value)
        except self.Meta.model.DoesNotExist:
            pass
        else:
            raise ValidationError(f'User already owns Budget with name "{value}".')
        return value
