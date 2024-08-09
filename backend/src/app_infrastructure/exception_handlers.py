from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


def default_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Custom exception handling function.

    Args:
        exc [Exception]: Exception subclass.
        context [dict]: Context data of raised Exception.

    Returns:
        Response | None: DRF Response of None.
    """
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response

    if isinstance(getattr(exc, 'detail', None), (list, dict)):
        response.data = {'detail': response.data}

    return response
