"""
Django admin configuration for Accounts app.
User model now contains all employee fields.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User/Employee model."""

    list_display = [
        'username', 'employee_id', 'get_full_name', 'email',
        'role', 'job_title', 'employment_status', 'primary_location', 'is_active'
    ]
    list_filter = [
        'role', 'employment_status', 'employment_type',
        'primary_location', 'is_staff', 'is_active', 'gender'
    ]
    search_fields = [
        'username', 'employee_id', 'first_name', 'last_name',
        'email', 'job_title', 'phone'
    ]
    readonly_fields = ['remaining_vacation_days', 'last_login', 'date_joined']
    filter_horizontal = ['groups', 'user_permissions', 'qualifications', 'additional_locations']
    ordering = ['employee_id']

    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'password', 'email')
        }),
        ('Personal Information', {
            'fields': (
                'first_name', 'last_name', 'employee_id',
                'date_of_birth', 'gender', 'nationality',
                'profile_picture'
            )
        }),
        ('Contact Information', {
            'fields': (
                'phone', 'address', 'city', 'postal_code', 'country',
                'emergency_contact_name', 'emergency_contact_phone'
            )
        }),
        ('Employment Details', {
            'fields': (
                'role', 'hire_date', 'employment_status', 'employment_type',
                'job_title', 'department', 'contract_hours_per_week',
                'termination_date', 'termination_reason'
            )
        }),
        ('Location & Reporting', {
            'fields': (
                'primary_location', 'additional_locations',
                'supervisor', 'qualifications'
            )
        }),
        ('Vacation Information', {
            'fields': ('annual_vacation_days', 'remaining_vacation_days')
        }),
        ('Salary Information', {
            'fields': ('hourly_rate', 'monthly_salary', 'currency'),
            'classes': ('collapse',),
            'description': 'Sensitive salary information - restricted access'
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Employee Information', {
            'classes': ('wide',),
            'fields': ('employee_id', 'first_name', 'last_name', 'role'),
        }),
    )

    def get_full_name(self, obj):
        """Display user's full name."""
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'
