"""
Vacation management models for the Careplan project.
Handles vacation requests, approvals, and public holidays.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.constants import VacationStatus, MIN_ADVANCE_NOTICE_DAYS
from apps.core.utils.date_utils import get_vacation_days_count, get_total_days_count


class RequestType(models.TextChoices):
    """Vacation request type choices."""
    ANNUAL_LEAVE = 'ANNUAL_LEAVE', 'Annual Leave'
    SICK_LEAVE = 'SICK_LEAVE', 'Sick Leave'
    UNPAID_LEAVE = 'UNPAID_LEAVE', 'Unpaid Leave'
    PARENTAL_LEAVE = 'PARENTAL_LEAVE', 'Parental Leave'
    BEREAVEMENT_LEAVE = 'BEREAVEMENT_LEAVE', 'Bereavement Leave'
    OTHER = 'OTHER', 'Other'


class PublicHoliday(BaseModel):
    """
    Public holidays that are excluded from vacation day calculations.
    Can be nationwide or location-specific.
    """

    date = models.DateField(
        db_index=True,
        help_text='Holiday date'
    )
    name = models.CharField(
        max_length=100,
        help_text='Holiday name (e.g., Christmas, New Year)'
    )
    description = models.TextField(
        blank=True,
        help_text='Optional description'
    )

    # Location-specific or national
    location = models.ForeignKey(
        'locations.Location',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='holidays',
        help_text='Specific location, or null for nationwide holiday'
    )
    is_nationwide = models.BooleanField(
        default=True,
        help_text='True if applies to all locations'
    )

    # Recurring holidays (e.g., Christmas on Dec 25 every year)
    is_recurring = models.BooleanField(
        default=False,
        help_text='If true, holiday repeats annually'
    )
    recurring_month = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 13)],
        help_text='Month (1-12) for recurring holidays'
    )
    recurring_day = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 32)],
        help_text='Day of month for recurring holidays'
    )

    class Meta:
        db_table = 'public_holidays'
        verbose_name = 'Public Holiday'
        verbose_name_plural = 'Public Holidays'
        ordering = ['date']
        unique_together = [['date', 'location']]
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['location', 'date']),
            models.Index(fields=['is_nationwide']),
        ]

    def __str__(self):
        location_str = self.location.name if self.location else 'Nationwide'
        return f"{self.name} - {self.date} ({location_str})"

    @classmethod
    def get_holidays_for_year(cls, year, location=None):
        """
        Get all holidays for a specific year and location.

        Args:
            year: Year to get holidays for
            location: Optional location (if None, gets national holidays only)

        Returns:
            QuerySet of PublicHoliday objects
        """
        from datetime import date
        start = date(year, 1, 1)
        end = date(year, 12, 31)

        query = cls.objects.filter(date__range=(start, end))
        if location:
            query = query.filter(
                models.Q(location=location) | models.Q(is_nationwide=True)
            )
        else:
            query = query.filter(is_nationwide=True)

        return query

    @classmethod
    def is_holiday(cls, date_obj, location=None):
        """
        Check if a specific date is a public holiday.

        Args:
            date_obj: Date to check
            location: Optional location

        Returns:
            Boolean
        """
        query = cls.objects.filter(date=date_obj)
        if location:
            query = query.filter(
                models.Q(location=location) | models.Q(is_nationwide=True)
            )
        else:
            query = query.filter(is_nationwide=True)

        return query.exists()


class VacationRequest(BaseModel):
    """
    Vacation request with approval workflow and balance tracking.
    """

    # Employee requesting vacation
    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='vacation_requests',
        help_text='Employee requesting vacation'
    )

    # Date range
    start_date = models.DateField(
        db_index=True,
        help_text='First day of vacation (inclusive)'
    )
    end_date = models.DateField(
        help_text='Last day of vacation (inclusive)'
    )

    # Auto-calculated fields
    vacation_days = models.IntegerField(
        default=0,
        help_text='Vacation days (weekdays only, excludes weekends/holidays)'
    )
    total_days = models.IntegerField(
        default=0,
        help_text='Total calendar days'
    )

    # Request details
    request_type = models.CharField(
        max_length=20,
        choices=RequestType.choices,
        default=RequestType.ANNUAL_LEAVE,
        help_text='Type of leave request'
    )
    reason = models.TextField(
        blank=True,
        help_text='Optional reason for request'
    )
    notes = models.TextField(
        blank=True,
        help_text='Internal notes (visible to managers)'
    )

    # Supporting documents (e.g., medical certificates for sick leave)
    supporting_document = models.FileField(
        upload_to='vacation_documents/',
        null=True,
        blank=True,
        help_text='Supporting document (e.g., medical certificate)'
    )

    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=VacationStatus.choices,
        default=VacationStatus.PENDING,
        db_index=True,
        help_text='Current status of the request'
    )

    # Approval tracking
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_vacation_requests',
        help_text='Manager who approved this request'
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When request was approved'
    )

    # Denial tracking
    denied_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='denied_vacation_requests',
        help_text='Manager who denied this request'
    )
    denied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When request was denied'
    )
    denial_reason = models.TextField(
        blank=True,
        help_text='Reason for denial'
    )

    # Cancellation tracking
    cancelled_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_vacation_requests',
        help_text='Who cancelled this request'
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When request was cancelled'
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text='Reason for cancellation'
    )

    class Meta:
        db_table = 'vacation_requests'
        verbose_name = 'Vacation Request'
        verbose_name_plural = 'Vacation Requests'
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['status']),
            models.Index(fields=['approved_by']),
        ]

    def __str__(self):
        return f"{self.employee.employee_id} - {self.start_date} to {self.end_date} ({self.get_status_display()})"

    def clean(self):
        """Validate vacation request."""
        errors = {}

        # Rule 1: End date must be >= start date
        if self.start_date and self.end_date and self.end_date < self.start_date:
            errors['end_date'] = 'End date must be after or equal to start date'

        # Rule 2: Cannot request vacation in the past
        today = timezone.now().date()
        if self.start_date and self.start_date < today:
            errors['start_date'] = 'Cannot request vacation in the past'

        # Rule 3: Minimum advance notice
        if self.start_date:
            days_until = (self.start_date - today).days
            if days_until < MIN_ADVANCE_NOTICE_DAYS:
                errors['start_date'] = f'Vacation must be requested at least {MIN_ADVANCE_NOTICE_DAYS} days in advance (requested {days_until} days in advance)'

        # Rule 4: No overlapping vacation requests
        if self.employee_id and self.start_date and self.end_date:
            overlapping = VacationRequest.objects.filter(
                employee=self.employee,
                status__in=[VacationStatus.PENDING, VacationStatus.APPROVED]
            ).filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            ).exclude(pk=self.pk)

            if overlapping.exists():
                first_overlap = overlapping.first()
                errors['start_date'] = f'Overlaps with existing request from {first_overlap.start_date} to {first_overlap.end_date}'

        # Rule 5: Sufficient vacation days (for ANNUAL_LEAVE only)
        if self.request_type == RequestType.ANNUAL_LEAVE and self.employee_id and self.start_date and self.end_date:
            vacation_days = get_vacation_days_count(
                self.start_date,
                self.end_date,
                location=self.employee.primary_location
            )

            # Check remaining balance
            if vacation_days > self.employee.remaining_vacation_days:
                errors['end_date'] = f'Insufficient vacation days. Requested: {vacation_days}, Available: {self.employee.remaining_vacation_days}'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Auto-calculate vacation days and total days."""
        if self.start_date and self.end_date:
            # Auto-calculate vacation days (weekdays only, excludes holidays)
            self.vacation_days = get_vacation_days_count(
                self.start_date,
                self.end_date,
                location=self.employee.primary_location if self.employee_id else None
            )
            # Auto-calculate total calendar days
            self.total_days = get_total_days_count(
                self.start_date,
                self.end_date
            )

        super().save(*args, **kwargs)

    # Status check properties
    @property
    def is_pending(self):
        """Check if request is pending."""
        return self.status == VacationStatus.PENDING

    @property
    def is_approved(self):
        """Check if request is approved."""
        return self.status == VacationStatus.APPROVED

    @property
    def is_denied(self):
        """Check if request is denied."""
        return self.status == VacationStatus.DENIED

    @property
    def is_cancelled(self):
        """Check if request is cancelled."""
        return self.status == VacationStatus.CANCELLED

    @property
    def is_in_past(self):
        """Check if vacation is in the past."""
        today = timezone.now().date()
        return self.end_date < today

    @property
    def is_current(self):
        """Check if vacation is currently active."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def is_future(self):
        """Check if vacation is in the future."""
        today = timezone.now().date()
        return self.start_date > today

    # Workflow methods
    def is_modifiable(self):
        """Check if request can be modified."""
        return self.status == VacationStatus.PENDING and self.is_future

    def is_cancellable(self):
        """Check if request can be cancelled."""
        return self.status in [VacationStatus.PENDING, VacationStatus.APPROVED] and not self.is_in_past

    def days_until_start(self):
        """Calculate days until vacation starts."""
        if not self.start_date:
            return None
        today = timezone.now().date()
        return (self.start_date - today).days

    # Action methods
    def approve(self, approved_by):
        """
        Approve the vacation request.

        Args:
            approved_by: User who is approving the request
        """
        if self.status != VacationStatus.PENDING:
            raise ValidationError('Only pending requests can be approved')

        self.status = VacationStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()

    def deny(self, denied_by, reason=''):
        """
        Deny the vacation request.

        Args:
            denied_by: User who is denying the request
            reason: Reason for denial
        """
        if self.status != VacationStatus.PENDING:
            raise ValidationError('Only pending requests can be denied')

        self.status = VacationStatus.DENIED
        self.denied_by = denied_by
        self.denied_at = timezone.now()
        self.denial_reason = reason
        self.save()

    def cancel(self, cancelled_by, reason=''):
        """
        Cancel the vacation request.

        Args:
            cancelled_by: User who is cancelling the request
            reason: Reason for cancellation
        """
        if not self.is_cancellable():
            raise ValidationError('This request cannot be cancelled')

        # Store previous status to know if we need to restore balance
        was_approved = self.status == VacationStatus.APPROVED

        self.status = VacationStatus.CANCELLED
        self.cancelled_by = cancelled_by
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()

        # Restore balance if it was approved (handled by signal)
        return was_approved
