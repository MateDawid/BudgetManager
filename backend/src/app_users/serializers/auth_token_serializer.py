from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the User's AuthToken."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate and authenticate the user.

        Args:
            attrs [dict]: Values passed to Serializer.

        Returns:
            dict: Extended attrs dictionary.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            msg = _('Unable to authenticate user with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
