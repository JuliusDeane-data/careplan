"""
Django admin configuration for Employees app.
Employee data is now in User model (apps.accounts.User).
This admin only handles Qualifications and Documents.
"""

from django.contrib import admin
from .models import Qualification, EmployeeDocument


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    """Admin interface for Qualification model."""
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'required_for_roles', 'is_active')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    """Admin interface for EmployeeDocument model."""
    list_display = [
        'employee', 'document_type', 'title',
        'expiry_date', 'is_expired', 'created_at'
    ]
    list_filter = ['document_type', 'expiry_date']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name', 'title']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Document Information', {
            'fields': ('employee', 'document_type', 'title', 'file', 'expiry_date', 'notes')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def is_expired(self, obj):
        """Display if document is expired."""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
