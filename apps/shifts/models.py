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

    def validate_skill_mix(self):
        """
        Validate that the shift has an appropriate skill mix.
        
        According to staffing guidelines, shifts must have:
        - At least 60% Registered Nurses (RN + Charge Nurse)
        - Maximum 40% CNAs
        
        Returns:
            bool: True if skill mix is valid
            
        Raises:
            ValidationError: If skill mix requirements are not met
        """
        assignments = self.assignments.filter(status='SCHEDULED')
        total_count = assignments.count()
        
        if total_count == 0:
            return True  # No assignments yet, nothing to validate
        
        # Count RNs (includes NURSE and CHARGE_NURSE roles)
        rn_count = assignments.filter(role__in=['NURSE', 'CHARGE_NURSE']).count()
        cna_count = assignments.filter(role='CNA').count()
        
        rn_percentage = (rn_count / total_count) * 100
        cna_percentage = (cna_count / total_count) * 100
        
        if rn_percentage < 60:
            raise ValidationError(
                f"Invalid skill mix: RN ratio is {rn_percentage:.0f}%, "
                f"minimum 60% required. Current: {rn_count} RN(s) of {total_count} staff."
            )
        
        if cna_percentage > 40:
            raise ValidationError(
                f"Invalid skill mix: CNA ratio is {cna_percentage:.0f}%, "
                f"maximum 40% allowed. Current: {cna_count} CNA(s) of {total_count} staff."
            )
        
        return True

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

    def validate_minimum_rest_period(self):
        """
        Validate that the employee has sufficient rest between shifts.
        
        According to EU Working Time Directive, employees must have a minimum
        of 11 consecutive hours of rest between shifts.
        
        Returns:
            bool: True if rest period is sufficient
            
        Raises:
            ValidationError: If rest period is less than 11 hours
        """
        MINIMUM_REST_HOURS = 11
        
        # Get shift start datetime
        shift_start = datetime.combine(self.shift.date, self.shift.start_time)
        
        # Find the most recent previous shift assignment for this employee
        previous_assignments = ShiftAssignment.objects.filter(
            employee=self.employee,
            status__in=[self.Status.SCHEDULED, self.Status.CONFIRMED]
        ).exclude(
            id=self.id if self.id else None
        ).select_related('shift')
        
        # Calculate when each previous shift ends and find the latest one before this shift
        latest_end = None
        
        for assignment in previous_assignments:
            prev_shift = assignment.shift
            prev_end = datetime.combine(prev_shift.date, prev_shift.end_time)
            
            # Handle overnight shifts (end time is next day)
            if prev_shift.end_time <= prev_shift.start_time:
                prev_end += timedelta(days=1)
            
            # Only consider shifts that end before this one starts
            if prev_end <= shift_start:
                if latest_end is None or prev_end > latest_end:
                    latest_end = prev_end
        
        if latest_end is None:
            # No previous shifts found
            return True
        
        # Calculate rest period
        rest_period = shift_start - latest_end
        rest_hours = rest_period.total_seconds() / 3600
        
        if rest_hours < MINIMUM_REST_HOURS:
            raise ValidationError(
                f"Insufficient rest period: {rest_hours:.1f} hours between shifts. "
                f"EU Working Time Directive requires minimum 11 hours rest period."
            )
        
        return True

    def validate_certification_requirements(self):
        """
        Validate that the employee has required certifications for this assignment.
        
        Requirements:
        - All nursing staff must have valid BLS (Basic Life Support) certification
        - Charge Nurses must have at least 5 years of experience
        
        Returns:
            bool: True if all certification requirements are met
            
        Raises:
            ValidationError: If required certifications are missing or invalid
        """
        from apps.employees.models import EmployeeQualification
        
        # Check for CHARGE_NURSE experience requirement
        if self.role == self.Role.CHARGE_NURSE:
            years_of_service = self.employee.years_of_service
            if years_of_service is None or years_of_service < 5:
                raise ValidationError(
                    f"Charge Nurse role requires minimum 5 years of experience. "
                    f"Employee has {years_of_service or 0} years."
                )
        
        # Check for required BLS certification for nursing roles
        if self.role in [self.Role.NURSE, self.Role.CHARGE_NURSE, self.Role.CNA]:
            # Check if employee has active BLS certification
            has_valid_bls = EmployeeQualification.objects.filter(
                employee=self.employee,
                qualification__code='BLS',
                status__in=[
                    EmployeeQualification.CertificationStatus.ACTIVE,
                    EmployeeQualification.CertificationStatus.EXPIRING_SOON
                ]
            ).exists()
            
            if not has_valid_bls:
                raise ValidationError(
                    f"Employee {self.employee.get_full_name()} is missing required "
                    f"BLS (Basic Life Support) certification for {self.get_role_display()} role."
                )
        
        return True

    def validate_max_consecutive_nights(self):
        """
        Validate that the employee does not exceed maximum consecutive night shifts.
        
        According to health and safety guidelines, staff should not work more
        than 4 consecutive night shifts to prevent fatigue-related errors.
        
        Returns:
            bool: True if consecutive nights limit is not exceeded
            
        Raises:
            ValidationError: If this assignment would exceed 4 consecutive nights
        """
        MAX_CONSECUTIVE_NIGHTS = 4
        
        # Only applies to night shifts
        if self.shift.shift_type != Shift.ShiftType.NIGHT:
            return True
        
        shift_date = self.shift.date
        
        # Fetch all relevant night assignments around this date in a single query
        window_start = shift_date - timedelta(days=MAX_CONSECUTIVE_NIGHTS)
        window_end = shift_date + timedelta(days=MAX_CONSECUTIVE_NIGHTS)

        night_assignments = (
            ShiftAssignment.objects.filter(
                employee=self.employee,
                shift__date__range=(window_start, window_end),
                shift__shift_type=Shift.ShiftType.NIGHT,
                status__in=[self.Status.SCHEDULED, self.Status.CONFIRMED],
            )
            .exclude(id=self.id if self.id else None)
        )

        # Build a set of dates where the employee already has a qualifying night shift
        night_dates = {
            assignment.shift.date
            for assignment in night_assignments
        }
        
        # Count consecutive night shifts before this one
        consecutive_before = 0
        check_date = shift_date - timedelta(days=1)
        
        while (
            consecutive_before < MAX_CONSECUTIVE_NIGHTS
            and check_date in night_dates
        ):
            consecutive_before += 1
            check_date -= timedelta(days=1)
        
        # Count consecutive night shifts after this one
        consecutive_after = 0
        check_date = shift_date + timedelta(days=1)
        
        while (
            consecutive_after < MAX_CONSECUTIVE_NIGHTS
            and check_date in night_dates
        ):
            consecutive_after += 1
            check_date += timedelta(days=1)
        
        # Total consecutive nights including this assignment
        total_consecutive = consecutive_before + 1 + consecutive_after
        
        if total_consecutive > MAX_CONSECUTIVE_NIGHTS:
            raise ValidationError(
                f"Cannot assign {total_consecutive} consecutive night shifts. "
                f"Maximum allowed is {MAX_CONSECUTIVE_NIGHTS} consecutive nights "
                f"to prevent fatigue-related errors."
            )
        
        return True


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
