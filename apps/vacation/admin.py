"""
Django admin configuration for vacation app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import VacationRequest, PublicHoliday, RequestType
from apps.core.constants import VacationStatus


@admin.register(VacationRequest)
class VacationRequestAdmin(admin.ModelAdmin):
    """Admin interface for vacation requests."""

    list_display = [
        'id',
        'employee_display',
        'request_type',
        'start_date',
        'end_date',
        'vacation_days',
        'status_display',
        'approved_by',
        'created_at',
    ]

    list_filter = [
        'status',
        'request_type',
        'start_date',
        'approved_by',
        'created_at',
    ]

    search_fields = [
        'employee__username',
        'employee__employee_id',
        'employee__first_name',
        'employee__last_name',
        'reason',
    ]

    readonly_fields = [
        'vacation_days',
        'total_days',
        'approved_at',
        'approved_by',
        'denied_at',
        'denied_by',
        'cancelled_at',
        'cancelled_by',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]

    autocomplete_fields = [
        'employee',
    ]

    date_hierarchy = 'start_date'

    list_per_page = 50

    fieldsets = (
        ('Request Details', {
            'fields': (
                'employee',
                'request_type',
                'start_date',
                'end_date',
                'vacation_days',
                'total_days',
                'reason',
            )
        }),
        ('Status', {
            'fields': (
                'status',
            )
        }),
        ('Approval Information', {
            'fields': (
                'approved_by',
                'approved_at',
            ),
            'classes': ('collapse',),
        }),
        ('Denial Information', {
            'fields': (
                'denied_by',
                'denied_at',
                'denial_reason',
            ),
            'classes': ('collapse',),
        }),
        ('Cancellation Information', {
            'fields': (
                'cancelled_by',
                'cancelled_at',
                'cancellation_reason',
            ),
            'classes': ('collapse',),
        }),
        ('Supporting Documents', {
            'fields': ('supporting_document',),
            'classes': ('collapse',),
        }),
        ('Internal Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
        ('Audit Trail', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
            ),
            'classes': ('collapse',),
        }),
    )

    actions = ['approve_requests', 'deny_requests', 'cancel_requests']

    def employee_display(self, obj):
        """Display employee with employee ID."""
        return f"{obj.employee.employee_id} - {obj.employee.get_full_name()}"
    employee_display.short_description = 'Employee'
    employee_display.admin_order_field = 'employee__employee_id'

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            VacationStatus.PENDING: 'orange',
            VacationStatus.APPROVED: 'green',
            VacationStatus.DENIED: 'red',
            VacationStatus.CANCELLED: 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'

    def approve_requests(self, request, queryset):
        """Bulk action to approve vacation requests."""
        count = 0
        errors = []

        for vacation_request in queryset.filter(status=VacationStatus.PENDING):
            try:
                vacation_request.approve(approved_by=request.user)
                count += 1
            except ValidationError as e:
                errors.append(f"{vacation_request.id}: {str(e)}")

        self.message_user(request, f'{count} request(s) approved.')
        if errors:
            self.message_user(request, f'Errors: {"; ".join(errors)}', level='ERROR')

    approve_requests.short_description = 'Approve selected requests'

    def deny_requests(self, request, queryset):
        """Bulk action to deny vacation requests."""
        count = 0
        errors = []

        for vacation_request in queryset.filter(status=VacationStatus.PENDING):
            try:
                vacation_request.deny(
                    denied_by=request.user,
                    reason='Denied via bulk action'
                )
                count += 1
            except ValidationError as e:
                errors.append(f"{vacation_request.id}: {str(e)}")

        self.message_user(request, f'{count} request(s) denied.')
        if errors:
            self.message_user(request, f'Errors: {"; ".join(errors)}', level='ERROR')

    deny_requests.short_description = 'Deny selected requests'

    def cancel_requests(self, request, queryset):
        """Bulk action to cancel vacation requests."""
        count = 0
        errors = []

        for vacation_request in queryset:
            if vacation_request.is_cancellable():
                try:
                    vacation_request.cancel(
                        cancelled_by=request.user,
                        reason='Cancelled via bulk action'
                    )
                    count += 1
                except ValidationError as e:
                    errors.append(f"{vacation_request.id}: {str(e)}")

        self.message_user(request, f'{count} request(s) cancelled.')
        if errors:
            self.message_user(request, f'Errors: {"; ".join(errors)}', level='ERROR')

    cancel_requests.short_description = 'Cancel selected requests'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'employee',
            'approved_by',
            'denied_by',
            'cancelled_by',
            'created_by',
            'updated_by'
        )


@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    """Admin interface for public holidays."""

    list_display = [
        'date',
        'name',
        'location_display',
        'is_nationwide',
        'is_recurring',
        'created_at',
    ]

    list_filter = [
        'is_nationwide',
        'is_recurring',
        'location',
        'date',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]

    autocomplete_fields = ['location']

    date_hierarchy = 'date'

    list_per_page = 50

    fieldsets = (
        ('Holiday Details', {
            'fields': (
                'name',
                'date',
                'description',
            )
        }),
        ('Scope', {
            'fields': (
                'is_nationwide',
                'location',
            )
        }),
        ('Recurring Settings', {
            'fields': (
                'is_recurring',
                'recurring_month',
                'recurring_day',
            ),
            'classes': ('collapse',),
            'description': 'Configure if this holiday repeats annually (e.g., Christmas on Dec 25)'
        }),
        ('Audit Trail', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
            ),
            'classes': ('collapse',),
        }),
    )

    def location_display(self, obj):
        """Display location or 'All Locations' for nationwide holidays."""
        if obj.is_nationwide:
            return 'All Locations'
        return obj.location.name if obj.location else '-'
    location_display.short_description = 'Location'
    location_display.admin_order_field = 'location__name'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'location',
            'created_by',
            'updated_by'
        )
