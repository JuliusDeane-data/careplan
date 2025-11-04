"""
Custom exception handler for Django REST Framework.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('apps.core')


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error format.

    Args:
        exc: Exception object
        context: Context dictionary containing view, request, etc.

    Returns:
        Response object with standardized error format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize error response format
        custom_response = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code
        }

        # Add details if available
        if isinstance(response.data, dict):
            custom_response['details'] = response.data
        elif isinstance(response.data, list):
            custom_response['details'] = {'errors': response.data}
        else:
            custom_response['details'] = {'detail': response.data}

        response.data = custom_response

        # Log the error
        logger.error(
            f"API Error: {exc} - Status: {response.status_code} - "
            f"View: {context.get('view', 'Unknown')}"
        )
    else:
        # Handle uncaught exceptions
        logger.exception(f"Uncaught exception in API: {exc}")

    return response
