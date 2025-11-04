"""
Tests for custom validators.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.utils import timezone
from apps.core.utils.validators import (
    validate_phone_number,
    validate_postal_code,
    validate_future_date,
    validate_past_date,
    validate_date_range,
    validate_positive_integer,
    validate_employee_id
)


class ValidatorsTestCase(TestCase):
    """Test cases for custom validators."""

    def test_valid_phone_number(self):
        """Test validation of valid phone numbers."""
        valid_numbers = [
            '+491234567890',  # 12 digits with country code
            '491234567890',   # 12 digits
            '+491234567890123',  # 15 digits total (max allowed)
        ]
        for number in valid_numbers:
            try:
                validate_phone_number(number)
            except ValidationError:
                self.fail(f"Valid phone number raised ValidationError: {number}")

    def test_invalid_phone_number(self):
        """Test validation of invalid phone numbers."""
        invalid_numbers = [
            '123',  # Too short
            '+49123456789012345',  # Too long
            'abcdefghijk',  # Letters
        ]
        for number in invalid_numbers:
            with self.assertRaises(ValidationError):
                validate_phone_number(number)

    def test_valid_postal_code(self):
        """Test validation of valid German postal codes."""
        valid_codes = ['12345', '98765', '00000']
        for code in valid_codes:
            try:
                validate_postal_code(code)
            except ValidationError:
                self.fail(f"Valid postal code raised ValidationError: {code}")

    def test_invalid_postal_code(self):
        """Test validation of invalid postal codes."""
        invalid_codes = [
            '1234',  # Too short
            '123456',  # Too long
            'abcde',  # Letters
            '12 34',  # Space
        ]
        for code in invalid_codes:
            with self.assertRaises(ValidationError):
                validate_postal_code(code)

    def test_future_date_valid(self):
        """Test validation of future dates."""
        tomorrow = timezone.now().date() + timedelta(days=1)
        try:
            validate_future_date(tomorrow)
        except ValidationError:
            self.fail("Future date raised ValidationError")

    def test_future_date_invalid(self):
        """Test validation rejects past dates."""
        yesterday = timezone.now().date() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_future_date(yesterday)

    def test_past_date_valid(self):
        """Test validation of past dates."""
        yesterday = timezone.now().date() - timedelta(days=1)
        try:
            validate_past_date(yesterday)
        except ValidationError:
            self.fail("Past date raised ValidationError")

    def test_past_date_invalid(self):
        """Test validation rejects future dates."""
        tomorrow = timezone.now().date() + timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_past_date(tomorrow)

    def test_valid_date_range(self):
        """Test validation of valid date ranges."""
        start = date(2025, 11, 1)
        end = date(2025, 11, 30)
        try:
            validate_date_range(start, end)
        except ValidationError:
            self.fail("Valid date range raised ValidationError")

    def test_invalid_date_range(self):
        """Test validation rejects invalid date ranges."""
        start = date(2025, 11, 30)
        end = date(2025, 11, 1)
        with self.assertRaises(ValidationError):
            validate_date_range(start, end)

    def test_valid_positive_integer(self):
        """Test validation of positive integers."""
        valid_values = [0, 1, 100, 999999]
        for value in valid_values:
            try:
                validate_positive_integer(value)
            except ValidationError:
                self.fail(f"Valid positive integer raised ValidationError: {value}")

    def test_invalid_positive_integer(self):
        """Test validation rejects negative integers."""
        invalid_values = [-1, -100, -999]
        for value in invalid_values:
            with self.assertRaises(ValidationError):
                validate_positive_integer(value)

    def test_valid_employee_id(self):
        """Test validation of valid employee IDs."""
        valid_ids = [
            'ABC123',
            'EMP001',
            'WORKER99',
            'A1B2C3D4E5',  # 10 characters
        ]
        for emp_id in valid_ids:
            try:
                validate_employee_id(emp_id)
            except ValidationError:
                self.fail(f"Valid employee ID raised ValidationError: {emp_id}")

    def test_invalid_employee_id(self):
        """Test validation of invalid employee IDs."""
        invalid_ids = [
            'ABC',  # Too short
            'ABCDEFGHIJK',  # Too long
            'EMP-001',  # Contains hyphen
            'EMP 001',  # Contains space
        ]
        for emp_id in invalid_ids:
            with self.assertRaises(ValidationError):
                validate_employee_id(emp_id)
