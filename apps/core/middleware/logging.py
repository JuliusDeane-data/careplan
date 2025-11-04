"""
Request logging middleware for the Careplan project.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps.core')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all HTTP requests for auditing and debugging.

    Logs:
    - Request method, path, user, and IP address
    - Response status code
    - Request processing time

    Skips logging for:
    - Static files (/static/)
    - Health checks (/health/)
    - Debug toolbar (/__debug__/)
    """

    def process_request(self, request):
        """Mark the start time of the request."""
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        """Log the request details after processing."""
        # Skip logging for static files, health checks, and debug toolbar
        if (request.path.startswith('/static/') or
            request.path == '/health/' or
            request.path.startswith('/__debug__/')):
            return response

        # Calculate request duration
        duration = time.time() - getattr(request, '_start_time', time.time())

        # Get user info
        user = request.user if request.user.is_authenticated else 'Anonymous'

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')

        # Log the request
        logger.info(
            f"{request.method} {request.path} - "
            f"User: {user} - "
            f"IP: {ip} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )

        return response
