"""
Signals for vacation app.
Handles notifications and vacation balance updates on status changes.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import VacationRequest, RequestType
from apps.core.utils.helpers import send_notification
from apps.core.constants import NotificationType, VacationStatus


@receiver(pre_save, sender=VacationRequest)
def vacation_request_pre_save(sender, instance, **kwargs):
    """Track status changes before save."""
    if instance.pk:
        # Get the old instance to compare status
        try:
            instance._old_status = VacationRequest.objects.get(pk=instance.pk).status
        except VacationRequest.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=VacationRequest)
def vacation_request_post_save(sender, instance, created, **kwargs):
    """
    Handle vacation request status changes.
    Send notifications and update vacation balance.
    """
    if created:
        # New request created - notify manager
        notify_manager_of_new_request(instance)
    else:
        # Check if status changed
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            if instance.status == VacationStatus.APPROVED:
                notify_employee_approved(instance)
                update_employee_balance(instance)
            elif instance.status == VacationStatus.DENIED:
                notify_employee_denied(instance)
            elif instance.status == VacationStatus.CANCELLED:
                notify_stakeholders_cancelled(instance)
                if old_status == VacationStatus.APPROVED:
                    restore_employee_balance(instance)


def notify_manager_of_new_request(vacation_request):
    """Notify manager when new vacation request is submitted."""
    employee = vacation_request.employee

    # Determine who to notify (supervisor first, then location manager)
    manager = employee.supervisor
    if not manager and employee.primary_location:
        manager = employee.primary_location.manager

    if manager:
        send_notification(
            user=manager,
            notification_type=NotificationType.VACATION_REQUEST_SUBMITTED,
            title=f'New Vacation Request from {employee.get_full_name()}',
            message=f'{employee.get_full_name()} ({employee.employee_id}) requested {vacation_request.get_request_type_display()} from {vacation_request.start_date} to {vacation_request.end_date} ({vacation_request.vacation_days} days).',
            action_url=f'/admin/vacation/vacationrequest/{vacation_request.id}/change/',
            related_object=vacation_request,
            created_by=employee
        )


def notify_employee_approved(vacation_request):
    """Notify employee when vacation is approved."""
    send_notification(
        user=vacation_request.employee,
        notification_type=NotificationType.VACATION_REQUEST_APPROVED,
        title='Vacation Request Approved',
        message=f'Your {vacation_request.get_request_type_display().lower()} from {vacation_request.start_date} to {vacation_request.end_date} ({vacation_request.vacation_days} days) has been approved by {vacation_request.approved_by.get_full_name() if vacation_request.approved_by else "manager"}.',
        action_url=f'/vacation/requests/{vacation_request.id}/',
        related_object=vacation_request,
        created_by=vacation_request.approved_by
    )


def notify_employee_denied(vacation_request):
    """Notify employee when vacation is denied."""
    reason_text = f" Reason: {vacation_request.denial_reason}" if vacation_request.denial_reason else ""
    send_notification(
        user=vacation_request.employee,
        notification_type=NotificationType.VACATION_REQUEST_DENIED,
        title='Vacation Request Denied',
        message=f'Your {vacation_request.get_request_type_display().lower()} from {vacation_request.start_date} to {vacation_request.end_date} has been denied by {vacation_request.denied_by.get_full_name() if vacation_request.denied_by else "manager"}.{reason_text}',
        action_url=f'/vacation/requests/{vacation_request.id}/',
        related_object=vacation_request,
        created_by=vacation_request.denied_by
    )


def notify_stakeholders_cancelled(vacation_request):
    """Notify employee and manager when vacation is cancelled."""
    cancelled_by_name = vacation_request.cancelled_by.get_full_name() if vacation_request.cancelled_by else "admin"
    reason_text = f" Reason: {vacation_request.cancellation_reason}" if vacation_request.cancellation_reason else ""

    # Notify employee (if they didn't cancel it themselves)
    if vacation_request.cancelled_by != vacation_request.employee:
        send_notification(
            user=vacation_request.employee,
            notification_type=NotificationType.VACATION_REQUEST_CANCELLED,
            title='Vacation Request Cancelled',
            message=f'Your {vacation_request.get_request_type_display().lower()} from {vacation_request.start_date} to {vacation_request.end_date} has been cancelled by {cancelled_by_name}.{reason_text}',
            action_url=f'/vacation/requests/{vacation_request.id}/',
            related_object=vacation_request,
            created_by=vacation_request.cancelled_by
        )

    # Notify manager (if they exist and didn't cancel it)
    employee = vacation_request.employee
    manager = employee.supervisor or (employee.primary_location.manager if employee.primary_location else None)

    if manager and vacation_request.cancelled_by != manager:
        send_notification(
            user=manager,
            notification_type=NotificationType.VACATION_REQUEST_CANCELLED,
            title=f'Vacation Request Cancelled - {employee.get_full_name()}',
            message=f'{employee.get_full_name()}\'s {vacation_request.get_request_type_display().lower()} from {vacation_request.start_date} to {vacation_request.end_date} has been cancelled by {cancelled_by_name}.{reason_text}',
            action_url=f'/admin/vacation/vacationrequest/{vacation_request.id}/change/',
            related_object=vacation_request,
            created_by=vacation_request.cancelled_by
        )


def update_employee_balance(vacation_request):
    """Decrease employee vacation balance on approval."""
    # Only decrease balance for annual leave
    if vacation_request.request_type == RequestType.ANNUAL_LEAVE:
        employee = vacation_request.employee
        employee.remaining_vacation_days -= vacation_request.vacation_days
        employee.save(update_fields=['remaining_vacation_days'])


def restore_employee_balance(vacation_request):
    """Restore employee vacation balance on cancellation of approved request."""
    # Only restore balance for annual leave
    if vacation_request.request_type == RequestType.ANNUAL_LEAVE:
        employee = vacation_request.employee
        employee.remaining_vacation_days += vacation_request.vacation_days
        employee.save(update_fields=['remaining_vacation_days'])
