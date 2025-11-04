"""
User/Employee model for the Careplan project.
User model now includes all employee fields - no separate Employee model needed.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import date
from apps.core.utils.validators import validate_phone_number, validate_postal_code


class User(AbstractUser):
    """
    Custom User model that serves as both authentication and employee profile.
    All users in the system are employees with different roles.
    """

    class Role(models.TextChoices):
        """User role choices for permissions."""
        EMPLOYEE = 'EMPLOYEE', 'Employee'
        MANAGER = 'MANAGER', 'Manager'
        ADMIN = 'ADMIN', 'Admin'

    class EmploymentStatus(models.TextChoices):
        """Employment status choices."""
        ACTIVE = 'ACTIVE', 'Active'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'
        TERMINATED = 'TERMINATED', 'Terminated'

    class EmploymentType(models.TextChoices):
        """Employment type choices."""
        FULL_TIME = 'FULL_TIME', 'Full Time'
        PART_TIME = 'PART_TIME', 'Part Time'
        CONTRACT = 'CONTRACT', 'Contract'
        TEMPORARY = 'TEMPORARY', 'Temporary'

    class Gender(models.TextChoices):
        """Gender choices."""
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'
        PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'

    # Override email to make it unique and required
    email = models.EmailField(
        unique=True,
        help_text='Email address for login and notifications'
    )

    # Role and permissions
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        help_text='User role for permissions',
        db_index=True
    )

    # Employee identification
    employee_id = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
        help_text='Unique employee identifier (e.g., EMP001)'
    )

    # Personal information
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Date of birth'
    )
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_SAY,
        blank=True
    )
    nationality = models.CharField(max_length=50, blank=True)

    # Contact information
    phone = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        blank=True,
        help_text='Primary phone number'
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        blank=True
    )
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(
        max_length=10,
        validators=[validate_postal_code],
        blank=True
    )
    country = models.CharField(max_length=50, default='Germany', blank=True)

    # Employment information
    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when employee was hired'
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        db_index=True
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        blank=True
    )
    job_title = models.CharField(
        max_length=100,
        blank=True,
        help_text='e.g., Care Worker, Nurse, Care Manager'
    )
    department = models.CharField(max_length=100, blank=True)
    contract_hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00,
        help_text='Contracted weekly hours'
    )
    termination_date = models.DateField(null=True, blank=True)
    termination_reason = models.TextField(blank=True)

    # Location relationships (temporarily commented out to avoid circular dependency in migrations)
    # Will be added back in migration 0002
    # primary_location = models.ForeignKey(
    #     'locations.Location',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='primary_employees',
    #     help_text='Primary work location'
    # )
    # additional_locations = models.ManyToManyField(
    #     'locations.Location',
    #     related_name='additional_employees',
    #     blank=True,
    #     help_text='Additional locations where employee can work'
    # )

    # Supervisor relationship (self-referential)
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_employees',
        help_text='Direct supervisor'
    )

    # Qualifications
    qualifications = models.ManyToManyField(
        'employees.Qualification',
        related_name='employees',
        blank=True,
        help_text='Employee qualifications and certifications'
    )

    # Vacation information
    annual_vacation_days = models.IntegerField(
        default=30,
        help_text='Total vacation days per year'
    )
    remaining_vacation_days = models.IntegerField(
        default=30,
        help_text='Remaining vacation days for current year'
    )

    # Salary information (sensitive)
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Hourly rate for hourly employees'
    )
    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly salary for salaried employees'
    )
    currency = models.CharField(max_length=3, default='EUR')

    # Additional fields
    notes = models.TextField(
        blank=True,
        help_text='Internal HR notes'
    )
    profile_picture = models.ImageField(
        upload_to='employee_photos/',
        null=True,
        blank=True,
        help_text='Employee photo'
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'User/Employee'
        verbose_name_plural = 'Users/Employees'
        ordering = ['employee_id']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['role']),
            models.Index(fields=['employment_status']),
            # models.Index(fields=['primary_location']),  # Will be added in migration 0002
        ]

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()} ({self.role})"

    # Role permission methods
    def is_employee(self):
        """Check if user has employee role."""
        return self.role == self.Role.EMPLOYEE

    def is_manager(self):
        """Check if user has manager role."""
        return self.role == self.Role.MANAGER

    def is_admin_role(self):
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN

    # Employee-related methods
    def get_age(self):
        """Calculate current age from date of birth."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) <
            (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def age(self):
        """Property for age."""
        return self.get_age()

    def get_years_of_service(self):
        """Calculate years of service since hire date."""
        if not self.hire_date:
            return None
        today = date.today()
        return today.year - self.hire_date.year - (
            (today.month, today.day) <
            (self.hire_date.month, self.hire_date.day)
        )

    @property
    def years_of_service(self):
        """Property for years of service."""
        return self.get_years_of_service()

    def is_active_employee(self):
        """Check if employee is currently active."""
        return self.employment_status == self.EmploymentStatus.ACTIVE and self.is_active

    def can_work_at_location(self, location):
        """
        Check if employee can work at a specific location.

        Args:
            location: Location object to check

        Returns:
            bool: True if employee can work at location
        """
        # Temporarily disabled until location fields are added in migration 0002
        # if not location:
        #     return False
        # return (
        #     self.primary_location == location or
        #     location in self.additional_locations.all()
        # )
        return False  # Placeholder

    def update_vacation_balance(self):
        """
        Recalculate remaining vacation days based on approved requests.
        This is called via signal when vacation requests change.
        """
        try:
            from apps.vacation.models import VacationRequest

            # Get current year's approved vacation days
            year = timezone.now().year
            used_days = VacationRequest.objects.filter(
                employee=self,
                status='APPROVED',
                start_date__year=year
            ).aggregate(
                total=models.Sum('total_days')
            )['total'] or 0

            self.remaining_vacation_days = self.annual_vacation_days - used_days
            self.save(update_fields=['remaining_vacation_days'])
        except ImportError:
            # VacationRequest model not yet created
            pass
