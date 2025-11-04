"""
Tests for date utility functions.
"""

from django.test import TestCase
from datetime import date
from apps.core.utils.date_utils import (
    get_vacation_days_count,
    get_total_days_count,
    is_weekend,
    is_workable_day,
    date_range,
    get_month_date_range,
    get_business_days_ahead
)


class DateUtilsTestCase(TestCase):
    """Test cases for date utility functions."""

    def test_vacation_days_weekdays_only(self):
        """Test vacation days calculation for weekdays only."""
        # Monday to Friday = 5 vacation days
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 7)    # Friday
        self.assertEqual(get_vacation_days_count(start, end), 5)

    def test_vacation_days_with_weekend(self):
        """Test vacation days calculation excluding weekends."""
        # Monday to Sunday = 5 vacation days (excludes Sat/Sun)
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 9)    # Sunday
        self.assertEqual(get_vacation_days_count(start, end), 5)

    def test_vacation_days_single_day(self):
        """Test vacation days for a single day."""
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 3)    # Same day
        self.assertEqual(get_vacation_days_count(start, end), 1)

    def test_vacation_days_weekend_only(self):
        """Test vacation days for weekend only (should be 0)."""
        start = date(2025, 11, 8)  # Saturday
        end = date(2025, 11, 9)    # Sunday
        self.assertEqual(get_vacation_days_count(start, end), 0)

    def test_vacation_days_invalid_range(self):
        """Test vacation days with start date after end date."""
        start = date(2025, 11, 10)
        end = date(2025, 11, 3)
        self.assertEqual(get_vacation_days_count(start, end), 0)

    def test_total_days_includes_weekend(self):
        """Test total days calculation includes weekends."""
        # Monday to Sunday = 7 total calendar days
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 9)    # Sunday
        self.assertEqual(get_total_days_count(start, end), 7)

    def test_total_days_single_day(self):
        """Test total days for a single day."""
        start = date(2025, 11, 3)
        end = date(2025, 11, 3)
        self.assertEqual(get_total_days_count(start, end), 1)

    def test_weekend_detection(self):
        """Test weekend detection."""
        saturday = date(2025, 11, 8)
        sunday = date(2025, 11, 9)
        monday = date(2025, 11, 10)
        friday = date(2025, 11, 7)

        self.assertTrue(is_weekend(saturday))
        self.assertTrue(is_weekend(sunday))
        self.assertFalse(is_weekend(monday))
        self.assertFalse(is_weekend(friday))

    def test_workable_day_excludes_weekends(self):
        """Test workable day detection excludes weekends."""
        monday = date(2025, 11, 3)
        saturday = date(2025, 11, 8)

        self.assertTrue(is_workable_day(monday))
        self.assertFalse(is_workable_day(saturday))

    def test_date_range_generation(self):
        """Test date range generation."""
        start = date(2025, 11, 3)
        end = date(2025, 11, 5)
        expected = [
            date(2025, 11, 3),
            date(2025, 11, 4),
            date(2025, 11, 5)
        ]
        self.assertEqual(date_range(start, end), expected)

    def test_month_date_range(self):
        """Test getting first and last day of month."""
        first, last = get_month_date_range(2025, 11)
        self.assertEqual(first, date(2025, 11, 1))
        self.assertEqual(last, date(2025, 11, 30))

        # Test February (non-leap year)
        first, last = get_month_date_range(2025, 2)
        self.assertEqual(first, date(2025, 2, 1))
        self.assertEqual(last, date(2025, 2, 28))

    def test_business_days_ahead(self):
        """Test calculating date N business days ahead."""
        # Monday + 5 business days = next Monday (skips weekend)
        monday = date(2025, 11, 3)
        result = get_business_days_ahead(monday, 5)
        expected = date(2025, 11, 10)  # Next Monday
        self.assertEqual(result, expected)

        # Friday + 1 business day = next Monday (skips weekend)
        friday = date(2025, 11, 7)
        result = get_business_days_ahead(friday, 1)
        expected = date(2025, 11, 10)  # Next Monday
        self.assertEqual(result, expected)
