"""
Django admin configuration for notifications app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""

    list_display = [
        'id',
        'recipient_display',
        'notification_type',
        'title_display',
        'is_read_display',
        'created_at',
        'read_at',
    ]
    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
    ]
    search_fields = [
        'recipient__username',
        'recipient__email',
        'recipient__employee_id',
        'title',
        'message',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'read_at',
        'related_object',
    ]
    autocomplete_fields = ['recipient']
    date_hierarchy = 'created_at'
    list_per_page = 50

    fieldsets = (
        ('Notification Details', {
            'fields': (
                'recipient',
                'notification_type',
                'title',
                'message',
            )
        }),
        ('Status', {
            'fields': (
                'is_read',
                'read_at',
            )
        }),
        ('Related Object', {
            'fields': (
                'content_type',
                'object_id',
                'related_object',
                'action_url',
            ),
            'classes': ('collapse',),
        }),
        ('Audit Information', {
            'fields': (
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
            ),
            'classes': ('collapse',),
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected']

    def recipient_display(self, obj):
        """Display recipient with employee ID."""
        return f"{obj.recipient.employee_id} - {obj.recipient.get_full_name()}"
    recipient_display.short_description = 'Recipient'
    recipient_display.admin_order_field = 'recipient__employee_id'

    def title_display(self, obj):
        """Display title with truncation."""
        if len(obj.title) > 50:
            return obj.title[:50] + '...'
        return obj.title
    title_display.short_description = 'Title'
    title_display.admin_order_field = 'title'

    def is_read_display(self, obj):
        """Display read status with colored indicator."""
        if obj.is_read:
            return format_html('<span style="color: green;">[Read]</span>')
        return format_html('<span style="color: orange;">[Unread]</span>')
    is_read_display.short_description = 'Status'
    is_read_display.admin_order_field = 'is_read'

    def mark_as_read(self, request, queryset):
        """Bulk action to mark notifications as read."""
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Bulk action to mark notifications as unread."""
        count = 0
        for notification in queryset:
            if notification.is_read:
                notification.mark_as_unread()
                count += 1
        self.message_user(request, f'{count} notification(s) marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'recipient',
            'content_type',
            'created_by',
            'updated_by'
        )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model."""

    list_display = [
        'user_display',
        'email_notifications_enabled',
        'push_notifications_enabled',
        'quiet_hours_display',
        'updated_at',
    ]
    list_filter = [
        'email_notifications_enabled',
        'push_notifications_enabled',
        'quiet_hours_enabled',
    ]
    search_fields = [
        'user__username',
        'user__email',
        'user__employee_id',
    ]
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('General Settings', {
            'fields': (
                'email_notifications_enabled',
                'push_notifications_enabled',
            )
        }),
        ('Notification Types', {
            'fields': (
                'vacation_request_submitted',
                'vacation_request_approved',
                'vacation_request_denied',
                'vacation_request_modified',
                'vacation_request_cancelled',
                'shift_assigned',
                'shift_modified',
                'profile_updated',
                'system_message',
            )
        }),
        ('Quiet Hours', {
            'fields': (
                'quiet_hours_enabled',
                'quiet_hours_start',
                'quiet_hours_end',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    def user_display(self, obj):
        """Display user with employee ID."""
        return f"{obj.user.employee_id} - {obj.user.get_full_name()}"
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user__employee_id'

    def quiet_hours_display(self, obj):
        """Display quiet hours status."""
        if obj.quiet_hours_enabled and obj.quiet_hours_start and obj.quiet_hours_end:
            return f"{obj.quiet_hours_start.strftime('%H:%M')} - {obj.quiet_hours_end.strftime('%H:%M')}"
        return "Disabled"
    quiet_hours_display.short_description = 'Quiet Hours'
