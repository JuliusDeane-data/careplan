"""
Notification models for the Careplan project.
Handles in-app notifications for users about important events.
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.core.models import BaseModel
from apps.core.constants import NotificationType


class Notification(BaseModel):
    """
    Notification model for in-app notifications.
    Supports linking to any model via GenericForeignKey.
    """

    recipient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='User who receives this notification'
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        db_index=True,
        help_text='Type of notification'
    )
    title = models.CharField(
        max_length=200,
        help_text='Notification title/summary'
    )
    message = models.TextField(
        help_text='Detailed notification message'
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether notification has been read'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When notification was read'
    )

    # Generic relation to link to any object (vacation request, shift, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Type of related object'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='ID of related object'
    )
    related_object = GenericForeignKey('content_type', 'object_id')

    # Optional action URL for frontend navigation
    action_url = models.CharField(
        max_length=500,
        blank=True,
        help_text='URL to navigate to when clicking notification'
    )

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_unread(self):
        """Mark notification as unread."""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])


class NotificationPreference(models.Model):
    """
    User preferences for notifications.
    Controls which notifications a user wants to receive and how.
    """

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        help_text='User these preferences belong to'
    )

    # General notification settings
    email_notifications_enabled = models.BooleanField(
        default=True,
        help_text='Receive email notifications'
    )
    push_notifications_enabled = models.BooleanField(
        default=True,
        help_text='Receive push notifications (future feature)'
    )

    # Specific notification type preferences
    vacation_request_submitted = models.BooleanField(
        default=True,
        help_text='Notify when vacation request is submitted (managers only)'
    )
    vacation_request_approved = models.BooleanField(
        default=True,
        help_text='Notify when vacation request is approved'
    )
    vacation_request_denied = models.BooleanField(
        default=True,
        help_text='Notify when vacation request is denied'
    )
    vacation_request_modified = models.BooleanField(
        default=True,
        help_text='Notify when vacation request is modified'
    )
    vacation_request_cancelled = models.BooleanField(
        default=True,
        help_text='Notify when vacation request is cancelled'
    )
    shift_assigned = models.BooleanField(
        default=True,
        help_text='Notify when shift is assigned'
    )
    shift_modified = models.BooleanField(
        default=True,
        help_text='Notify when shift is modified'
    )
    profile_updated = models.BooleanField(
        default=False,
        help_text='Notify when profile is updated'
    )
    system_message = models.BooleanField(
        default=True,
        help_text='Receive system messages'
    )

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(
        default=False,
        help_text='Enable quiet hours (no notifications)'
    )
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text='Start time for quiet hours (e.g., 22:00)'
    )
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text='End time for quiet hours (e.g., 07:00)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.username}"

    def should_notify(self, notification_type):
        """
        Check if user wants to receive a specific notification type.

        Args:
            notification_type: NotificationType constant

        Returns:
            bool: True if user wants this notification
        """
        # Map notification types to preference fields
        type_mapping = {
            NotificationType.VACATION_REQUEST_SUBMITTED: self.vacation_request_submitted,
            NotificationType.VACATION_REQUEST_APPROVED: self.vacation_request_approved,
            NotificationType.VACATION_REQUEST_DENIED: self.vacation_request_denied,
            NotificationType.VACATION_REQUEST_MODIFIED: self.vacation_request_modified,
            NotificationType.VACATION_REQUEST_CANCELLED: self.vacation_request_cancelled,
            NotificationType.SHIFT_ASSIGNED: self.shift_assigned,
            NotificationType.SHIFT_MODIFIED: self.shift_modified,
            NotificationType.PROFILE_UPDATED: self.profile_updated,
            NotificationType.SYSTEM_MESSAGE: self.system_message,
        }

        return type_mapping.get(notification_type, True)

    def is_in_quiet_hours(self):
        """
        Check if current time is within quiet hours.

        Returns:
            bool: True if in quiet hours
        """
        if not self.quiet_hours_enabled:
            return False

        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        from django.utils import timezone
        now = timezone.now().time()

        # Handle quiet hours that span midnight
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Normal case: 22:00 - 07:00 doesn't span midnight in comparison
            # Actually if start <= end, it means it doesn't span midnight
            # e.g., 09:00 - 17:00
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:
            # Spans midnight: e.g., 22:00 - 07:00
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
