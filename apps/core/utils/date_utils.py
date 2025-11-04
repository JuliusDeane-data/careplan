"""
Date and time utility functions for the Careplan project.

Important Business Logic:
- Employees work in a 24/7/365 shift system (including weekends and holidays)
- Weekends and holidays are regular work days (may have shift premiums)
- Vacation days are calculated EXCLUDING weekends and holidays
- Example: Vacation Monday-Sunday = 5 vacation days (excludes Sat/Sun)
- Each location must maintain minimum staff coverage at all times
"""

from datetime import timedelta, date
from calendar import monthrange
from django.db import models


def get_vacation_days_count(start_date, end_date, location=None):
    """
    Calculate vacation days for a date range.
    Excludes weekends and public holidays since employees
    cannot take vacation on these days.

    Args:
        start_date: Start date of vacation
        end_date: End date of vacation (inclusive)
        location: Optional location for location-specific holidays

    Returns:
        Number of vacation days (excludes weekends and holidays)

    Example:
        Monday to Friday = 5 vacation days
        Monday to Sunday = 5 vacation days (excludes Sat/Sun)
    """
    if start_date > end_date:
        return 0

    vacation_days = 0
    current = start_date

    while current <= end_date:
        # Count only weekdays that are not public holidays
        if is_workable_day(current, location):
            vacation_days += 1
        current += timedelta(days=1)

    return vacation_days


def get_total_days_count(start_date, end_date):
    """
    Calculate total calendar days between two dates (inclusive).
    This is for shift scheduling, not vacation calculation.

    Args:
        start_date: Start date
        end_date: End date (inclusive)

    Returns:
        Total number of calendar days

    Example:
        Monday to Sunday = 7 total days
    """
    if start_date > end_date:
        return 0
    return (end_date - start_date).days + 1


def is_weekend(date_obj):
    """
    Check if a date falls on weekend (Saturday or Sunday).

    Args:
        date_obj: Date to check

    Returns:
        True if Saturday or Sunday, False otherwise
    """
    return date_obj.weekday() >= 5  # Saturday=5, Sunday=6


def is_workable_day(date_obj, location=None):
    """
    Check if a day counts as a vacation day.
    Returns False for weekends and public holidays.

    This is used to determine if an employee can take vacation on this day.
    Since employees work shifts including weekends and holidays, they cannot
    use vacation days on these dates.

    Args:
        date_obj: Date to check
        location: Optional location for location-specific holidays

    Returns:
        True if day counts as vacation day, False otherwise
    """
    if is_weekend(date_obj):
        return False
    if is_public_holiday(date_obj, location):
        return False
    return True


def is_public_holiday(date_obj, location=None):
    """
    Check if date is a public holiday.

    Args:
        date_obj: Date to check
        location: Optional location for location-specific holidays

    Returns:
        True if public holiday, False otherwise
    """
    try:
        from apps.vacation.models import PublicHoliday

        query = PublicHoliday.objects.filter(date=date_obj)
        if location:
            # Include holidays for this location or global holidays (location=None)
            query = query.filter(
                models.Q(location=location) | models.Q(location__isnull=True)
            )

        return query.exists()
    except ImportError:
        # PublicHoliday model not yet created, return False
        return False


def date_range(start_date, end_date):
    """
    Generate a list of dates between start_date and end_date (inclusive).

    Args:
        start_date: Start date
        end_date: End date (inclusive)

    Returns:
        List of date objects

    Example:
        date_range(date(2025, 11, 3), date(2025, 11, 5))
        Returns: [date(2025, 11, 3), date(2025, 11, 4), date(2025, 11, 5)]
    """
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def get_month_date_range(year, month):
    """
    Get the first and last day of a given month.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)

    Returns:
        Tuple of (first_day, last_day) as date objects

    Example:
        get_month_date_range(2025, 11)
        Returns: (date(2025, 11, 1), date(2025, 11, 30))
    """
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    return first_day, last_day


def get_business_days_ahead(start_date, days):
    """
    Get the date that is N business days (weekdays) ahead.

    Args:
        start_date: Starting date
        days: Number of business days to add

    Returns:
        Date that is N business days ahead

    Example:
        get_business_days_ahead(date(2025, 11, 3), 5)  # Monday + 5 business days
        Returns: date(2025, 11, 10)  # Next Monday (skips weekend)
    """
    current = start_date
    business_days_added = 0

    while business_days_added < days:
        current += timedelta(days=1)
        if not is_weekend(current):
            business_days_added += 1

    return current
