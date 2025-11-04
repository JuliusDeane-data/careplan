# Core App Implementation Plan

## Overview
The Core app provides shared functionality, base models, mixins, utilities, and custom middleware that will be used across all other apps in the Careplan project. This is the foundation for maintaining consistent behavior and reducing code duplication.

---

## 1. Base Abstract Models

### 1.1 TimeStampedModel
**Purpose**: Automatically track creation and modification timestamps for all models

**Fields**:
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Usage**: All other models will inherit from this

**Implementation**:
```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
```

---

### 1.2 SoftDeleteModel
**Purpose**: Implement soft deletion (mark as deleted instead of actual deletion)

**Fields**:
- `is_deleted` (BooleanField, default=False, db_index=True)
- `deleted_at` (DateTimeField, null=True, blank=True)
- `deleted_by` (ForeignKey to User, null=True, blank=True)

**Custom Manager**:
- `objects` - Default manager (excludes soft-deleted records)
- `all_objects` - Returns all records including soft-deleted

**Methods**:
- `soft_delete()` - Mark record as deleted
- `restore()` - Restore soft-deleted record

**Implementation**:
```python
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted_objects'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()
```

---

### 1.3 AuditModel
**Purpose**: Track who created and last modified a record

**Fields**:
- `created_by` (ForeignKey to User, null=True)
- `updated_by` (ForeignKey to User, null=True)

**Usage**: Combined with TimeStampedModel for complete audit trail

**Implementation**:
```python
class AuditModel(models.Model):
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True
```

---

### 1.4 BaseModel (Combined)
**Purpose**: Ultimate base model combining all features

**Inherits from**:
- TimeStampedModel
- SoftDeleteModel
- AuditModel

**Implementation**:
```python
class BaseModel(TimeStampedModel, SoftDeleteModel, AuditModel):
    """
    Base model that combines timestamps, soft delete, and audit tracking.
    Use this as the base for most models in the application.
    """
    class Meta:
        abstract = True
```

---

## 2. Custom Managers and QuerySets

### 2.1 OptimizedQuerySet
**Purpose**: Provide common query optimization methods

**Methods**:
- `with_user()` - Automatically select_related common User foreign keys
- `with_location()` - Automatically select_related Location
- `active()` - Filter for active records (is_active=True)
- `inactive()` - Filter for inactive records

**Implementation**:
```python
class OptimizedQuerySet(models.QuerySet):
    def with_user(self):
        return self.select_related('created_by', 'updated_by')

    def with_location(self):
        return self.select_related('location')

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)
```

---

## 3. Utility Functions

### 3.1 Date and Time Utilities (`utils/date_utils.py`)

**Important Business Logic**:
- Employees work in a **24/7/365 shift system** (including weekends and holidays)
- Weekends and holidays are **regular work days** (may have shift premiums)
- Vacation days are calculated **excluding weekends and holidays**
- Example: Vacation Monday-Sunday = 5 vacation days (excludes Sat/Sun)
- Each location must maintain minimum staff coverage at all times

**Functions**:
- `get_vacation_days_count(start_date, end_date)` - Calculate vacation days (excludes weekends & holidays)
- `get_total_days_count(start_date, end_date)` - Calculate total calendar days
- `is_weekend(date)` - Check if date is weekend
- `is_public_holiday(date, location=None)` - Check if date is public holiday
- `is_workable_day(date, location=None)` - Check if day counts as vacation day (not weekend/holiday)
- `date_range(start_date, end_date)` - Generate list of dates in range
- `get_month_date_range(year, month)` - Get start and end dates of a month

**Implementation Example**:
```python
from datetime import timedelta, date
from django.utils import timezone

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
    """
    if start_date > end_date:
        return 0
    return (end_date - start_date).days + 1

def is_weekend(date_obj):
    """Check if a date falls on weekend (Saturday or Sunday)."""
    return date_obj.weekday() >= 5

def is_workable_day(date_obj, location=None):
    """
    Check if a day counts as a vacation day.
    Returns False for weekends and public holidays.

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
    # Will be implemented with PublicHoliday model lookup
    # For now, return False as placeholder
    from apps.vacation.models import PublicHoliday

    query = PublicHoliday.objects.filter(date=date_obj)
    if location:
        query = query.filter(models.Q(location=location) | models.Q(location__isnull=True))

    return query.exists()

def date_range(start_date, end_date):
    """Generate a list of dates between start_date and end_date (inclusive)."""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def get_month_date_range(year, month):
    """Get the first and last day of a given month."""
    from calendar import monthrange
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])
    return first_day, last_day
```

---

### 3.2 Validators (`utils/validators.py`)

**Custom Validators**:
- `validate_phone_number(value)` - Validate phone number format
- `validate_postal_code(value)` - Validate postal code
- `validate_future_date(value)` - Ensure date is in the future
- `validate_date_range(start_date, end_date)` - Validate start < end

**Implementation Example**:
```python
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_phone_number(value):
    """Validate phone number format."""
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Phone number must be in format: +999999999. Up to 15 digits allowed.')
        )

def validate_future_date(value):
    """Ensure date is in the future."""
    from django.utils import timezone
    if value < timezone.now().date():
        raise ValidationError(_('Date must be in the future.'))
```

---

### 3.3 Helper Functions (`utils/helpers.py`)

**Functions**:
- `generate_unique_code(prefix, length=8)` - Generate unique alphanumeric codes
- `get_client_ip(request)` - Extract client IP from request
- `send_notification(user, notification_type, **kwargs)` - Send notifications
- `paginate_queryset(queryset, page, page_size=50)` - Manual pagination helper

---

## 4. Custom Middleware

### 4.1 RequestLoggingMiddleware
**Purpose**: Log all requests for auditing and debugging

**Features**:
- Log request method, path, user, IP address
- Log response status code and time taken
- Skip logging for static files and health checks

**Implementation**:
```python
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps.core')

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        # Skip logging for static files and health checks
        if request.path.startswith('/static/') or request.path == '/health/':
            return response

        duration = time.time() - request._start_time
        user = request.user if request.user.is_authenticated else 'Anonymous'

        logger.info(
            f"{request.method} {request.path} - "
            f"User: {user} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.2f}s"
        )

        return response
```

---

### 4.2 TimezoneMiddleware
**Purpose**: Set timezone based on user preferences

**Implementation**:
```python
import pytz
from django.utils import timezone

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Get user's timezone from profile or use default
            tzname = getattr(request.user, 'timezone', 'UTC')
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
```

---

## 5. Custom Exception Handler

**Purpose**: Provide consistent API error responses

**File**: `core/exceptions.py`

**Implementation**:
```python
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        # Customize error response format
        custom_response = {
            'error': True,
            'message': str(exc),
            'details': response.data if isinstance(response.data, dict) else {'detail': response.data},
            'status_code': response.status_code
        }
        response.data = custom_response

    return response
```

---

## 6. Constants and Choices

**File**: `core/constants.py`

**Implementation**:
```python
from django.db import models

class EmploymentStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    ON_LEAVE = 'ON_LEAVE', 'On Leave'
    TERMINATED = 'TERMINATED', 'Terminated'

class VacationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    DENIED = 'DENIED', 'Denied'
    CANCELLED = 'CANCELLED', 'Cancelled'

class NotificationType(models.TextChoices):
    VACATION_REQUEST = 'VACATION_REQUEST', 'Vacation Request'
    VACATION_APPROVED = 'VACATION_APPROVED', 'Vacation Approved'
    VACATION_DENIED = 'VACATION_DENIED', 'Vacation Denied'
    PROFILE_UPDATED = 'PROFILE_UPDATED', 'Profile Updated'

# Other constants
MAX_VACATION_DAYS_PER_YEAR = 30
MIN_ADVANCE_NOTICE_DAYS = 14
```

---

## 7. Mixins

### 7.1 UserCreatedMixin
**Purpose**: Automatically set created_by field from request

**Implementation**:
```python
class UserCreatedMixin:
    """Mixin to automatically set created_by from request."""

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

### 7.2 UserUpdatedMixin
**Purpose**: Automatically set updated_by field from request

**Implementation**:
```python
class UserUpdatedMixin:
    """Mixin to automatically set updated_by from request."""

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
```

---

## 8. File Structure

```
apps/core/
├── __init__.py
├── apps.py
├── admin.py
├── models.py              # Base abstract models
├── managers.py            # Custom managers and querysets
├── mixins.py              # Reusable mixins
├── constants.py           # Application constants and choices
├── exceptions.py          # Custom exception handler
├── middleware/
│   ├── __init__.py
│   ├── logging.py         # RequestLoggingMiddleware
│   └── timezone.py        # TimezoneMiddleware
├── utils/
│   ├── __init__.py
│   ├── date_utils.py      # Date and time utilities
│   ├── validators.py      # Custom validators
│   └── helpers.py         # General helper functions
├── templatetags/
│   ├── __init__.py
│   └── core_tags.py       # Custom template tags (if needed)
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_utils.py
    └── test_validators.py
```

---

## 9. Implementation Order

1. ✅ Create base abstract models (TimeStampedModel, SoftDeleteModel, AuditModel, BaseModel)
2. ✅ Create custom managers and querysets
3. ✅ Implement date utilities
4. ✅ Implement validators
5. ✅ Implement helper functions
6. ✅ Create middleware (RequestLogging, Timezone)
7. ✅ Create custom exception handler
8. ✅ Define constants and choices
9. ✅ Create mixins for DRF views
10. ✅ Write unit tests
11. ✅ Update settings to use middleware and exception handler

---

## 10. Testing Strategy

### Test Coverage:
- Base models (soft delete, audit trail)
- Date utilities (working days calculation)
- Validators (phone numbers, dates)
- Middleware (request logging)
- Helper functions

### Example Test:
```python
from django.test import TestCase
from datetime import date
from apps.core.utils.date_utils import (
    get_vacation_days_count,
    get_total_days_count,
    is_weekend,
    is_workable_day
)

class DateUtilsTestCase(TestCase):
    def test_vacation_days_weekdays_only(self):
        # Monday to Friday = 5 vacation days
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 7)    # Friday
        self.assertEqual(get_vacation_days_count(start, end), 5)

    def test_vacation_days_with_weekend(self):
        # Monday to Sunday = 5 vacation days (excludes Sat/Sun)
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 9)    # Sunday
        self.assertEqual(get_vacation_days_count(start, end), 5)

    def test_total_days_includes_weekend(self):
        # Monday to Sunday = 7 total calendar days
        start = date(2025, 11, 3)  # Monday
        end = date(2025, 11, 9)    # Sunday
        self.assertEqual(get_total_days_count(start, end), 7)

    def test_weekend_detection(self):
        saturday = date(2025, 11, 8)
        sunday = date(2025, 11, 9)
        monday = date(2025, 11, 10)
        self.assertTrue(is_weekend(saturday))
        self.assertTrue(is_weekend(sunday))
        self.assertFalse(is_weekend(monday))

    def test_workable_day_excludes_weekends(self):
        # Weekdays count as workable (vacation) days
        monday = date(2025, 11, 3)
        saturday = date(2025, 11, 8)
        self.assertTrue(is_workable_day(monday))
        self.assertFalse(is_workable_day(saturday))
```

---

## 11. Dependencies

**No additional packages needed** - All functionality uses Django/DRF built-ins and Python standard library.

---

## 12. Next Steps After Core App

Once the Core app is complete:
1. Update other apps to inherit from BaseModel
2. Use date utilities in Vacation app for working days calculation
3. Apply custom middleware in settings
4. Use validators across all models
5. Implement custom exception handler in REST API

---

## Success Criteria

- ✅ All base models created and tested
- ✅ Soft delete functionality working
- ✅ Date utilities calculating working days correctly
- ✅ Validators preventing invalid data
- ✅ Middleware logging requests properly
- ✅ 90%+ test coverage for core utilities
- ✅ Documentation complete
- ✅ Other apps can successfully use core functionality
