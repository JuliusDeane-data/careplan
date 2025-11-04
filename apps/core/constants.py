"""
Constants and choices for the Careplan project.
"""

from django.db import models


class EmploymentStatus(models.TextChoices):
    """Employment status choices for employees."""
    ACTIVE = 'ACTIVE', 'Active'
    ON_LEAVE = 'ON_LEAVE', 'On Leave'
    TERMINATED = 'TERMINATED', 'Terminated'


class VacationStatus(models.TextChoices):
    """Vacation request status choices."""
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    DENIED = 'DENIED', 'Denied'
    CANCELLED = 'CANCELLED', 'Cancelled'


class NotificationType(models.TextChoices):
    """Notification type choices."""
    VACATION_REQUEST_SUBMITTED = 'VACATION_REQUEST_SUBMITTED', 'Vacation Request Submitted'
    VACATION_REQUEST_APPROVED = 'VACATION_REQUEST_APPROVED', 'Vacation Request Approved'
    VACATION_REQUEST_DENIED = 'VACATION_REQUEST_DENIED', 'Vacation Request Denied'
    VACATION_REQUEST_MODIFIED = 'VACATION_REQUEST_MODIFIED', 'Vacation Request Modified'
    VACATION_REQUEST_CANCELLED = 'VACATION_REQUEST_CANCELLED', 'Vacation Request Cancelled'
    SHIFT_ASSIGNED = 'SHIFT_ASSIGNED', 'Shift Assigned'
    SHIFT_MODIFIED = 'SHIFT_MODIFIED', 'Shift Modified'
    PROFILE_UPDATED = 'PROFILE_UPDATED', 'Profile Updated'
    SYSTEM_MESSAGE = 'SYSTEM_MESSAGE', 'System Message'


# Vacation constants
MAX_VACATION_DAYS_PER_YEAR = 30
MIN_ADVANCE_NOTICE_DAYS = 14  # Minimum days in advance to request vacation

# Location constants
MAX_LOCATION_CAPACITY = 200  # Maximum number of employees per location
MIN_STAFF_COVERAGE_PERCENTAGE = 70  # Minimum % of staff required on-site

# Pagination constants
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# File upload constants
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']

# Time constants
SESSION_COOKIE_AGE_DAYS = 7
TOKEN_EXPIRY_HOURS = 24
PASSWORD_RESET_TIMEOUT_HOURS = 1
