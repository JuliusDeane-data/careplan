"""
Location models for the Careplan project.
"""

from django.db import models
from apps.core.models import BaseModel
from apps.core.utils.validators import validate_phone_number, validate_postal_code


class Location(BaseModel):
    """
    Location model representing care facility locations.
    """
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=10,
        validators=[validate_postal_code]
    )
    country = models.CharField(max_length=50, default='Germany')
    phone = models.CharField(
        max_length=20,
        validators=[validate_phone_number]
    )
    email = models.EmailField(blank=True)
    max_capacity = models.IntegerField(
        default=50,
        help_text='Maximum number of patients/residents'
    )
    manager = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_locations',
        help_text='Manager responsible for this location'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this location is currently active'
    )

    class Meta:
        db_table = 'locations'
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city}"

    def get_employee_count(self):
        """Get the number of employees assigned to this location."""
        from apps.accounts.models import User
        return self.primary_employees.filter(
            employment_status=User.EmploymentStatus.ACTIVE
        ).count()
