"""
Shift API Serializers for ICU Workforce Management

This module provides Django REST Framework serializers for the shift scheduling system.
Includes serializers for Shift, ShiftAssignment, and ShiftTemplate models with
computed fields for staffing status and validation.

Author: CarePlan Development Team
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Shift, ShiftAssignment, ShiftTemplate

User = get_user_model()


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal employee representation for nested use in shift assignments.
    Provides essential employee info without circular references.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields

    def get_full_name(self, obj):
        """Return full name or username as fallback"""
        full_name = obj.get_full_name()
        return full_name if full_name.strip() else obj.username


class ShiftAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for ShiftAssignment model.
    
    Provides nested employee data for read operations and accepts
    employee_id for write operations. Includes computed fields for
    hours calculation and conflict detection.
    """
    # Nested read-only employee data
    employee = EmployeeMinimalSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='employee',
        write_only=True,
        help_text="ID of the employee to assign"
    )
    
    # Nested read-only assigned_by data
    assigned_by = EmployeeMinimalSerializer(read_only=True)
    
    # Computed fields
    hours = serializers.SerializerMethodField(
        help_text="Calculated hours for this assignment"
    )
    has_conflicts = serializers.SerializerMethodField(
        help_text="Whether this assignment conflicts with other shifts"
    )
    role_display = serializers.CharField(
        source='get_role_display',
        read_only=True,
        help_text="Human-readable role name"
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
        help_text="Human-readable status name"
    )

    class Meta:
        model = ShiftAssignment
        fields = [
            'id',
            'shift',
            'employee',
            'employee_id',
            'role',
            'role_display',
            'status',
            'status_display',
            'assigned_by',
            'assigned_at',
            'notes',
            'hours',
            'has_conflicts',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'assigned_by',
            'assigned_at',
            'hours',
            'has_conflicts',
            'created_at',
            'updated_at',
        ]

    def get_hours(self, obj):
        """Calculate hours worked for this assignment"""
        return obj.calculate_hours()

    def get_has_conflicts(self, obj):
        """Check if this assignment has scheduling conflicts"""
        return len(obj.conflicts_with_other_shifts()) > 0

    def validate(self, attrs):
        """
        Validate assignment data.
        Currently checks only for duplicate assignments (same employee on the same shift).
        """
        shift = attrs.get('shift') or (self.instance.shift if self.instance else None)
        employee = attrs.get('employee') or (self.instance.employee if self.instance else None)
        
        if shift and employee:
            # Check for duplicate assignment (same employee to same shift)
            existing = ShiftAssignment.objects.filter(
                shift=shift,
                employee=employee
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'employee_id': 'This employee is already assigned to this shift.'
                })
        
        return attrs


class ShiftAssignmentCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating shift assignments.
    Used for bulk operations and simple assignment creation.
    """
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='employee',
        help_text="ID of the employee to assign"
    )

    class Meta:
        model = ShiftAssignment
        fields = ['employee_id', 'role', 'notes']


class ShiftSerializer(serializers.ModelSerializer):
    """
    Full serializer for Shift model.
    
    Includes all fields, nested assignments, and computed fields
    for staffing status. Used for detail views and full CRUD operations.
    """
    # Nested assignments (read-only, use separate endpoints to manage)
    assignments = ShiftAssignmentSerializer(many=True, read_only=True)
    
    # Computed staffing fields
    assigned_count = serializers.SerializerMethodField(
        help_text="Number of staff currently assigned"
    )
    rn_count = serializers.SerializerMethodField(
        help_text="Number of RNs currently assigned"
    )
    has_charge_nurse = serializers.SerializerMethodField(
        help_text="Whether a charge nurse is assigned"
    )
    is_fully_staffed = serializers.SerializerMethodField(
        help_text="Whether all staffing requirements are met"
    )
    coverage_percentage = serializers.SerializerMethodField(
        help_text="Staffing coverage as percentage (0-100)"
    )
    duration_hours = serializers.SerializerMethodField(
        help_text="Shift duration in hours"
    )
    
    # Display fields
    shift_type_display = serializers.CharField(
        source='get_shift_type_display',
        read_only=True,
        help_text="Human-readable shift type"
    )
    location_name = serializers.CharField(
        source='location.name',
        read_only=True,
        help_text="Name of the location"
    )

    class Meta:
        model = Shift
        fields = [
            'id',
            'location',
            'location_name',
            'shift_type',
            'shift_type_display',
            'start_time',
            'end_time',
            'date',
            'required_staff_count',
            'required_rn_count',
            'required_charge_nurse',
            'notes',
            'is_published',
            # Computed fields
            'assigned_count',
            'rn_count',
            'has_charge_nurse',
            'is_fully_staffed',
            'coverage_percentage',
            'duration_hours',
            # Nested data
            'assignments',
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'assigned_count',
            'rn_count',
            'has_charge_nurse',
            'is_fully_staffed',
            'coverage_percentage',
            'duration_hours',
            'created_at',
            'updated_at',
        ]

    def get_assigned_count(self, obj):
        """Get number of employees assigned to this shift"""
        return obj.get_assigned_count()

    def get_rn_count(self, obj):
        """Get number of RNs assigned"""
        return obj.get_rn_count()

    def get_has_charge_nurse(self, obj):
        """Check if a charge nurse is assigned"""
        return obj.has_charge_nurse()

    def get_is_fully_staffed(self, obj):
        """Check if shift meets all staffing requirements"""
        return obj.is_fully_staffed()

    def get_coverage_percentage(self, obj):
        """Calculate staffing coverage as percentage"""
        return obj.get_coverage_percentage()

    def get_duration_hours(self, obj):
        """Calculate shift duration in hours"""
        return obj.get_duration_hours()

    def validate(self, attrs):
        """
        Validate shift data.
        Ensures RN count doesn't exceed total staff count.
        """
        required_staff_count = attrs.get(
            'required_staff_count',
            self.instance.required_staff_count if self.instance else 0
        )
        required_rn_count = attrs.get(
            'required_rn_count',
            self.instance.required_rn_count if self.instance else 0
        )
        
        if required_rn_count > required_staff_count:
            raise serializers.ValidationError({
                'required_rn_count': 'Required RN count cannot exceed total required staff count.'
            })
        
        return attrs


class ShiftListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Shift list views and calendar displays.
    
    Excludes nested assignments for performance on large lists.
    Use ShiftSerializer for detail views with full data.
    """
    # Computed staffing fields
    assigned_count = serializers.SerializerMethodField()
    is_fully_staffed = serializers.SerializerMethodField()
    coverage_percentage = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    
    # Display fields
    shift_type_display = serializers.CharField(
        source='get_shift_type_display',
        read_only=True
    )
    location_name = serializers.CharField(
        source='location.name',
        read_only=True
    )

    class Meta:
        model = Shift
        fields = [
            'id',
            'location',
            'location_name',
            'shift_type',
            'shift_type_display',
            'start_time',
            'end_time',
            'date',
            'required_staff_count',
            'is_published',
            # Computed fields
            'assigned_count',
            'is_fully_staffed',
            'coverage_percentage',
            'duration_hours',
        ]
        read_only_fields = fields

    def get_assigned_count(self, obj):
        return obj.get_assigned_count()

    def get_is_fully_staffed(self, obj):
        return obj.is_fully_staffed()

    def get_coverage_percentage(self, obj):
        return obj.get_coverage_percentage()

    def get_duration_hours(self, obj):
        return obj.get_duration_hours()


class ShiftTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for ShiftTemplate model.
    
    Used for managing recurring shift patterns that can be used
    to generate shifts automatically.
    """
    # Display fields
    day_of_week_display = serializers.CharField(
        source='get_day_of_week_display',
        read_only=True,
        help_text="Human-readable day name"
    )
    shift_type_display = serializers.CharField(
        source='get_shift_type_display',
        read_only=True,
        help_text="Human-readable shift type"
    )
    location_name = serializers.CharField(
        source='location.name',
        read_only=True,
        help_text="Name of the location"
    )
    
    # Computed field for shift duration
    duration_hours = serializers.SerializerMethodField(
        help_text="Shift duration in hours"
    )

    class Meta:
        model = ShiftTemplate
        fields = [
            'id',
            'name',
            'location',
            'location_name',
            'day_of_week',
            'day_of_week_display',
            'shift_type',
            'shift_type_display',
            'start_time',
            'end_time',
            'required_staff_count',
            'required_rn_count',
            'required_charge_nurse',
            'is_active',
            'duration_hours',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'duration_hours',
            'created_at',
            'updated_at',
        ]

    def get_duration_hours(self, obj):
        """Calculate template shift duration in hours"""
        from datetime import datetime, timedelta, date
        
        # Use a dummy date to calculate duration
        dummy_date = date.today()
        start = datetime.combine(dummy_date, obj.start_time)
        end = datetime.combine(dummy_date, obj.end_time)
        
        # Handle overnight shifts
        if end <= start:
            end += timedelta(days=1)
        
        duration = end - start
        return duration.total_seconds() / 3600

    def validate(self, attrs):
        """
        Validate template data.
        Ensures RN count doesn't exceed total staff count.
        """
        required_staff_count = attrs.get(
            'required_staff_count',
            self.instance.required_staff_count if self.instance else 0
        )
        required_rn_count = attrs.get(
            'required_rn_count',
            self.instance.required_rn_count if self.instance else 0
        )
        
        if required_rn_count > required_staff_count:
            raise serializers.ValidationError({
                'required_rn_count': 'Required RN count cannot exceed total required staff count.'
            })
        
        return attrs


class BulkAssignmentSerializer(serializers.Serializer):
    """
    Serializer for bulk assignment operations.
    
    Allows assigning multiple employees to a shift at once
    with the same role.
    """
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of employee IDs to assign"
    )
    role = serializers.ChoiceField(
        choices=ShiftAssignment.Role.choices,
        help_text="Role for all assignments"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes for all assignments"
    )

    def validate_employee_ids(self, value):
        """Validate that all employee IDs exist"""
        existing_ids = set(
            User.objects.filter(id__in=value).values_list('id', flat=True)
        )
        invalid_ids = set(value) - existing_ids
        
        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid employee IDs: {sorted(invalid_ids)}"
            )
        
        return value


class ShiftValidationResultSerializer(serializers.Serializer):
    """
    Serializer for shift validation results.
    
    Returns validation status with detailed errors and warnings
    for staffing compliance checks.
    """
    is_valid = serializers.BooleanField(
        help_text="Whether the shift meets all requirements"
    )
    errors = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of critical errors that must be fixed"
    )
    warnings = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of warnings that should be reviewed"
    )
