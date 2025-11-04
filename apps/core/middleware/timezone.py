"""
Timezone middleware for the Careplan project.
"""

import pytz
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    """
    Middleware to set timezone based on user preferences.

    If user is authenticated and has a timezone preference,
    activate that timezone for the duration of the request.
    """

    def process_request(self, request):
        """Activate user's timezone if available."""
        if request.user.is_authenticated:
            # Get user's timezone from profile or use default
            tzname = getattr(request.user, 'timezone', None) or 'UTC'
            try:
                timezone.activate(pytz.timezone(tzname))
            except pytz.exceptions.UnknownTimeZoneError:
                # If timezone is invalid, use UTC
                timezone.activate(pytz.timezone('UTC'))
        else:
            timezone.deactivate()
