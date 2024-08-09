from entities.models.deposit_model import Deposit
from entities.serializers.entity_serializer import EntitySerializer


class DepositSerializer(EntitySerializer):
    """Serializer for Deposit."""

    class Meta:
        model = Deposit
        fields = ['id', 'name', 'description', 'is_active']
        read_only_fields = ['id']
