"""
Django admin configuration for Locations app.
"""

from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin interface for Location model."""
    list_display = ['name', 'city', 'max_capacity', 'is_active', 'created_at']
    list_filter = ['is_active', 'city', 'country']
    search_fields = ['name', 'city', 'address', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'max_capacity', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'postal_code', 'country', 'phone', 'email')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
