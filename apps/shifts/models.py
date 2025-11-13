"""
Shift scheduling models for ICU workforce management
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from apps.employees.models import BaseModel
from apps.locations.models import Location

User = get_user_model()


class Shift(BaseModel):
    """
    Represents a single shift that needs to be staffed.
    Shifts are created by managers and assigned to employees.
    """

    class ShiftType(models.TextChoices):
        DAY = 'DAY', 'Day Shift (07:00-19:00)'
        NIGHT = 'NIGHT', 'Night Shift (19:00-07:00)'
        ON_CALL = 'ON_CALL', 'On-Call'

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='shifts',
        help_text="Location where this shift takes place"
    )
    shift_type = models.CharField(
        max_length=20,
        choices=ShiftType.choices,
        help_text="Type of shift"
    )
    start_time = models.TimeField(help_text="Shift start time")
    end_time = models.TimeField(help_text="Shift end time")
    date = models.DateField(help_text="Date of the shift", db_index=True)

    # Staffing requirements
    required_staff_count = models.IntegerField(
        help_text="Minimum total staff required for this shift"
    )
    required_rn_count = models.IntegerField(
        default=0,
        help_text="Minimum registered nurses required (RN)"
    )
    required_charge_nurse = models.BooleanField(
        default=False,
        help_text="Whether a charge nurse is required for this shift"
    )

    notes = models.TextField(blank=True, help_text="Additional notes about the shift")
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether staff can see this shift (false = draft)"
    )

    class Meta:
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['date', 'location']),
            models.Index(fields=['shift_type', 'date']),
            models.Index(fields=['is_published']),
        ]
        unique_together = ['location', 'date', 'start_time', 'shift_type']

    def __str__(self):
        return f"{self.get_shift_type_display()} - {self.location.name} - {self.date}"

    def get_duration_hours(self):
        """Calculate shift duration in hours"""
        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)

        # Handle overnight shifts
        if end <= start:
            end += timedelta(days=1)

        duration = end - start
        return duration.total_seconds() / 3600

    def get_assigned_count(self):
        """Get number of employees assigned to this shift"""
        return self.assignments.filter(status='SCHEDULED').count()

    def get_rn_count(self):
        """Get number of RNs assigned"""
        return self.assignments.filter(
            status='SCHEDULED',
            role__in=['NURSE', 'CHARGE_NURSE']
        ).count()

    def has_charge_nurse(self):
        """Check if a charge nurse is assigned"""
        return self.assignments.filter(
            status='SCHEDULED',
            role='CHARGE_NURSE'
        ).exists()

    def is_fully_staffed(self):
        """Check if shift meets all staffing requirements"""
        if self.get_assigned_count() < self.required_staff_count:
            return False
        if self.get_rn_count() < self.required_rn_count:
            return False
        if self.required_charge_nurse and not self.has_charge_nurse():
            return False
        return True

    def get_coverage_percentage(self):
        """Calculate staffing coverage as percentage"""
        if self.required_staff_count == 0:
            return 100
        return int((self.get_assigned_count() / self.required_staff_count) * 100)

    def clean(self):
        """Validate shift data"""
        if self.required_rn_count > self.required_staff_count:
            raise ValidationError(
                "Required RN count cannot exceed total required staff count"
            )


class ShiftAssignment(BaseModel):
    """
    Junction model representing an employee assigned to a shift.
    Tracks who is scheduled to work when and in what capacity.
    """

    class Role(models.TextChoices):
        NURSE = 'NURSE', 'Registered Nurse (RN)'
        CHARGE_NURSE = 'CHARGE_NURSE', 'Charge Nurse'
        CNA = 'CNA', 'Certified Nursing Assistant'
        ON_CALL = 'ON_CALL', 'On-Call Staff'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        CONFIRMED = 'CONFIRMED', 'Confirmed by Employee'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No Show'

    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shift_assignments'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        help_text="Role for this shift"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_made',
        help_text="Manager who made this assignment"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['shift', 'status']),
        ]
        unique_together = ['shift', 'employee']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.shift}"

    def calculate_hours(self):
        """Calculate hours worked for this assignment"""
        if self.status not in [self.Status.SCHEDULED, self.Status.CONFIRMED]:
            return 0
        return self.shift.get_duration_hours()

    def conflicts_with_other_shifts(self):
        """
        Check if this assignment conflicts with other shifts for the same employee.
        Returns list of conflicting assignments.
        """
        # Get shift datetime range
        shift_start = datetime.combine(self.shift.date, self.shift.start_time)
        shift_end = datetime.combine(self.shift.date, self.shift.end_time)
        if shift_end <= shift_start:
            shift_end += timedelta(days=1)

        # Find overlapping shifts
        same_day_assignments = ShiftAssignment.objects.filter(
            employee=self.employee,
            status=self.Status.SCHEDULED,
            shift__date=self.shift.date
        )
        if self.id is not None:
            same_day_assignments = same_day_assignments.exclude(id=self.id)
        same_day_assignments = same_day_assignments.select_related('shift')

        conflicts = []
        for assignment in same_day_assignments:
            other_start = datetime.combine(
                assignment.shift.date,
                assignment.shift.start_time
            )
            other_end = datetime.combine(
                assignment.shift.date,
                assignment.shift.end_time
            )
            if other_end <= other_start:
                other_end += timedelta(days=1)

            # Check if time ranges overlap
            if shift_start < other_end and shift_end > other_start:
                conflicts.append(assignment)

        return conflicts


class ShiftTemplate(BaseModel):
    """
    Template for creating recurring shift patterns.
    Used to quickly generate shifts based on a standardized pattern.
    """

    name = models.CharField(max_length=200, help_text="Template name")
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='shift_templates'
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ],
        help_text="Day of week (0=Monday, 6=Sunday)"
    )
    shift_type = models.CharField(
        max_length=20,
        choices=Shift.ShiftType.choices
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    required_staff_count = models.IntegerField()
    required_rn_count = models.IntegerField(default=0)
    required_charge_nurse = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        indexes = [
            models.Index(fields=['location', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_day_of_week_display()}"

    def create_shift(self, date):
        """Create a Shift instance from this template for a specific date"""
        return Shift.objects.create(
            location=self.location,
            shift_type=self.shift_type,
            start_time=self.start_time,
            end_time=self.end_time,
            date=date,
            required_staff_count=self.required_staff_count,
            required_rn_count=self.required_rn_count,
            required_charge_nurse=self.required_charge_nurse,
            is_published=False,  # Templates create draft shifts
            created_by=self.created_by
        )
