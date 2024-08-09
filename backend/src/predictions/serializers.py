from collections import OrderedDict
from decimal import Decimal

from django.db.models import Model
from predictions.models import ExpensePrediction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class ExpensePredictionSerializer(serializers.ModelSerializer):
    """Serializer for ExpensePrediction model."""

    class Meta:
        model: Model = ExpensePrediction
        fields = ('id', 'period', 'category', 'value', 'description')
        read_only_fields = ['id']

    @staticmethod
    def validate_value(value: Decimal) -> Decimal:
        """
        Checks if provided value is higher than zero.

        Args:
            value [Decimal]: Value of given ExpensePrediction.

        Returns:
            Decimal: Validated value of ExpensePrediction.
        """
        if value <= Decimal('0.00'):
            raise ValidationError('Value should be higher than 0.00.')
        return value

    def to_representation(self, instance: ExpensePrediction) -> OrderedDict:
        """
        Returns human-readable values of ExpensePrediction period and category.

        Attributes:
            instance [ExpensePrediction]: ExpensePrediction model instance

        Returns:
            OrderedDict: Dictionary containing readable ExpensePrediction period and category.
        """
        representation = super().to_representation(instance)
        representation['period'] = instance.period.name
        representation['category'] = instance.category.name
        return representation
