from app_users.serializers.auth_token_serializer import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class CreateTokenView(ObtainAuthToken):
    """View to create new AuthToken for User."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
