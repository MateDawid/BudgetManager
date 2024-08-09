from app_infrastructure.exception_handlers import default_exception_handler
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError


class TestDefaultExceptionHandler:
    def test_django_validation_error_with_string(self):
        """
        GIVEN: DjangoValidationError with string passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 400 returned with expected detail.
        """
        exception_detail = 'Django Validation Error'
        exception = DjangoValidationError(exception_detail)
        response = default_exception_handler(exception, {'error': 'Django Error'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail']['non_field_errors'][0] == exception_detail

    def test_django_validation_error_with_dict(self):
        """
        GIVEN: DjangoValidationError with dict passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 400 returned with expected detail.
        """
        exception_detail = {'exception': 'Django Validation Error'}
        exception = DjangoValidationError(exception_detail)
        response = default_exception_handler(exception, {'error': 'Django Error'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail']['exception'][0] == exception_detail['exception']

    def test_http404_error_with_string(self):
        """
        GIVEN: Http404 with string passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 404 returned with expected detail.
        """
        exception_detail = 'HTTP 404 Error'
        exception = Http404(exception_detail)
        response = default_exception_handler(exception, {'error': 'HTTP Error'})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Not found.'

    def test_http404_error_with_dict(self):
        """
        GIVEN: Http404 with dict passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 404 returned with expected detail.
        """
        exception_detail = {'exception': 'HTTP 404 Error'}
        exception = Http404(exception_detail)
        response = default_exception_handler(exception, {'error': 'HTTP Error'})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Not found.'

    def test_permission_denied_with_string(self):
        """
        GIVEN: PermissionDenied with string passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 403 returned with expected detail.
        """
        exception_detail = 'Permission denied'
        exception = PermissionDenied(exception_detail)
        response = default_exception_handler(exception, {'error': 'Permission error'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    def test_permission_denied_with_dict(self):
        """
        GIVEN: PermissionDenied with dict passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 403 returned with expected detail.
        """
        exception_detail = {'exception': 'Permission denied'}
        exception = PermissionDenied(exception_detail)
        response = default_exception_handler(exception, {'error': 'Permission error'})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['detail'] == 'You do not have permission to perform this action.'

    def test_drf_validation_error_with_string(self):
        """
        GIVEN: DRFValidationError with string passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 400 returned with expected detail.
        """
        exception_detail = 'DRF Validation Error'
        exception = DRFValidationError(exception_detail)
        response = default_exception_handler(exception, {'error': 'DRF Error'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail'][0] == exception_detail

    def test_drf_validation_error_with_dict(self):
        """
        GIVEN: DRFValidationError with dict passed as argument.
        WHEN: Processing exception with default_exception_handler.
        THEN: HTTP 400 returned with expected detail.
        """
        exception_detail = {'exception': 'DRF Validation Error'}
        exception = DjangoValidationError(exception_detail)
        response = default_exception_handler(exception, {'error': 'DRF Error'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['detail']['exception'][0] == exception_detail['exception']

    def test_system_error(self):
        """
        GIVEN: SystemError (as exception not handled by DRF exception_handler).
        WHEN: Processing exception with default_exception_handler.
        THEN: Response is None.
        """
        exception_detail = 'System Error'
        exception = SystemError(exception_detail)
        response = default_exception_handler(exception, {'error': 'System Error'})
        assert response is None
