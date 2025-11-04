# Vacation App - Comprehensive Implementation Plan

**Date Created**: 2025-11-04
**Phase**: 3 of 5
**Priority**: High - Core business functionality

---

## 📋 Table of Contents

1. [Business Requirements](#business-requirements)
2. [Data Models](#data-models)
3. [Business Logic & Validation](#business-logic--validation)
4. [Signals & Automation](#signals--automation)
5. [Admin Interface](#admin-interface)
6. [Implementation Steps](#implementation-steps)
7. [Edge Cases & Considerations](#edge-cases--considerations)
8. [Testing Strategy](#testing-strategy)

---

## 🎯 Business Requirements

### Core Functionality
The vacation management system must handle:

1. **Vacation Requests**
   - Employees can request vacation time
   - Different types: Annual leave, sick leave, unpaid leave, etc.
   - Auto-calculate vacation days (excluding weekends/holidays)
   - Track approval status workflow
   - Support modifications and cancellations

2. **Approval Workflow**
   - Pending → Approved/Denied
   - Managers can approve/deny requests
   - Employees can cancel pending/approved requests
   - Notification sent at each status change

3. **Vacation Balance Tracking**
   - Each employee has annual vacation days (default: 30)
   - Track remaining days (decreases on approval)
   - Restore days on cancellation
   - Reset annually (future feature)

4. **Public Holidays**
   - Track national and location-specific holidays
   - Employees cannot use vacation days on holidays
   - Holidays automatically excluded from vacation day count

### Business Rules (24/7 Shift-Based System)

**Critical Understanding**:
- Employees work shifts 24/7/365 including weekends and holidays
- Vacation days = Weekdays only (Mon-Fri)
- Weekends (Sat-Sun) don't count as vacation days
- Public holidays don't count as vacation days
- Example: Vacation Mon-Sun = 5 vacation days (not 7)

**Why?**
- Employees may work Saturdays/Sundays as regular shifts
- They cannot "take vacation" on days they're not normally scheduled
- Only weekdays count because that's when vacation substitutes the regular schedule

---

## 📊 Data Models

### 1. VacationRequest Model

**Purpose**: Track employee vacation requests with full approval workflow

**Base**: Inherits from `BaseModel` (timestamps, soft delete, audit trail)

```python
class VacationRequest(BaseModel):
    """Vacation request with approval workflow."""

    # Core fields
    employee = ForeignKey(User, related_name='vacation_requests')
    start_date = DateField()
    end_date = DateField()

    # Auto-calculated fields
    vacation_days = IntegerField(help_text='Workdays only, excludes weekends/holidays')
    total_days = IntegerField(help_text='Total calendar days')

    # Request details
    request_type = CharField(choices=RequestType.choices)
      # ANNUAL_LEAVE (default)
      # SICK_LEAVE (requires medical certificate after X days)
      # UNPAID_LEAVE
      # PARENTAL_LEAVE
      # BEREAVEMENT_LEAVE
      # OTHER

    reason = TextField(blank=True, help_text='Optional reason for request')
    notes = TextField(blank=True, help_text='Internal notes')

    # Approval workflow
    status = CharField(choices=VacationStatus.choices, default='PENDING')
      # PENDING - Awaiting approval
      # APPROVED - Approved by manager
      # DENIED - Denied by manager
      # CANCELLED - Cancelled by employee or admin

    # Approval tracking
    approved_by = ForeignKey(User, null=True, related_name='approved_vacations')
    approved_at = DateTimeField(null=True)
    denial_reason = TextField(blank=True)
    denied_by = ForeignKey(User, null=True, related_name='denied_vacations')
    denied_at = DateTimeField(null=True)

    # Cancellation tracking
    cancelled_by = ForeignKey(User, null=True, related_name='cancelled_vacations')
    cancelled_at = DateTimeField(null=True)
    cancellation_reason = TextField(blank=True)

    # File upload (for sick leave medical certificates, etc.)
    supporting_document = FileField(blank=True, upload_to='vacation_documents/')
```

**Indexes**:
- `employee + status` - Fast lookup of user's pending/approved requests
- `start_date` - Date range queries
- `status` - Status filtering
- `approved_by` - Manager's approval history

**Meta**:
```python
class Meta:
    db_table = 'vacation_requests'
    ordering = ['-start_date']
    unique_together = None  # Allow overlapping for different types
```

**Methods**:
```python
def clean(self):
    """Validate vacation request."""
    # Implemented in business logic section

def approve(self, approved_by):
    """Approve the vacation request."""

def deny(self, denied_by, reason):
    """Deny the vacation request."""

def cancel(self, cancelled_by, reason=''):
    """Cancel the vacation request."""

def is_modifiable(self):
    """Check if request can be modified."""
    return self.status == 'PENDING'

def is_cancellable(self):
    """Check if request can be cancelled."""
    return self.status in ['PENDING', 'APPROVED']

def days_until_start(self):
    """Calculate days until vacation starts."""
    from django.utils import timezone
    today = timezone.now().date()
    return (self.start_date - today).days
```

**Properties**:
```python
@property
def is_pending(self):
    return self.status == VacationStatus.PENDING

@property
def is_approved(self):
    return self.status == VacationStatus.APPROVED

@property
def is_in_past(self):
    from django.utils import timezone
    return self.end_date < timezone.now().date()

@property
def is_current(self):
    """Check if vacation is currently active."""
    from django.utils import timezone
    today = timezone.now().date()
    return self.start_date <= today <= self.end_date
```

---

### 2. PublicHoliday Model

**Purpose**: Track public holidays that don't count as vacation days

**Base**: Inherits from `BaseModel`

```python
class PublicHoliday(BaseModel):
    """Public holidays that exclude from vacation day calculations."""

    date = DateField(db_index=True, help_text='Holiday date')
    name = CharField(max_length=100, help_text='Holiday name')
    description = TextField(blank=True)

    # Location-specific or national
    location = ForeignKey(
        Location,
        null=True,
        blank=True,
        related_name='holidays',
        help_text='Specific location, or null for national holiday'
    )
    is_nationwide = BooleanField(
        default=True,
        help_text='True if applies to all locations'
    )

    # Recurring or one-time
    is_recurring = BooleanField(
        default=False,
        help_text='If true, holiday repeats annually'
    )
    recurring_month = IntegerField(
        null=True,
        blank=True,
        help_text='Month (1-12) for recurring holidays'
    )
    recurring_day = IntegerField(
        null=True,
        blank=True,
        help_text='Day of month for recurring holidays'
    )
```

**Indexes**:
- `date` - Fast date lookups
- `location + date` - Location-specific queries
- `is_nationwide` - National holiday filtering

**Meta**:
```python
class Meta:
    db_table = 'public_holidays'
    ordering = ['date']
    unique_together = [['date', 'location']]  # Prevent duplicates
```

**Methods**:
```python
@classmethod
def get_holidays_for_year(cls, year, location=None):
    """Get all holidays for a specific year and location."""
    from datetime import date
    start = date(year, 1, 1)
    end = date(year, 12, 31)

    query = cls.objects.filter(date__range=(start, end))
    if location:
        query = query.filter(
            models.Q(location=location) | models.Q(is_nationwide=True)
        )
    return query

@classmethod
def create_recurring_holidays(cls, year):
    """Auto-create recurring holidays for a given year."""
    # Generate holidays from recurring templates
```

---

## ⚙️ Business Logic & Validation

### Validation Rules

Implement in `VacationRequest.clean()` method:

#### 1. Date Validation
```python
def clean(self):
    from django.core.exceptions import ValidationError
    from django.utils import timezone
    from apps.core.utils.date_utils import get_vacation_days_count
    from apps.core.constants import MIN_ADVANCE_NOTICE_DAYS

    errors = {}

    # Rule 1: End date must be >= start date
    if self.end_date < self.start_date:
        errors['end_date'] = 'End date must be after start date'

    # Rule 2: Cannot request vacation in the past
    today = timezone.now().date()
    if self.start_date < today:
        errors['start_date'] = 'Cannot request vacation in the past'

    # Rule 3: Minimum advance notice (14 days)
    days_until = (self.start_date - today).days
    if days_until < MIN_ADVANCE_NOTICE_DAYS:
        errors['start_date'] = f'Vacation must be requested at least {MIN_ADVANCE_NOTICE_DAYS} days in advance'

    if errors:
        raise ValidationError(errors)
```

#### 2. Overlap Detection
```python
    # Rule 4: No overlapping vacation requests (only for same type)
    overlapping = VacationRequest.objects.filter(
        employee=self.employee,
        status__in=['PENDING', 'APPROVED']
    ).filter(
        models.Q(start_date__lte=self.end_date, end_date__gte=self.start_date)
    ).exclude(pk=self.pk)

    if overlapping.exists():
        raise ValidationError({
            'start_date': f'Overlaps with existing request: {overlapping.first()}'
        })
```

#### 3. Balance Validation
```python
    # Rule 5: Sufficient vacation days (for ANNUAL_LEAVE only)
    if self.request_type == 'ANNUAL_LEAVE':
        vacation_days = get_vacation_days_count(
            self.start_date,
            self.end_date,
            location=self.employee.primary_location
        )

        # Check remaining balance
        if vacation_days > self.employee.remaining_vacation_days:
            raise ValidationError({
                'end_date': f'Insufficient vacation days. Requested: {vacation_days}, Available: {self.employee.remaining_vacation_days}'
            })
```

#### 4. Location Coverage Check (Optional - Advanced)
```python
    # Rule 6: Ensure minimum staff coverage at location
    # Count approved vacations for same dates at same location
    same_location_vacations = VacationRequest.objects.filter(
        employee__primary_location=self.employee.primary_location,
        status='APPROVED',
        start_date__lte=self.end_date,
        end_date__gte=self.start_date
    ).exclude(pk=self.pk).count()

    # Calculate if this would breach minimum coverage
    # This is a soft warning, not a hard block
    # (Can be implemented later if needed)
```

### Auto-Calculation on Save

```python
def save(self, *args, **kwargs):
    from apps.core.utils.date_utils import get_vacation_days_count, get_total_days_count

    # Auto-calculate vacation days (weekdays only)
    if self.start_date and self.end_date:
        self.vacation_days = get_vacation_days_count(
            self.start_date,
            self.end_date,
            location=self.employee.primary_location
        )
        self.total_days = get_total_days_count(
            self.start_date,
            self.end_date
        )

    super().save(*args, **kwargs)
```

---

## 🔔 Signals & Automation

### Signal: Post-Save VacationRequest

**File**: `apps/vacation/signals.py`

```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import VacationRequest
from apps.core.utils.helpers import send_notification
from apps.core.constants import NotificationType

@receiver(post_save, sender=VacationRequest)
def vacation_request_post_save(sender, instance, created, **kwargs):
    """Handle vacation request status changes."""

    if created:
        # New request created - notify manager
        notify_manager_of_new_request(instance)
    else:
        # Check if status changed
        if instance.status == 'APPROVED':
            notify_employee_approved(instance)
            update_employee_balance(instance)
        elif instance.status == 'DENIED':
            notify_employee_denied(instance)
        elif instance.status == 'CANCELLED':
            notify_employee_cancelled(instance)
            restore_employee_balance(instance)

def notify_manager_of_new_request(vacation_request):
    """Notify manager when new vacation request is submitted."""
    employee = vacation_request.employee
    manager = employee.supervisor or employee.primary_location.manager

    if manager:
        send_notification(
            user=manager,
            notification_type=NotificationType.VACATION_REQUEST_SUBMITTED,
            title=f'New Vacation Request from {employee.get_full_name()}',
            message=f'{employee.get_full_name()} requested vacation from {vacation_request.start_date} to {vacation_request.end_date} ({vacation_request.vacation_days} days).',
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
        message=f'Your vacation request from {vacation_request.start_date} to {vacation_request.end_date} has been approved.',
        action_url=f'/vacation/requests/{vacation_request.id}/',
        related_object=vacation_request,
        created_by=vacation_request.approved_by
    )

def notify_employee_denied(vacation_request):
    """Notify employee when vacation is denied."""
    send_notification(
        user=vacation_request.employee,
        notification_type=NotificationType.VACATION_REQUEST_DENIED,
        title='Vacation Request Denied',
        message=f'Your vacation request from {vacation_request.start_date} to {vacation_request.end_date} has been denied. Reason: {vacation_request.denial_reason}',
        action_url=f'/vacation/requests/{vacation_request.id}/',
        related_object=vacation_request,
        created_by=vacation_request.denied_by
    )

def update_employee_balance(vacation_request):
    """Decrease employee vacation balance on approval."""
    if vacation_request.request_type == 'ANNUAL_LEAVE':
        employee = vacation_request.employee
        employee.remaining_vacation_days -= vacation_request.vacation_days
        employee.save(update_fields=['remaining_vacation_days'])

def restore_employee_balance(vacation_request):
    """Restore employee vacation balance on cancellation."""
    if vacation_request.request_type == 'ANNUAL_LEAVE' and vacation_request.status == 'CANCELLED':
        # Only restore if it was previously approved
        employee = vacation_request.employee
        employee.remaining_vacation_days += vacation_request.vacation_days
        employee.save(update_fields=['remaining_vacation_days'])
```

### Register Signals

**File**: `apps/vacation/apps.py`

```python
from django.apps import AppConfig

class VacationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vacation'

    def ready(self):
        import apps.vacation.signals  # noqa
```

---

## 🎨 Admin Interface

### VacationRequest Admin

```python
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
        'denied_at',
        'cancelled_at',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]

    autocomplete_fields = [
        'employee',
        'approved_by',
        'denied_by',
        'cancelled_by',
    ]

    date_hierarchy = 'start_date'

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
        return f"{obj.employee.employee_id} - {obj.employee.get_full_name()}"

    def status_display(self, obj):
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'green',
            'DENIED': 'red',
            'CANCELLED': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    def approve_requests(self, request, queryset):
        """Bulk approve vacation requests."""
        count = 0
        for vacation_request in queryset.filter(status='PENDING'):
            vacation_request.approve(approved_by=request.user)
            count += 1
        self.message_user(request, f'{count} request(s) approved.')

    def deny_requests(self, request, queryset):
        """Bulk deny vacation requests."""
        # This would need a form to collect denial reason
        pass
```

### PublicHoliday Admin

```python
@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    """Admin interface for public holidays."""

    list_display = [
        'date',
        'name',
        'location',
        'is_nationwide',
        'is_recurring',
    ]

    list_filter = [
        'is_nationwide',
        'is_recurring',
        'location',
        'date',
    ]

    search_fields = ['name', 'description']

    date_hierarchy = 'date'

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
        ('Recurring', {
            'fields': (
                'is_recurring',
                'recurring_month',
                'recurring_day',
            ),
            'classes': ('collapse',),
        }),
    )
```

---

## 📝 Implementation Steps

### Step 1: Create Models
1. Create `VacationRequest` model in `apps/vacation/models.py`
2. Create `PublicHoliday` model
3. Add request type choices
4. Add validation methods
5. Add approval/deny/cancel methods

### Step 2: Create Migrations
1. `python manage.py makemigrations vacation`
2. Review migration file
3. `python manage.py migrate vacation`

### Step 3: Create Signals
1. Create `apps/vacation/signals.py`
2. Implement notification signals
3. Implement balance update signals
4. Register signals in `apps.py`

### Step 4: Create Admin
1. Create `VacationRequestAdmin` in `apps/vacation/admin.py`
2. Create `PublicHolidayAdmin`
3. Add custom actions
4. Add colored status display

### Step 5: Test
1. Create public holidays via admin
2. Create vacation requests
3. Test approval workflow
4. Verify notifications sent
5. Verify balance updates
6. Test validation rules

---

## 🔍 Edge Cases & Considerations

### Edge Case 1: Year Boundary
**Problem**: Vacation spans Dec 31 - Jan 2
**Solution**: Calculate days correctly across year boundary
**Status**: Already handled by date_utils

### Edge Case 2: Holiday in Middle of Vacation
**Problem**: Vacation Mon-Fri, but Wednesday is a holiday
**Solution**: Auto-exclude holiday from count (4 vacation days, not 5)
**Status**: Already handled by `get_vacation_days_count()`

### Edge Case 3: Cancelling Approved Vacation
**Problem**: Employee cancels 1 day before vacation starts
**Solution**:
- Allow cancellation up to 1 day before
- Restore vacation balance
- Send notification to manager
**Implementation**: Add `min_cancellation_notice` validation

### Edge Case 4: Employee Termination
**Problem**: Employee terminated with pending vacation
**Solution**: Auto-deny or auto-cancel pending requests
**Implementation**: Signal on User.employment_status change

### Edge Case 5: Sick Leave Without Medical Certificate
**Problem**: Sick leave > 3 days requires certificate
**Solution**:
- Add validation in clean() for SICK_LEAVE
- Require `supporting_document` if > 3 days
**Implementation**: Custom validation

### Edge Case 6: Balance Goes Negative
**Problem**: Admin manually edits remaining_vacation_days
**Solution**: Add warning in admin, don't hard-block
**Implementation**: Custom save validation

### Edge Case 7: Overlapping Different Types
**Problem**: Can employee have sick leave and annual leave same day?
**Solution**: Generally no, but sick leave can override annual leave
**Implementation**: Special handling in validation

---

## 🧪 Testing Strategy

### Unit Tests
```python
# Test vacation day calculation
def test_vacation_days_exclude_weekends():
    # Mon-Sun = 5 days

def test_vacation_days_exclude_holidays():
    # Create holiday, verify excluded

# Test validation
def test_cannot_overlap_requests():

def test_minimum_advance_notice():

def test_insufficient_balance():

# Test workflow
def test_approve_request():

def test_deny_request():

def test_cancel_request():

# Test balance updates
def test_balance_decreases_on_approval():

def test_balance_restores_on_cancellation():
```

### Integration Tests
```python
# Test signals
def test_notification_sent_on_approval():

def test_manager_notified_on_new_request():

# Test admin actions
def test_bulk_approve():
```

---

## 📊 Success Metrics

### Phase Complete When:
- ✅ Models created and migrated
- ✅ Admin interface functional
- ✅ Validation rules working
- ✅ Signals sending notifications
- ✅ Balance updates correctly
- ✅ Public holidays exclude from count
- ✅ All Django checks pass
- ✅ Can create, approve, deny, cancel requests via admin

---

## 🚀 Future Enhancements

### Phase 4+ Features:
1. **Annual Balance Reset** - Celery task to reset on Jan 1
2. **Carryover Days** - Allow carrying unused days to next year (max 5)
3. **Vacation Calendar View** - Visual calendar in admin
4. **Team Vacation View** - See who's on vacation when
5. **Email Notifications** - Send emails in addition to in-app
6. **Mobile Approval** - Approve from mobile device
7. **Automatic Substitutes** - Suggest replacement employees
8. **Blackout Dates** - Prevent vacation during busy periods
9. **Half-Day Requests** - Support partial day vacation
10. **Vacation Planning Assistant** - Suggest optimal dates

---

## 📚 References

- Date utilities: `apps/core/utils/date_utils.py`
- Constants: `apps/core/constants.py`
- Notifications: `apps/notifications/models.py`
- User model: `apps/accounts/models.py`

---

**Status**: Ready for Implementation
**Estimated Time**: 3-4 hours
**Dependencies**: Core app ✅, Notifications app ✅, Accounts app ✅
