# Employees App Implementation Plan

## Overview
The Employees app manages employee profiles, HR data, qualifications, and employment information. It serves as the central repository for all employee-related data and integrates closely with the User model from the accounts app.

---

## 1. Models

### 1.1 Employee Model

**Purpose**: Store comprehensive employee information and link to User account

**Base**: Inherits from `BaseModel` (includes timestamps, soft delete, audit trail)

**Relationships**:
- `user` - OneToOneField to User (CASCADE)
- `primary_location` - ForeignKey to Location (PROTECT)
- `additional_locations` - ManyToManyField to Location (can work at multiple locations)
- `supervisor` - ForeignKey to User (SET_NULL, nullable)
- `qualifications` - ManyToManyField to Qualification

**Personal Information Fields**:
- `employee_id` (CharField, unique, indexed) - Unique employee identifier (e.g., "EMP001")
- `date_of_birth` (DateField)
- `gender` (CharField, choices: MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY)
- `nationality` (CharField, optional)

**Contact Information Fields**:
- `phone` (CharField, validated with validate_phone_number)
- `emergency_contact_name` (CharField)
- `emergency_contact_phone` (CharField, validated)
- `address` (CharField)
- `city` (CharField)
- `postal_code` (CharField, validated with validate_postal_code)
- `country` (CharField, default='Germany')

**Employment Information Fields**:
- `hire_date` (DateField)
- `employment_status` (CharField, choices from EmploymentStatus: ACTIVE, ON_LEAVE, TERMINATED)
- `employment_type` (CharField, choices: FULL_TIME, PART_TIME, CONTRACT, TEMPORARY)
- `job_title` (CharField) - e.g., "Care Worker", "Nurse", "Care Manager"
- `department` (CharField, optional) - e.g., "Elderly Care", "Intensive Care"
- `contract_hours_per_week` (DecimalField) - Contracted weekly hours
- `termination_date` (DateField, null=True, blank=True)
- `termination_reason` (TextField, null=True, blank=True)

**Vacation Information Fields**:
- `annual_vacation_days` (IntegerField, default=30) - Total vacation days per year
- `remaining_vacation_days` (IntegerField, default=30) - Cached field, updated by signals

**Salary Information** (Sensitive):
- `hourly_rate` (DecimalField, null=True, blank=True) - For hourly employees
- `monthly_salary` (DecimalField, null=True, blank=True) - For salaried employees
- `currency` (CharField, default='EUR')

**Additional Fields**:
- `notes` (TextField, blank=True) - Internal HR notes
- `profile_picture` (ImageField, optional) - Employee photo

**Meta**:
```python
class Meta:
    db_table = 'employees'
    verbose_name = 'Employee'
    verbose_name_plural = 'Employees'
    ordering = ['employee_id']
    indexes = [
        models.Index(fields=['employee_id']),
        models.Index(fields=['employment_status']),
        models.Index(fields=['primary_location']),
    ]
```

**Methods**:
- `get_full_name()` - Return user's full name
- `get_age()` - Calculate current age from date_of_birth
- `get_years_of_service()` - Calculate years since hire_date
- `is_active()` - Check if employment_status is ACTIVE
- `can_work_at_location(location)` - Check if employee can work at location
- `update_vacation_balance()` - Recalculate remaining vacation days

**Properties**:
- `full_name` - Property for easy access to name
- `age` - Property for age
- `years_of_service` - Property for service duration

**Implementation**:
```python
from django.db import models
from django.utils import timezone
from apps.core.models import BaseModel
from apps.core.utils.validators import validate_phone_number, validate_postal_code
from apps.core.constants import EmploymentStatus
from datetime import date

class EmploymentType(models.TextChoices):
    FULL_TIME = 'FULL_TIME', 'Full Time'
    PART_TIME = 'PART_TIME', 'Part Time'
    CONTRACT = 'CONTRACT', 'Contract'
    TEMPORARY = 'TEMPORARY', 'Temporary'

class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'
    PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', 'Prefer not to say'

class Employee(BaseModel):
    # Relationship with User
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )

    # Unique identifier
    employee_id = models.CharField(
        max_length=10,
        unique=True,
        db_index=True
    )

    # Personal information
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_SAY
    )
    nationality = models.CharField(max_length=50, blank=True)

    # Contact information
    phone = models.CharField(
        max_length=20,
        validators=[validate_phone_number]
    )
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(
        max_length=20,
        validators=[validate_phone_number]
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=10,
        validators=[validate_postal_code]
    )
    country = models.CharField(max_length=50, default='Germany')

    # Employment information
    hire_date = models.DateField()
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        db_index=True
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    contract_hours_per_week = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=40.00
    )
    termination_date = models.DateField(null=True, blank=True)
    termination_reason = models.TextField(blank=True)

    # Location relationships
    primary_location = models.ForeignKey(
        'locations.Location',
        on_delete=models.PROTECT,
        related_name='primary_employees'
    )
    additional_locations = models.ManyToManyField(
        'locations.Location',
        related_name='additional_employees',
        blank=True
    )

    # Supervisor relationship
    supervisor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_employees'
    )

    # Qualifications
    qualifications = models.ManyToManyField(
        'Qualification',
        related_name='employees',
        blank=True
    )

    # Vacation information
    annual_vacation_days = models.IntegerField(default=30)
    remaining_vacation_days = models.IntegerField(default=30)

    # Salary information (sensitive)
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='EUR')

    # Additional
    notes = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='employee_photos/',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']

    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"

    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.get_full_name()

    def get_age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) <
            (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def age(self):
        return self.get_age()

    def get_years_of_service(self):
        today = date.today()
        return today.year - self.hire_date.year - (
            (today.month, today.day) <
            (self.hire_date.month, self.hire_date.day)
        )

    @property
    def years_of_service(self):
        return self.get_years_of_service()

    def is_active(self):
        return self.employment_status == EmploymentStatus.ACTIVE

    def can_work_at_location(self, location):
        return (
            self.primary_location == location or
            location in self.additional_locations.all()
        )

    def update_vacation_balance(self):
        """
        Recalculate remaining vacation days based on approved requests.
        This should be called via signal when vacation requests change.
        """
        from apps.vacation.models import VacationRequest
        from apps.core.constants import VacationStatus

        # Get current year's approved vacation days
        year = timezone.now().year
        used_days = VacationRequest.objects.filter(
            employee=self,
            status=VacationStatus.APPROVED,
            start_date__year=year
        ).aggregate(
            total=models.Sum('total_days')
        )['total'] or 0

        self.remaining_vacation_days = self.annual_vacation_days - used_days
        self.save(update_fields=['remaining_vacation_days'])
```

---

### 1.2 Qualification Model

**Purpose**: Store qualifications/certifications that employees can have

**Base**: Inherits from `BaseModel`

**Fields**:
- `code` (CharField, unique) - Short code (e.g., "RN", "CNA", "LPN")
- `name` (CharField) - Full name (e.g., "Registered Nurse")
- `description` (TextField) - Detailed description
- `required_for_roles` (TextField, optional) - Which roles require this
- `is_active` (BooleanField, default=True) - Can be disabled

**Meta**:
```python
class Meta:
    db_table = 'qualifications'
    verbose_name = 'Qualification'
    verbose_name_plural = 'Qualifications'
    ordering = ['name']
```

**Implementation**:
```python
class Qualification(BaseModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    required_for_roles = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'qualifications'
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"
```

---

### 1.3 EmployeeDocument Model

**Purpose**: Store employee documents (contracts, certificates, etc.)

**Base**: Inherits from `BaseModel`

**Fields**:
- `employee` (ForeignKey to Employee, CASCADE)
- `document_type` (CharField, choices: CONTRACT, CERTIFICATE, ID_DOCUMENT, OTHER)
- `title` (CharField) - Document title
- `file` (FileField) - Uploaded document
- `expiry_date` (DateField, nullable) - For certificates that expire
- `notes` (TextField, optional)

**Meta**:
```python
class Meta:
    db_table = 'employee_documents'
    ordering = ['-created_at']
```

**Implementation**:
```python
class DocumentType(models.TextChoices):
    CONTRACT = 'CONTRACT', 'Employment Contract'
    CERTIFICATE = 'CERTIFICATE', 'Certificate/Qualification'
    ID_DOCUMENT = 'ID_DOCUMENT', 'Identification Document'
    TRAINING = 'TRAINING', 'Training Certificate'
    OTHER = 'OTHER', 'Other'

class EmployeeDocument(BaseModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='employee_documents/')
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'employee_documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"

    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False
```

---

## 2. Signals

**Purpose**: Automatic actions when employee data changes

### 2.1 Create User Signal
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User

@receiver(post_save, sender=Employee)
def sync_employee_to_user(sender, instance, created, **kwargs):
    """
    Sync employee information to user model.
    Update user's first_name and last_name from employee data.
    """
    if instance.user:
        user = instance.user
        # Could sync additional fields if needed
        if not user.first_name or not user.last_name:
            # Trigger profile update
            pass
```

### 2.2 Vacation Balance Signal
```python
from apps.vacation.models import VacationRequest

@receiver(post_save, sender=VacationRequest)
def update_vacation_balance_on_request_change(sender, instance, **kwargs):
    """
    Update employee's remaining vacation days when request status changes.
    """
    if instance.employee:
        instance.employee.update_vacation_balance()
```

---

## 3. Managers

### 3.1 EmployeeManager

**Purpose**: Custom manager with common query methods

```python
from apps.core.managers import OptimizedManager

class EmployeeManager(OptimizedManager):
    def active(self):
        """Get only active employees."""
        return self.get_queryset().filter(
            employment_status=EmploymentStatus.ACTIVE
        )

    def at_location(self, location):
        """Get employees who can work at a location."""
        return self.get_queryset().filter(
            models.Q(primary_location=location) |
            models.Q(additional_locations=location)
        ).distinct()

    def with_qualifications(self, qualification_codes):
        """Get employees with specific qualifications."""
        return self.get_queryset().filter(
            qualifications__code__in=qualification_codes
        ).distinct()

    def supervised_by(self, supervisor):
        """Get employees supervised by a specific user."""
        return self.get_queryset().filter(supervisor=supervisor)
```

---

## 4. Admin Interface

**Purpose**: Django admin for employee management

```python
from django.contrib import admin
from .models import Employee, Qualification, EmployeeDocument

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_full_name', 'job_title',
        'employment_status', 'primary_location', 'hire_date'
    ]
    list_filter = [
        'employment_status', 'employment_type',
        'primary_location', 'job_title'
    ]
    search_fields = [
        'employee_id', 'user__first_name', 'user__last_name',
        'user__email', 'job_title'
    ]
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    fieldsets = (
        ('User Account', {
            'fields': ('user', 'employee_id')
        }),
        ('Personal Information', {
            'fields': (
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
        ('Employment', {
            'fields': (
                'hire_date', 'employment_status', 'employment_type',
                'job_title', 'department', 'contract_hours_per_week',
                'termination_date', 'termination_reason'
            )
        }),
        ('Location & Supervisor', {
            'fields': (
                'primary_location', 'additional_locations',
                'supervisor', 'qualifications'
            )
        }),
        ('Vacation', {
            'fields': ('annual_vacation_days', 'remaining_vacation_days')
        }),
        ('Salary', {
            'fields': ('hourly_rate', 'monthly_salary', 'currency'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'document_type', 'title',
        'expiry_date', 'created_at'
    ]
    list_filter = ['document_type', 'expiry_date']
    search_fields = ['employee__employee_id', 'title']
```

---

## 5. Serializers (DRF)

### 5.1 QualificationSerializer
```python
from rest_framework import serializers
from .models import Qualification

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ['id', 'code', 'name', 'description', 'is_active']
        read_only_fields = ['id']
```

### 5.2 EmployeeListSerializer
```python
class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing employees."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    location_name = serializers.CharField(
        source='primary_location.name',
        read_only=True
    )

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'age',
            'job_title', 'employment_status', 'employment_type',
            'location_name', 'phone', 'hire_date'
        ]
        read_only_fields = ['id', 'employee_id']
```

### 5.3 EmployeeDetailSerializer
```python
class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for employee profile."""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    years_of_service = serializers.IntegerField(read_only=True)
    primary_location = serializers.StringRelatedField()
    additional_locations = serializers.StringRelatedField(many=True)
    supervisor = serializers.StringRelatedField()
    qualifications = QualificationSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'age', 'years_of_service',
            'user_email', 'user_role',
            'date_of_birth', 'gender', 'nationality',
            'phone', 'address', 'city', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone',
            'hire_date', 'employment_status', 'employment_type',
            'job_title', 'department', 'contract_hours_per_week',
            'primary_location', 'additional_locations',
            'supervisor', 'qualifications',
            'annual_vacation_days', 'remaining_vacation_days',
            'profile_picture', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'employee_id', 'remaining_vacation_days',
            'created_at', 'updated_at'
        ]
```

### 5.4 EmployeeCreateUpdateSerializer
```python
class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating employees."""

    class Meta:
        model = Employee
        fields = [
            'user', 'employee_id',
            'date_of_birth', 'gender', 'nationality',
            'phone', 'address', 'city', 'postal_code', 'country',
            'emergency_contact_name', 'emergency_contact_phone',
            'hire_date', 'employment_status', 'employment_type',
            'job_title', 'department', 'contract_hours_per_week',
            'primary_location', 'additional_locations',
            'supervisor', 'qualifications',
            'annual_vacation_days', 'hourly_rate', 'monthly_salary',
            'notes'
        ]

    def validate_employee_id(self, value):
        """Ensure employee_id is unique."""
        if self.instance:
            # Update - allow same ID
            if Employee.objects.exclude(pk=self.instance.pk).filter(
                employee_id=value
            ).exists():
                raise serializers.ValidationError(
                    "Employee with this ID already exists."
                )
        else:
            # Create - check uniqueness
            if Employee.objects.filter(employee_id=value).exists():
                raise serializers.ValidationError(
                    "Employee with this ID already exists."
                )
        return value

    def validate(self, data):
        """Cross-field validation."""
        # Ensure hire_date is not in future
        if data.get('hire_date') and data['hire_date'] > date.today():
            raise serializers.ValidationError({
                'hire_date': 'Hire date cannot be in the future.'
            })

        # If terminated, ensure termination_date is set
        if data.get('employment_status') == EmploymentStatus.TERMINATED:
            if not data.get('termination_date'):
                raise serializers.ValidationError({
                    'termination_date': 'Termination date required for terminated employees.'
                })

        return data
```

### 5.5 EmployeeDocumentSerializer
```python
class EmployeeDocumentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source='employee.get_full_name',
        read_only=True
    )
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'employee', 'employee_name',
            'document_type', 'title', 'file',
            'expiry_date', 'is_expired', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

---

## 6. Views (DRF ViewSets)

### 6.1 EmployeeViewSet
```python
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.mixins import UserAuditMixin

class EmployeeViewSet(UserAuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for Employee CRUD operations.

    List: GET /api/v1/employees/
    Create: POST /api/v1/employees/
    Retrieve: GET /api/v1/employees/{id}/
    Update: PUT/PATCH /api/v1/employees/{id}/
    Delete: DELETE /api/v1/employees/{id}/
    """
    queryset = Employee.objects.select_related(
        'user', 'primary_location', 'supervisor'
    ).prefetch_related('additional_locations', 'qualifications')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employment_status', 'employment_type', 'primary_location', 'job_title']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'job_title']
    ordering_fields = ['employee_id', 'hire_date', 'created_at']
    ordering = ['employee_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeCreateUpdateSerializer
        return EmployeeDetailSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's employee profile."""
        try:
            employee = request.user.employee_profile
            serializer = self.get_serializer(employee)
            return Response(serializer.data)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def vacation_balance(self, request, pk=None):
        """Get employee's vacation balance."""
        employee = self.get_object()
        return Response({
            'employee_id': employee.employee_id,
            'annual_vacation_days': employee.annual_vacation_days,
            'remaining_vacation_days': employee.remaining_vacation_days,
            'used_vacation_days': employee.annual_vacation_days - employee.remaining_vacation_days
        })

    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate an employee."""
        employee = self.get_object()
        termination_date = request.data.get('termination_date')
        termination_reason = request.data.get('termination_reason', '')

        if not termination_date:
            return Response(
                {'error': 'termination_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee.employment_status = EmploymentStatus.TERMINATED
        employee.termination_date = termination_date
        employee.termination_reason = termination_reason
        employee.updated_by = request.user
        employee.save()

        serializer = self.get_serializer(employee)
        return Response(serializer.data)
```

### 6.2 QualificationViewSet
```python
class QualificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Qualification CRUD operations.
    """
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']
    ordering = ['name']
```

### 6.3 EmployeeDocumentViewSet
```python
class EmployeeDocumentViewSet(UserAuditMixin, viewsets.ModelViewSet):
    """
    ViewSet for Employee Document management.
    """
    queryset = EmployeeDocument.objects.select_related('employee')
    serializer_class = EmployeeDocumentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'document_type']

    def get_queryset(self):
        """Filter documents based on user permissions."""
        user = self.request.user
        if user.is_admin_role() or user.is_planner():
            return self.queryset
        # Employees can only see their own documents
        return self.queryset.filter(employee__user=user)
```

---

## 7. URLs

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, QualificationViewSet, EmployeeDocumentViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'qualifications', QualificationViewSet, basename='qualification')
router.register(r'documents', EmployeeDocumentViewSet, basename='employee-document')

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## 8. Permissions

### 8.1 Custom Permissions
```python
from rest_framework import permissions

class IsAdminOrPlanner(permissions.BasePermission):
    """Allow access to admin and planner roles only."""

    def has_permission(self, request, view):
        return request.user.is_admin_role() or request.user.is_planner()

class IsOwnerOrAdminOrPlanner(permissions.BasePermission):
    """Allow access to owner, admin, or planner."""

    def has_object_permission(self, request, view, obj):
        # Admins and planners have full access
        if request.user.is_admin_role() or request.user.is_planner():
            return True

        # Employees can view/update their own profile (limited fields)
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False
```

---

## 9. Testing Strategy

### 9.1 Model Tests
- Test employee creation with all fields
- Test age calculation
- Test years of service calculation
- Test can_work_at_location method
- Test vacation balance updates
- Test soft delete functionality

### 9.2 API Tests
- Test employee list endpoint
- Test employee detail endpoint
- Test employee creation (admin only)
- Test employee update (admin/planner)
- Test self-service profile update (limited fields)
- Test terminate endpoint
- Test vacation balance endpoint
- Test search and filtering

### 9.3 Validation Tests
- Test unique employee_id constraint
- Test phone number validation
- Test postal code validation
- Test hire date validation (not in future)
- Test termination date required when terminated

---

## 10. File Structure

```
apps/employees/
├── __init__.py
├── apps.py
├── admin.py              # Django admin configuration
├── models.py             # Employee, Qualification, EmployeeDocument
├── serializers.py        # DRF serializers
├── views.py              # DRF viewsets
├── urls.py               # URL routing
├── permissions.py        # Custom permissions
├── signals.py            # Django signals
├── managers.py           # Custom managers
├── migrations/
│   └── __init__.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_serializers.py
    └── test_views.py
```

---

## 11. Implementation Order

1. ✅ Create models (Employee, Qualification, EmployeeDocument)
2. ✅ Create custom manager (EmployeeManager)
3. ✅ Create migrations
4. ✅ Run migrations
5. ✅ Configure Django admin
6. ✅ Create serializers
7. ✅ Create permissions
8. ✅ Create viewsets
9. ✅ Configure URLs
10. ✅ Create signals
11. ✅ Write tests
12. ✅ Test API endpoints

---

## 12. API Endpoints

### Employee Endpoints
- `GET /api/v1/employees/` - List all employees (paginated, filterable)
- `POST /api/v1/employees/` - Create employee (admin/planner)
- `GET /api/v1/employees/me/` - Get current user's profile
- `GET /api/v1/employees/{id}/` - Get employee details
- `PUT/PATCH /api/v1/employees/{id}/` - Update employee
- `DELETE /api/v1/employees/{id}/` - Soft delete employee
- `GET /api/v1/employees/{id}/vacation-balance/` - Get vacation balance
- `POST /api/v1/employees/{id}/terminate/` - Terminate employee

### Qualification Endpoints
- `GET /api/v1/qualifications/` - List qualifications
- `POST /api/v1/qualifications/` - Create qualification (admin)
- `GET /api/v1/qualifications/{id}/` - Get qualification details
- `PUT/PATCH /api/v1/qualifications/{id}/` - Update qualification
- `DELETE /api/v1/qualifications/{id}/` - Delete qualification

### Document Endpoints
- `GET /api/v1/documents/` - List documents (filtered by permissions)
- `POST /api/v1/documents/` - Upload document
- `GET /api/v1/documents/{id}/` - Get document details
- `DELETE /api/v1/documents/{id}/` - Delete document

---

## 13. Security Considerations

1. **Salary Information**: Restrict access to salary fields to admin/HR only
2. **Personal Data**: GDPR compliance for personal information
3. **Document Access**: Employees can only access their own documents
4. **Termination**: Only admin can terminate employees
5. **Profile Updates**: Employees have limited self-service fields

---

## 14. Integration Points

### With Other Apps:
- **Accounts**: OneToOne with User model
- **Locations**: ForeignKey to primary location, M2M to additional locations
- **Vacation**: Vacation balance tracking
- **Notifications**: Notify on profile updates, terminations

---

## 15. Future Enhancements

- Employee performance reviews
- Training history tracking
- Shift preferences
- Availability calendar
- Emergency contact secondary contacts
- Medical information (if needed)
- Background check tracking

---

## 16. Success Criteria

- ✅ All models created and migrated
- ✅ Django admin fully functional
- ✅ All API endpoints working
- ✅ Proper permissions enforced
- ✅ Validation working correctly
- ✅ Tests passing (>80% coverage)
- ✅ Can create, read, update, delete employees
- ✅ Vacation balance updates automatically
- ✅ Document upload/download working

---

**Next Step**: Begin implementation starting with models.
