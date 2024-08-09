from app_users.serializers.user_serializer import UserSerializer
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import authentication, generics, permissions


class ListUserView(generics.ListAPIView):
    """View to list all Users."""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self) -> QuerySet:
        """
        Additionally sorts queryset before returning it.

        Returns:
            QuerySet: QuerySet containing User model instances.
        """
        queryset = self.queryset
        return queryset.order_by('id').distinct()
