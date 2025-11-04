"""
General helper functions for the Careplan project.
"""

import random
import string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def generate_unique_code(prefix='', length=8):
    """
    Generate a unique alphanumeric code.

    Args:
        prefix: Optional prefix for the code
        length: Length of the random part (default: 8)

    Returns:
        String with format: {prefix}{random_alphanumeric}

    Example:
        generate_unique_code('EMP', 6) -> 'EMPAB12CD'
    """
    random_part = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )
    return f"{prefix}{random_part}"


def get_client_ip(request):
    """
    Extract client IP address from request.

    Handles proxy headers (X-Forwarded-For, X-Real-IP).

    Args:
        request: Django request object

    Returns:
        IP address as string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def paginate_queryset(queryset, page, page_size=50):
    """
    Paginate a queryset manually.

    Args:
        queryset: Django QuerySet to paginate
        page: Page number (1-indexed)
        page_size: Number of items per page (default: 50)

    Returns:
        Tuple of (page_object, has_next, has_previous)

    Example:
        items, has_next, has_prev = paginate_queryset(qs, 1, 20)
    """
    paginator = Paginator(queryset, page_size)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj, page_obj.has_next(), page_obj.has_previous()


def send_notification(user, notification_type, title, message, **kwargs):
    """
    Send a notification to a user.

    This is a helper function that will create a Notification object
    and optionally send an email based on user preferences.

    Args:
        user: User object to notify
        notification_type: Type of notification (from NotificationType choices)
        title: Notification title
        message: Notification message
        **kwargs: Additional data (action_url, related_object, created_by, etc.)

    Returns:
        Notification object or None

    Example:
        send_notification(
            user=employee,
            notification_type=NotificationType.VACATION_REQUEST_APPROVED,
            title='Vacation Request Approved',
            message='Your vacation request from Jan 1-5 has been approved.',
            action_url='/vacation/requests/123/',
            related_object=vacation_request,
            created_by=manager
        )
    """
    try:
        from apps.notifications.models import Notification, NotificationPreference

        # Check user preferences
        try:
            prefs = NotificationPreference.objects.get(user=user)
            if not prefs.should_notify(notification_type):
                return None
            if prefs.is_in_quiet_hours():
                return None
        except NotificationPreference.DoesNotExist:
            # No preferences set, proceed with notification
            pass

        # Create notification
        notification = Notification.objects.create(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=kwargs.get('action_url', ''),
            created_by=kwargs.get('created_by', None),
            updated_by=kwargs.get('created_by', None),
        )

        # Set related object if provided
        related_object = kwargs.get('related_object')
        if related_object:
            notification.related_object = related_object
            notification.save()

        # TODO: Send email notification via Celery task if email_notifications_enabled

        return notification
    except ImportError:
        # Notifications app not yet created
        return None


def format_currency(amount, currency='EUR'):
    """
    Format amount as currency string.

    Args:
        amount: Numeric amount
        currency: Currency code (default: EUR)

    Returns:
        Formatted currency string

    Example:
        format_currency(1234.56) -> '€1,234.56'
    """
    if currency == 'EUR':
        return f'€{amount:,.2f}'
    elif currency == 'USD':
        return f'${amount:,.2f}'
    else:
        return f'{amount:,.2f} {currency}'


def truncate_string(text, max_length=100, suffix='...'):
    """
    Truncate a string to a maximum length.

    Args:
        text: String to truncate
        max_length: Maximum length (default: 100)
        suffix: Suffix to add if truncated (default: '...')

    Returns:
        Truncated string

    Example:
        truncate_string('This is a long text', 10) -> 'This is...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
