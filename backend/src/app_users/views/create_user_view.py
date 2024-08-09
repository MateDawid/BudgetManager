from app_users.serializers.user_serializer import UserSerializer
from rest_framework import generics


class CreateUserView(generics.CreateAPIView):
    """View to create a new User."""

    serializer_class = UserSerializer
