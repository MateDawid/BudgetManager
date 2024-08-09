from app_users.models import User
from app_users.serializers.user_serializer import UserSerializer
from requests import Request
from rest_framework import authentication, generics, permissions
from rest_framework.exceptions import MethodNotAllowed


class AuthenticatedUserView(generics.RetrieveUpdateAPIView):
    """View for managing authenticated User."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User | None:
        """
        Retrieves and returns the authenticated user.

        Returns:
            User | None: Authenticated User or None.
        """
        return self.request.user

    def put(self, request: Request, *args: list, **kwargs: dict) -> None:
        """
        Overrides PUT method handling to return HTTP 405 Method not allowed.

        Args:
            request [Request]: User request.

        Raises:
            MethodNotAllowed: Raised when PUT method performed on endpoint. Returns 405 HTTP status.
        """
        raise MethodNotAllowed(request.method)
