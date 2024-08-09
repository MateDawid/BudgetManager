from app_users.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = User
        fields = ['email', 'password', 'name']
        extra_kwargs = {
            'password': {
                'write_only': True,  # password will be able to save in POST request, but won't be returned in response
                'min_length': 5,
            }
        }

    def create(self, validated_data: dict) -> User:
        """
        Creates and returns a User with encrypted password.

        Args:
            validated_data [dict]: Dictionary containing validated User data.

        Returns:
            User: Created User instance.
        """
        return User.objects.create_user(**validated_data)

    def update(self, instance: User, validated_data: dict) -> User:
        """
        Updates and returns User.

        Args:
            instance [User]: User instance to be updated.
            validated_data [dict]: Dictionary containing validated User data.

        Returns:
            User: Updated User instance.
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
