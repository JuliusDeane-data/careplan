"""
Tests for Shift API Serializers

This module contains comprehensive tests for the shift scheduling serializers.
Tests cover serialization, deserialization, validation, and computed fields.

Author: CarePlan Development Team
"""

import pytest
from datetime import date, time, timedelta
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.shifts.models import Shift, ShiftAssignment, ShiftTemplate
from apps.shifts.serializers import (
    ShiftSerializer,
    ShiftListSerializer,
    ShiftAssignmentSerializer,
    ShiftTemplateSerializer,
    BulkAssignmentSerializer,
    EmployeeMinimalSerializer,
)

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='John',
        last_name='Doe'
    )


@pytest.fixture
def manager(db):
    """Create a test manager user"""
    return User.objects.create_user(
        username='manager',
        email='manager@example.com',
        password='managerpass123',
        first_name='Jane',
        last_name='Manager'
    )


@pytest.fixture
def location(db):
    """Create a test location"""
    from apps.locations.models import Location
    return Location.objects.create(
        name='ICU-1',
        address='123 Main St',
        city='Test City',
        postal_code='12345',
        phone='555-123-4567',
    )


@pytest.fixture
def shift(db, location):
    """Create a test shift"""
    return Shift.objects.create(
        location=location,
        shift_type=Shift.ShiftType.DAY,
        start_time=time(7, 0),
        end_time=time(19, 0),
        date=date.today() + timedelta(days=1),
        required_staff_count=5,
        required_rn_count=3,
        required_charge_nurse=True,
        is_published=False
    )


@pytest.fixture
def shift_assignment(db, shift, user, manager):
    """Create a test shift assignment"""
    return ShiftAssignment.objects.create(
        shift=shift,
        employee=user,
        role=ShiftAssignment.Role.NURSE,
        status=ShiftAssignment.Status.SCHEDULED,
        assigned_by=manager
    )


@pytest.fixture
def shift_template(db, location):
    """Create a test shift template"""
    return ShiftTemplate.objects.create(
        name='Standard Day Shift',
        location=location,
        day_of_week=0,  # Monday
        shift_type=Shift.ShiftType.DAY,
        start_time=time(7, 0),
        end_time=time(19, 0),
        required_staff_count=5,
        required_rn_count=3,
        required_charge_nurse=True,
        is_active=True
    )


# ============================================================================
# Test 1: ShiftSerializer - Serialization with Computed Fields
# ============================================================================

@pytest.mark.django_db
class TestShiftSerializerSerialization:
    """Test ShiftSerializer serialization and computed fields"""

    def test_shift_serialization_includes_all_fields(self, shift):
        """Verify all expected fields are included in serialization"""
        serializer = ShiftSerializer(shift)
        data = serializer.data
        
        # Check core fields
        assert data['id'] == shift.id
        assert data['shift_type'] == 'DAY'
        assert data['start_time'] == '07:00:00'
        assert data['end_time'] == '19:00:00'
        assert data['required_staff_count'] == 5
        assert data['required_rn_count'] == 3
        assert data['required_charge_nurse'] is True
        assert data['is_published'] is False

    def test_shift_computed_fields_empty_assignments(self, shift):
        """Verify computed fields work correctly with no assignments"""
        serializer = ShiftSerializer(shift)
        data = serializer.data
        
        assert data['assigned_count'] == 0
        assert data['rn_count'] == 0
        assert data['has_charge_nurse'] is False
        assert data['is_fully_staffed'] is False
        assert data['coverage_percentage'] == 0
        assert data['duration_hours'] == 12.0

    def test_shift_computed_fields_with_assignments(self, shift, shift_assignment):
        """Verify computed fields update with assignments"""
        serializer = ShiftSerializer(shift)
        data = serializer.data
        
        assert data['assigned_count'] == 1
        assert data['rn_count'] == 1  # NURSE counts as RN
        assert data['is_fully_staffed'] is False  # Still not fully staffed
        assert data['coverage_percentage'] == 20  # 1/5 = 20%

    def test_shift_includes_display_fields(self, shift):
        """Verify display fields are included"""
        serializer = ShiftSerializer(shift)
        data = serializer.data
        
        assert data['shift_type_display'] == 'Day Shift (07:00-19:00)'
        assert data['location_name'] == 'ICU-1'


# ============================================================================
# Test 2: ShiftSerializer - Validation
# ============================================================================

@pytest.mark.django_db
class TestShiftSerializerValidation:
    """Test ShiftSerializer validation logic"""

    def test_valid_shift_data_passes_validation(self, location):
        """Verify valid data passes validation"""
        data = {
            'location': location.id,
            'shift_type': 'DAY',
            'start_time': '07:00:00',
            'end_time': '19:00:00',
            'date': str(date.today() + timedelta(days=2)),
            'required_staff_count': 5,
            'required_rn_count': 3,
            'required_charge_nurse': True,
        }
        serializer = ShiftSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_rn_count_exceeds_staff_count_fails(self, location):
        """Verify RN count > staff count raises validation error"""
        data = {
            'location': location.id,
            'shift_type': 'DAY',
            'start_time': '07:00:00',
            'end_time': '19:00:00',
            'date': str(date.today() + timedelta(days=2)),
            'required_staff_count': 3,
            'required_rn_count': 5,  # More than staff count!
            'required_charge_nurse': False,
        }
        serializer = ShiftSerializer(data=data)
        assert not serializer.is_valid()
        assert 'required_rn_count' in serializer.errors


# ============================================================================
# Test 3: ShiftAssignmentSerializer - Nested Employee Data
# ============================================================================

@pytest.mark.django_db
class TestShiftAssignmentSerializer:
    """Test ShiftAssignmentSerializer with nested data"""

    def test_assignment_includes_nested_employee(self, shift_assignment):
        """Verify nested employee data is included"""
        serializer = ShiftAssignmentSerializer(shift_assignment)
        data = serializer.data
        
        assert 'employee' in data
        assert data['employee']['username'] == 'testuser'
        assert data['employee']['full_name'] == 'John Doe'
        assert data['employee']['email'] == 'test@example.com'

    def test_assignment_includes_assigned_by(self, shift_assignment):
        """Verify assigned_by data is included"""
        serializer = ShiftAssignmentSerializer(shift_assignment)
        data = serializer.data
        
        assert 'assigned_by' in data
        assert data['assigned_by']['username'] == 'manager'
        assert data['assigned_by']['full_name'] == 'Jane Manager'

    def test_assignment_computed_hours(self, shift_assignment):
        """Verify hours calculation works"""
        serializer = ShiftAssignmentSerializer(shift_assignment)
        data = serializer.data
        
        assert data['hours'] == 12.0  # 07:00 to 19:00

    def test_assignment_display_fields(self, shift_assignment):
        """Verify display fields are included"""
        serializer = ShiftAssignmentSerializer(shift_assignment)
        data = serializer.data
        
        assert data['role_display'] == 'Registered Nurse (RN)'
        assert data['status_display'] == 'Scheduled'

    def test_assignment_write_with_employee_id(self, shift, user):
        """Verify assignment can be created with employee_id"""
        data = {
            'shift': shift.id,
            'employee_id': user.id,
            'role': 'CHARGE_NURSE',
        }
        serializer = ShiftAssignmentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors


# ============================================================================
# Test 4: ShiftAssignmentSerializer - Duplicate Validation
# ============================================================================

@pytest.mark.django_db
class TestShiftAssignmentDuplicateValidation:
    """Test duplicate assignment prevention"""

    def test_duplicate_assignment_fails(self, shift, user, shift_assignment):
        """Verify duplicate employee assignment to same shift fails"""
        data = {
            'shift': shift.id,
            'employee_id': user.id,  # Same user already assigned
            'role': 'CNA',
        }
        serializer = ShiftAssignmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'employee_id' in serializer.errors

    def test_same_employee_different_shift_succeeds(self, location, user, shift_assignment):
        """Verify same employee can be assigned to different shifts"""
        # Create a different shift
        different_shift = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(19, 0),
            end_time=time(7, 0),
            date=date.today() + timedelta(days=2),
            required_staff_count=3,
            required_rn_count=2,
        )
        
        data = {
            'shift': different_shift.id,
            'employee_id': user.id,
            'role': 'NURSE',
        }
        serializer = ShiftAssignmentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors


# ============================================================================
# Test 5: ShiftTemplateSerializer - Full CRUD
# ============================================================================

@pytest.mark.django_db
class TestShiftTemplateSerializer:
    """Test ShiftTemplateSerializer serialization and validation"""

    def test_template_serialization(self, shift_template):
        """Verify template serialization includes all fields"""
        serializer = ShiftTemplateSerializer(shift_template)
        data = serializer.data
        
        assert data['name'] == 'Standard Day Shift'
        assert data['day_of_week'] == 0
        assert data['day_of_week_display'] == 'Monday'
        assert data['shift_type'] == 'DAY'
        assert data['shift_type_display'] == 'Day Shift (07:00-19:00)'
        assert data['location_name'] == 'ICU-1'
        assert data['is_active'] is True

    def test_template_duration_hours_day_shift(self, shift_template):
        """Verify duration calculation for day shift"""
        serializer = ShiftTemplateSerializer(shift_template)
        data = serializer.data
        
        assert data['duration_hours'] == 12.0

    def test_template_duration_hours_night_shift(self, location):
        """Verify duration calculation for overnight shift"""
        night_template = ShiftTemplate.objects.create(
            name='Night Shift',
            location=location,
            day_of_week=0,
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(19, 0),
            end_time=time(7, 0),  # Next day
            required_staff_count=4,
            is_active=True
        )
        
        serializer = ShiftTemplateSerializer(night_template)
        data = serializer.data
        
        assert data['duration_hours'] == 12.0

    def test_template_validation_rn_exceeds_staff(self, location):
        """Verify validation prevents RN count > staff count"""
        data = {
            'name': 'Invalid Template',
            'location': location.id,
            'day_of_week': 1,
            'shift_type': 'DAY',
            'start_time': '07:00:00',
            'end_time': '19:00:00',
            'required_staff_count': 3,
            'required_rn_count': 5,  # Invalid!
            'is_active': True,
        }
        serializer = ShiftTemplateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'required_rn_count' in serializer.errors


# ============================================================================
# Test 6: BulkAssignmentSerializer - Bulk Operations
# ============================================================================

@pytest.mark.django_db
class TestBulkAssignmentSerializer:
    """Test BulkAssignmentSerializer for bulk operations"""

    def test_valid_bulk_assignment(self, user, manager):
        """Verify valid bulk assignment data passes"""
        data = {
            'employee_ids': [user.id, manager.id],
            'role': 'NURSE',
            'notes': 'Bulk assignment for coverage',
        }
        serializer = BulkAssignmentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_employee_ids_fails(self):
        """Verify empty employee list fails validation"""
        data = {
            'employee_ids': [],
            'role': 'NURSE',
        }
        serializer = BulkAssignmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'employee_ids' in serializer.errors

    def test_invalid_employee_ids_fails(self, user):
        """Verify invalid employee IDs are rejected"""
        data = {
            'employee_ids': [user.id, 99999],  # 99999 doesn't exist
            'role': 'NURSE',
        }
        serializer = BulkAssignmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'employee_ids' in serializer.errors
        assert '99999' in str(serializer.errors['employee_ids'])

    def test_invalid_role_fails(self, user):
        """Verify invalid role is rejected"""
        data = {
            'employee_ids': [user.id],
            'role': 'INVALID_ROLE',
        }
        serializer = BulkAssignmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'role' in serializer.errors


# ============================================================================
# Test 7: ShiftListSerializer - Lightweight Serialization
# ============================================================================

@pytest.mark.django_db
class TestShiftListSerializer:
    """Test ShiftListSerializer for calendar/list views"""

    def test_list_serializer_excludes_assignments(self, shift, shift_assignment):
        """Verify list serializer doesn't include nested assignments"""
        serializer = ShiftListSerializer(shift)
        data = serializer.data
        
        # Should not have assignments
        assert 'assignments' not in data
        
        # Should still have computed fields
        assert data['assigned_count'] == 1
        assert data['is_fully_staffed'] is False
        assert data['coverage_percentage'] == 20

    def test_list_serializer_fields(self, shift):
        """Verify list serializer has essential fields"""
        serializer = ShiftListSerializer(shift)
        data = serializer.data
        
        expected_fields = [
            'id', 'location', 'location_name', 'shift_type',
            'shift_type_display', 'start_time', 'end_time', 'date',
            'required_staff_count', 'is_published', 'assigned_count',
            'is_fully_staffed', 'coverage_percentage', 'duration_hours'
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"


# ============================================================================
# Test 8: EmployeeMinimalSerializer - Fallback Logic
# ============================================================================

@pytest.mark.django_db
class TestEmployeeMinimalSerializer:
    """Test EmployeeMinimalSerializer full_name fallback"""

    def test_full_name_with_names(self, user):
        """Verify full_name with first and last name"""
        serializer = EmployeeMinimalSerializer(user)
        data = serializer.data
        
        assert data['full_name'] == 'John Doe'

    def test_full_name_fallback_to_username(self, db):
        """Verify full_name falls back to username when no names set"""
        user_no_name = User.objects.create_user(
            username='noname_user',
            email='noname@example.com',
            password='testpass123'
        )
        serializer = EmployeeMinimalSerializer(user_no_name)
        data = serializer.data
        
        assert data['full_name'] == 'noname_user'
