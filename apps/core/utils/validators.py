"""
Custom validators for the Careplan project.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def validate_phone_number(value):
    """
    Validate phone number format.

    Accepts formats like:
    - +999999999 (international)
    - 999999999 (local)
    - 9-15 digits allowed

    Args:
        value: Phone number string to validate

    Raises:
        ValidationError: If phone number format is invalid
    """
    if not value:
        return

    # Remove spaces and hyphens
    cleaned = value.replace(' ', '').replace('-', '')

    # Pattern allows optional +, then 9-15 digits
    pattern = r'^\+?\d{9,15}$'
    if not re.match(pattern, cleaned):
        raise ValidationError(
            _('Phone number must be in format: +999999999. Between 9-15 digits allowed.')
        )


def validate_postal_code(value):
    """
    Validate postal code format (German format).

    Args:
        value: Postal code string to validate

    Raises:
        ValidationError: If postal code format is invalid
    """
    if not value:
        return

    # German postal code: 5 digits
    pattern = r'^\d{5}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Postal code must be 5 digits.')
        )


def validate_future_date(value):
    """
    Ensure date is in the future.

    Args:
        value: Date to validate

    Raises:
        ValidationError: If date is not in the future
    """
    if value < timezone.now().date():
        raise ValidationError(_('Date must be in the future.'))


def validate_past_date(value):
    """
    Ensure date is in the past.

    Args:
        value: Date to validate

    Raises:
        ValidationError: If date is not in the past
    """
    if value > timezone.now().date():
        raise ValidationError(_('Date must be in the past.'))


def validate_date_range(start_date, end_date):
    """
    Validate that start_date is before or equal to end_date.

    Args:
        start_date: Start date
        end_date: End date

    Raises:
        ValidationError: If start_date is after end_date
    """
    if start_date and end_date and start_date > end_date:
        raise ValidationError(_('Start date must be before or equal to end date.'))


def validate_positive_integer(value):
    """
    Validate that value is a positive integer.

    Args:
        value: Integer to validate

    Raises:
        ValidationError: If value is not positive
    """
    if value is not None and value < 0:
        raise ValidationError(_('Value must be a positive integer.'))


def validate_employee_id(value):
    """
    Validate employee ID format.

    Args:
        value: Employee ID string to validate

    Raises:
        ValidationError: If employee ID format is invalid
    """
    if not value:
        return

    # Employee ID: alphanumeric, 6-10 characters
    pattern = r'^[A-Z0-9]{6,10}$'
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _('Employee ID must be 6-10 alphanumeric characters.')
        )
