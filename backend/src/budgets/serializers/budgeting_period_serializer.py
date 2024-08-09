from collections import OrderedDict

from budgets.models import BudgetingPeriod
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class BudgetingPeriodSerializer(serializers.ModelSerializer):
    """Serializer for BudgetingPeriod."""

    class Meta:
        model = BudgetingPeriod
        fields = ['id', 'name', 'date_start', 'date_end', 'is_active']
        read_only_fields = ['id']

    def validate_name(self, name: str) -> str:
        """
        Checks if Budget contains BudgetingPeriod with given name already.

        Args:
            name [str]: Given name for BudgetingPeriod

        Returns:
            str: Validated name value.

        Raises:
            ValidationError: Raised when BudgetingPeriod for Budget with given name already exists in database.
        """
        try:
            BudgetingPeriod.objects.get(budget=self.context['view'].kwargs['budget_pk'], name=name)
        except self.Meta.model.DoesNotExist:
            pass
        else:
            raise ValidationError(f'Period with name "{name}" already exists in Budget.')
        return name

    def validate_is_active(self, is_active: bool) -> bool:
        """
        Checks if Budget contains active BudgetingPeriod.

        Args:
            is_active [bool]: Given is_active value to determine if BudgetingPeriod is active or not.

        Returns:
            bool: Validated is_active value.

        Raises:
            ValidationError: Raised when active BudgetingPeriod for Budget already exists in database.
        """
        if is_active is True:
            active_periods = BudgetingPeriod.objects.filter(
                budget__pk=self.context['view'].kwargs['budget_pk'], is_active=True
            ).exclude(pk=getattr(self.instance, 'pk', None))
            if active_periods.exists():
                raise ValidationError('Active period already exists in Budget.')
        return is_active

    def validate(self, attrs: OrderedDict) -> OrderedDict:
        """
        Checks if given BudgetingPeriod start and end dates do not collide with other Budget periods dates.

        Args:
            attrs [OrderedDict]: Dictionary containing given BudgetingPeriod params

        Returns:
            OrderedDict: Dictionary with validated attrs values.

        Raises:
            ValidationError: Raised when date_end earlier than date start or some Budget periods
            dates collides with given dates.
        """
        date_start = attrs.get('date_start', getattr(self.instance, 'date_start', None))
        date_end = attrs.get('date_end', getattr(self.instance, 'date_end', None))
        if date_start >= date_end:
            raise ValidationError('Start date should be earlier than end date.')

        budget_pk = self.context['view'].kwargs['budget_pk']
        colliding_periods = BudgetingPeriod.objects.filter(
            Q(budget__pk=budget_pk, date_start__lte=date_start, date_end__gte=date_start)
            | Q(budget__pk=budget_pk, date_start__lte=date_end, date_end__gte=date_end)
            | Q(budget__pk=budget_pk, date_start__gte=date_start, date_end__lte=date_end)
        ).exclude(pk=getattr(self.instance, 'pk', None))
        if colliding_periods.exists():
            raise ValidationError('Budgeting period date range collides with other period in Budget.')

        return super().validate(attrs)
