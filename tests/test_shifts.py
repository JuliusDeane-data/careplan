"""
Unit tests for Shift Scheduling System (TDD - RED Phase)

These tests define the expected behavior for the shift scheduling system.
Many will FAIL initially because validation methods are not yet implemented.
"""

import pytest
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError

from apps.shifts.models import Shift, ShiftAssignment, ShiftTemplate
from apps.locations.models import Location
from apps.employees.models import Qualification, EmployeeQualification
# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def location(db):
    """Create a test location (ICU unit)."""
    return Location.objects.create(
        name="ICU Unit 1",
        code="ICU1",
        address="123 Hospital St",
        capacity=20,
        is_active=True
    )


@pytest.fixture
def second_location(db):
    """Create a second location for multi-location tests."""
    return Location.objects.create(
        name="ICU Unit 2",
        code="ICU2",
        address="123 Hospital St",
        capacity=15,
        is_active=True
    )


@pytest.fixture
def nurse(create_user):
    """Create a test nurse user."""
    return create_user(
        username='nurse1',
        email='nurse1@hospital.com',
        first_name='Jane',
        last_name='Nurse'
    )


@pytest.fixture
def charge_nurse(create_user):
    """Create a test charge nurse user."""
    return create_user(
        username='charge1',
        email='charge1@hospital.com',
        first_name='John',
        last_name='Charge'
    )


@pytest.fixture
def cna(create_user):
    """Create a test CNA user."""
    return create_user(
        username='cna1',
        email='cna1@hospital.com',
        first_name='Bob',
        last_name='Assistant'
    )


@pytest.fixture
def manager(create_user):
    """Create a test manager user."""
    return create_user(
        username='manager1',
        email='manager1@hospital.com',
        first_name='Mary',
        last_name='Manager',
        is_staff=True
    )


@pytest.fixture
def day_shift(db, location, manager):
    """Create a standard day shift."""
    return Shift.objects.create(
        location=location,
        shift_type=Shift.ShiftType.DAY,
        start_time=time(7, 0),
        end_time=time(19, 0),
        date=date.today() + timedelta(days=1),
        required_staff_count=5,
        required_rn_count=3,
        required_charge_nurse=True,
        is_published=False,
        created_by=manager
    )


@pytest.fixture
def night_shift(db, location, manager):
    """Create a standard night shift (overnight)."""
    return Shift.objects.create(
        location=location,
        shift_type=Shift.ShiftType.NIGHT,
        start_time=time(19, 0),
        end_time=time(7, 0),  # Next day
        date=date.today() + timedelta(days=1),
        required_staff_count=4,
        required_rn_count=2,
        required_charge_nurse=True,
        is_published=False,
        created_by=manager
    )


@pytest.fixture
def shift_template(db, location, manager):
    """Create a shift template."""
    return ShiftTemplate.objects.create(
        name="Monday Day Shift Template",
        location=location,
        day_of_week=0,  # Monday
        shift_type=Shift.ShiftType.DAY,
        start_time=time(7, 0),
        end_time=time(19, 0),
        required_staff_count=5,
        required_rn_count=3,
        required_charge_nurse=True,
        is_active=True,
        created_by=manager
    )


@pytest.fixture
def bls_qualification(db):
    """Create a BLS (Basic Life Support) qualification."""
    return Qualification.objects.create(
        code='BLS',
        name='Basic Life Support',
        category=Qualification.QualificationCategory.MUST_HAVE,
        is_required=True,
        renewal_period_months=24
    )


@pytest.fixture
def nurse_with_bls(nurse, bls_qualification):
    """Create a nurse with valid BLS certification."""
    EmployeeQualification.objects.create(
        employee=nurse,
        qualification=bls_qualification,
        issue_date=date.today() - timedelta(days=180),  # Issued 6 months ago
        expiry_date=date.today() + timedelta(days=550),  # Expires in ~18 months
        status=EmployeeQualification.CertificationStatus.ACTIVE
    )
    return nurse


# ============================================================================
# SHIFT MODEL CREATION TESTS
# ============================================================================

class TestShiftModelCreation:
    """Tests for Shift model creation and basic fields."""

    def test_create_day_shift(self, db, location, manager):
        """Test creating a basic day shift."""
        shift = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today(),
            required_staff_count=5,
            required_rn_count=3,
            required_charge_nurse=True,
            is_published=False,
            created_by=manager
        )
        
        assert shift.id is not None
        assert shift.location == location
        assert shift.shift_type == Shift.ShiftType.DAY
        assert shift.required_staff_count == 5
        assert shift.required_rn_count == 3
        assert shift.required_charge_nurse is True
        assert shift.is_published is False

    def test_create_night_shift(self, db, location, manager):
        """Test creating a night shift with overnight times."""
        shift = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(19, 0),
            end_time=time(7, 0),  # Next day
            date=date.today(),
            required_staff_count=4,
            required_rn_count=2,
            required_charge_nurse=True,
            is_published=False,
            created_by=manager
        )
        
        assert shift.id is not None
        assert shift.shift_type == Shift.ShiftType.NIGHT

    def test_create_on_call_shift(self, db, location, manager):
        """Test creating an on-call shift."""
        shift = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.ON_CALL,
            start_time=time(0, 0),
            end_time=time(23, 59),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=1,
            required_charge_nurse=False,
            is_published=True,
            created_by=manager
        )
        
        assert shift.shift_type == Shift.ShiftType.ON_CALL

    def test_shift_string_representation(self, day_shift):
        """Test shift __str__ method."""
        assert "Day Shift" in str(day_shift)
        assert day_shift.location.name in str(day_shift)

    def test_shift_rn_count_cannot_exceed_staff_count(self, db, location, manager):
        """Test that RN count cannot exceed total staff count."""
        shift = Shift(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today(),
            required_staff_count=3,
            required_rn_count=5,  # More than total!
            required_charge_nurse=False,
            created_by=manager
        )
        
        with pytest.raises(ValidationError):
            shift.clean()


# ============================================================================
# SHIFT ASSIGNMENT MODEL TESTS
# ============================================================================

class TestShiftAssignmentModel:
    """Tests for ShiftAssignment model."""

    def test_create_assignment(self, day_shift, nurse, manager):
        """Test creating a shift assignment."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            status=ShiftAssignment.Status.SCHEDULED,
            assigned_by=manager
        )
        
        assert assignment.id is not None
        assert assignment.shift == day_shift
        assert assignment.employee == nurse
        assert assignment.role == ShiftAssignment.Role.NURSE
        assert assignment.status == ShiftAssignment.Status.SCHEDULED

    def test_create_charge_nurse_assignment(self, day_shift, charge_nurse, manager):
        """Test assigning a charge nurse."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=charge_nurse,
            role=ShiftAssignment.Role.CHARGE_NURSE,
            assigned_by=manager
        )
        
        assert assignment.role == ShiftAssignment.Role.CHARGE_NURSE

    def test_assignment_unique_per_shift(self, day_shift, nurse, manager):
        """Test that an employee can only be assigned once per shift."""
        ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        with pytest.raises(Exception):  # IntegrityError
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=nurse,
                role=ShiftAssignment.Role.CNA,
                assigned_by=manager
            )

    def test_assignment_string_representation(self, day_shift, nurse, manager):
        """Test assignment __str__ method."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        assert nurse.get_full_name() in str(assignment)


# ============================================================================
# SHIFT TEMPLATE MODEL TESTS
# ============================================================================

class TestShiftTemplateModel:
    """Tests for ShiftTemplate model."""

    def test_create_template(self, db, location, manager):
        """Test creating a shift template."""
        template = ShiftTemplate.objects.create(
            name="Weekend Night Template",
            location=location,
            day_of_week=5,  # Saturday
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(19, 0),
            end_time=time(7, 0),
            required_staff_count=4,
            required_rn_count=2,
            required_charge_nurse=True,
            is_active=True,
            created_by=manager
        )
        
        assert template.id is not None
        assert template.name == "Weekend Night Template"
        assert template.day_of_week == 5

    def test_template_string_representation(self, shift_template):
        """Test template __str__ method."""
        assert shift_template.name in str(shift_template)

    def test_create_shift_from_template(self, shift_template):
        """Test creating a shift from a template."""
        # Find next Monday
        today = date.today()
        days_until_monday = (0 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_monday = today + timedelta(days=days_until_monday)
        
        shift = shift_template.create_shift(next_monday)
        
        assert shift.id is not None
        assert shift.location == shift_template.location
        assert shift.shift_type == shift_template.shift_type
        assert shift.date == next_monday
        assert shift.required_staff_count == shift_template.required_staff_count
        assert shift.is_published is False  # Templates create drafts


# ============================================================================
# get_duration_hours() TESTS
# ============================================================================

class TestGetDurationHours:
    """Tests for Shift.get_duration_hours() method."""

    def test_day_shift_duration(self, day_shift):
        """Test that a 07:00-19:00 shift is 12 hours."""
        assert day_shift.get_duration_hours() == 12.0

    def test_night_shift_duration_overnight(self, night_shift):
        """Test that a 19:00-07:00 overnight shift is 12 hours."""
        assert night_shift.get_duration_hours() == 12.0

    def test_short_shift_duration(self, db, location, manager):
        """Test a shorter 4-hour shift."""
        shift = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.ON_CALL,
            start_time=time(14, 0),
            end_time=time(18, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        assert shift.get_duration_hours() == 4.0

    def test_half_hour_precision(self, db, location, manager):
        """Test that half-hour shifts are calculated correctly."""
        shift = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 30),
            end_time=time(16, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        assert shift.get_duration_hours() == 8.5


# ============================================================================
# is_fully_staffed() TESTS
# ============================================================================

class TestIsFullyStaffed:
    """Tests for Shift.is_fully_staffed() method."""

    def test_empty_shift_not_fully_staffed(self, day_shift):
        """Test that a shift with no assignments is not fully staffed."""
        assert day_shift.is_fully_staffed() is False

    def test_partially_staffed_shift(self, day_shift, nurse, manager):
        """Test that a shift with some staff is not fully staffed."""
        ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        # Still needs 4 more staff
        assert day_shift.is_fully_staffed() is False

    def test_fully_staffed_shift(self, day_shift, create_user, manager):
        """Test that a shift meeting all requirements is fully staffed."""
        # Create required staff
        charge = create_user(username='charge_test', email='charge@test.com')
        nurses = [create_user(username=f'nurse_{i}', email=f'nurse{i}@test.com') 
                  for i in range(3)]
        cna = create_user(username='cna_test', email='cna@test.com')
        
        # Assign charge nurse
        ShiftAssignment.objects.create(
            shift=day_shift,
            employee=charge,
            role=ShiftAssignment.Role.CHARGE_NURSE,
            assigned_by=manager
        )
        
        # Assign RNs
        for nurse in nurses[:2]:  # 2 more RNs (charge nurse counts as RN)
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=nurse,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        # Assign CNA to reach total of 5
        ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurses[2],
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        ShiftAssignment.objects.create(
            shift=day_shift,
            employee=cna,
            role=ShiftAssignment.Role.CNA,
            assigned_by=manager
        )
        
        assert day_shift.is_fully_staffed() is True

    def test_missing_charge_nurse_not_fully_staffed(self, day_shift, create_user, manager):
        """Test that missing required charge nurse means not fully staffed."""
        # Create 5 regular nurses but no charge nurse
        nurses = [create_user(username=f'rn_{i}', email=f'rn{i}@test.com') 
                  for i in range(5)]
        
        for nurse in nurses:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=nurse,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        # Has 5 staff, 5 RNs, but NO charge nurse
        assert day_shift.is_fully_staffed() is False


# ============================================================================
# get_coverage_percentage() TESTS
# ============================================================================

class TestGetCoveragePercentage:
    """Tests for Shift.get_coverage_percentage() method."""

    def test_zero_coverage(self, day_shift):
        """Test 0% coverage for empty shift."""
        assert day_shift.get_coverage_percentage() == 0

    def test_partial_coverage(self, day_shift, nurse, manager):
        """Test partial coverage percentage."""
        # Assign 1 of 5 required = 20%
        ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        assert day_shift.get_coverage_percentage() == 20

    def test_full_coverage(self, day_shift, create_user, manager):
        """Test 100% coverage."""
        nurses = [create_user(username=f'cov_{i}', email=f'cov{i}@test.com') 
                  for i in range(5)]
        
        for nurse in nurses:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=nurse,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        assert day_shift.get_coverage_percentage() == 100

    def test_over_staffed_coverage(self, day_shift, create_user, manager):
        """Test coverage can exceed 100% if overstaffed."""
        nurses = [create_user(username=f'extra_{i}', email=f'extra{i}@test.com') 
                  for i in range(7)]
        
        for nurse in nurses:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=nurse,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        # 7 / 5 = 140%
        assert day_shift.get_coverage_percentage() == 140


# ============================================================================
# validate_minimum_rest_period() TESTS - RED (Not Implemented)
# ============================================================================

class TestValidateMinimumRestPeriod:
    """
    Tests for minimum rest period validation.
    EU Working Time Directive requires 11 hours between shifts.
    
    These tests should FAIL because the method is not yet implemented.
    """

    def test_validate_rest_period_sufficient(self, db, location, nurse, manager):
        """Test that 12+ hours between shifts is valid."""
        # Day shift ending at 19:00
        day = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        # Night shift next day starting at 19:00 (24 hours later)
        night = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(19, 0),
            end_time=time(7, 0),
            date=date.today() + timedelta(days=1),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        ShiftAssignment.objects.create(
            shift=day,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        night_assignment = ShiftAssignment(
            shift=night,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        # Should NOT raise - 24 hours > 11 hours
        result = night_assignment.validate_minimum_rest_period()
        assert result is True

    def test_validate_rest_period_insufficient(self, db, location, nurse, manager):
        """Test that less than 11 hours between shifts raises error."""
        # Day shift ending at 19:00
        day = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        # Night shift same day starting at 22:00 (only 3 hours later!)
        night = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(22, 0),
            end_time=time(6, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        ShiftAssignment.objects.create(
            shift=day,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        night_assignment = ShiftAssignment(
            shift=night,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        # Should raise ValidationError - only 3 hours rest
        with pytest.raises(ValidationError) as exc_info:
            night_assignment.validate_minimum_rest_period()
        
        assert "11 hours" in str(exc_info.value) or "rest period" in str(exc_info.value).lower()

    def test_validate_rest_period_exactly_11_hours(self, db, location, nurse, manager):
        """Test that exactly 11 hours rest is valid (boundary case)."""
        # Shift ending at 19:00
        shift1 = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        # Next shift at 06:00 next day (exactly 11 hours)
        shift2 = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(6, 0),
            end_time=time(18, 0),
            date=date.today() + timedelta(days=1),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        ShiftAssignment.objects.create(
            shift=shift1,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        assignment2 = ShiftAssignment(
            shift=shift2,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        # Exactly 11 hours should be valid
        result = assignment2.validate_minimum_rest_period()
        assert result is True


# ============================================================================
# validate_certification_requirements() TESTS - RED (Not Implemented)
# ============================================================================

class TestValidateCertificationRequirements:
    """
    Tests for certification validation.
    Staff must have valid certifications to be assigned to shifts.
    """

    def test_nurse_with_valid_bls_can_be_assigned(self, day_shift, nurse_with_bls, manager):
        """Test that a nurse with valid BLS certification can be assigned."""
        assignment = ShiftAssignment(
            shift=day_shift,
            employee=nurse_with_bls,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        # Should not raise if nurse has valid BLS
        result = assignment.validate_certification_requirements()
        assert result is True

    def test_nurse_without_required_cert_cannot_be_assigned(self, day_shift, nurse, manager):
        """Test that a nurse without required certs cannot be assigned."""
        # Nurse has no certifications
        assignment = ShiftAssignment(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            assignment.validate_certification_requirements()
        
        assert "certification" in str(exc_info.value).lower()

    def test_charge_nurse_requires_experience(self, day_shift, create_user, manager):
        """Test that charge nurse role requires 5+ years experience."""
        new_nurse = create_user(username='newbie', email='newbie@test.com')
        # New nurse has less than 5 years experience
        
        assignment = ShiftAssignment(
            shift=day_shift,
            employee=new_nurse,
            role=ShiftAssignment.Role.CHARGE_NURSE,
            assigned_by=manager
        )
        
        with pytest.raises(ValidationError) as exc_info:
            assignment.validate_certification_requirements()
        
        assert "experience" in str(exc_info.value).lower() or "charge" in str(exc_info.value).lower()


# ============================================================================
# validate_max_consecutive_nights() TESTS - RED (Not Implemented)
# ============================================================================

class TestValidateMaxConsecutiveNights:
    """
    Tests for maximum consecutive night shifts validation.
    Staff should not work more than 4 consecutive night shifts.
    
    These tests should FAIL because the method is not yet implemented.
    """

    def test_four_consecutive_nights_allowed(self, db, location, nurse, manager):
        """Test that 4 consecutive night shifts is allowed."""
        assignments = []
        for i in range(4):
            shift = Shift.objects.create(
                location=location,
                shift_type=Shift.ShiftType.NIGHT,
                start_time=time(19, 0),
                end_time=time(7, 0),
                date=date.today() + timedelta(days=i),
                required_staff_count=1,
                required_rn_count=0,
                required_charge_nurse=False,
                created_by=manager
            )
            assignments.append(ShiftAssignment.objects.create(
                shift=shift,
                employee=nurse,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            ))
        
        # 4th assignment should be valid
        result = assignments[3].validate_max_consecutive_nights()
        assert result is True

    def test_five_consecutive_nights_not_allowed(self, db, location, nurse, manager):
        """Test that 5th consecutive night shift raises error."""
        # Create 4 existing night shifts
        for i in range(4):
            shift = Shift.objects.create(
                location=location,
                shift_type=Shift.ShiftType.NIGHT,
                start_time=time(19, 0),
                end_time=time(7, 0),
                date=date.today() + timedelta(days=i),
                required_staff_count=1,
                required_rn_count=0,
                required_charge_nurse=False,
                created_by=manager
            )
            ShiftAssignment.objects.create(
                shift=shift,
                employee=nurse,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        # Try to assign 5th consecutive night
        fifth_night = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.NIGHT,
            start_time=time(19, 0),
            end_time=time(7, 0),
            date=date.today() + timedelta(days=4),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        fifth_assignment = ShiftAssignment(
            shift=fifth_night,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        with pytest.raises(ValidationError) as exc_info:
            fifth_assignment.validate_max_consecutive_nights()
        
        assert "consecutive" in str(exc_info.value).lower() or "nights" in str(exc_info.value).lower()


# ============================================================================
# validate_skill_mix() TESTS - RED (Not Implemented)
# ============================================================================

class TestValidateSkillMix:
    """
    Tests for skill mix validation.
    Shifts should have at least 60% RN, max 40% CNA.
    
    These tests should FAIL because the method is not yet implemented.
    """

    def test_valid_skill_mix(self, day_shift, create_user, manager):
        """Test that 60% RN + 40% CNA is valid."""
        # 5 staff: 3 RN (60%) + 2 CNA (40%)
        rns = [create_user(username=f'rn_mix_{i}', email=f'rn_mix{i}@test.com') 
               for i in range(3)]
        cnas = [create_user(username=f'cna_mix_{i}', email=f'cna_mix{i}@test.com') 
                for i in range(2)]
        
        for rn in rns:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=rn,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        for cna in cnas:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=cna,
                role=ShiftAssignment.Role.CNA,
                assigned_by=manager
            )
        
        result = day_shift.validate_skill_mix()
        assert result is True

    def test_invalid_skill_mix_too_many_cnas(self, day_shift, create_user, manager):
        """Test that more than 40% CNA raises error."""
        # 5 staff: 2 RN (40%) + 3 CNA (60%) - INVALID
        rns = [create_user(username=f'rn_bad_{i}', email=f'rn_bad{i}@test.com') 
               for i in range(2)]
        cnas = [create_user(username=f'cna_bad_{i}', email=f'cna_bad{i}@test.com') 
                for i in range(3)]
        
        for rn in rns:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=rn,
                role=ShiftAssignment.Role.NURSE,
                assigned_by=manager
            )
        
        for cna in cnas:
            ShiftAssignment.objects.create(
                shift=day_shift,
                employee=cna,
                role=ShiftAssignment.Role.CNA,
                assigned_by=manager
            )
        
        with pytest.raises(ValidationError) as exc_info:
            day_shift.validate_skill_mix()
        
        assert "skill mix" in str(exc_info.value).lower() or "60%" in str(exc_info.value)


# ============================================================================
# conflicts_with_other_shifts() TESTS
# ============================================================================

class TestConflictsWithOtherShifts:
    """Tests for ShiftAssignment.conflicts_with_other_shifts() method."""

    def test_no_conflicts_different_days(self, db, location, nurse, manager):
        """Test no conflicts when shifts are on different days."""
        day1 = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        day2 = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(19, 0),
            date=date.today() + timedelta(days=1),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        ShiftAssignment.objects.create(
            shift=day1,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        new_assignment = ShiftAssignment(
            shift=day2,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        conflicts = new_assignment.conflicts_with_other_shifts()
        assert len(conflicts) == 0

    def test_overlapping_shifts_detected(self, db, location, nurse, manager):
        """Test that overlapping shifts on same day are detected."""
        morning = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(7, 0),
            end_time=time(15, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        afternoon = Shift.objects.create(
            location=location,
            shift_type=Shift.ShiftType.DAY,
            start_time=time(14, 0),  # Overlaps by 1 hour
            end_time=time(22, 0),
            date=date.today(),
            required_staff_count=1,
            required_rn_count=0,
            required_charge_nurse=False,
            created_by=manager
        )
        
        ShiftAssignment.objects.create(
            shift=morning,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        new_assignment = ShiftAssignment(
            shift=afternoon,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            assigned_by=manager
        )
        
        conflicts = new_assignment.conflicts_with_other_shifts()
        assert len(conflicts) == 1


# ============================================================================
# calculate_hours() TESTS
# ============================================================================

class TestCalculateHours:
    """Tests for ShiftAssignment.calculate_hours() method."""

    def test_calculate_hours_scheduled(self, day_shift, nurse, manager):
        """Test hours calculated for scheduled assignment."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            status=ShiftAssignment.Status.SCHEDULED,
            assigned_by=manager
        )
        
        assert assignment.calculate_hours() == 12.0

    def test_calculate_hours_confirmed(self, day_shift, nurse, manager):
        """Test hours calculated for confirmed assignment."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            status=ShiftAssignment.Status.CONFIRMED,
            assigned_by=manager
        )
        
        assert assignment.calculate_hours() == 12.0

    def test_calculate_hours_cancelled_returns_zero(self, day_shift, nurse, manager):
        """Test that cancelled assignments return 0 hours."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            status=ShiftAssignment.Status.CANCELLED,
            assigned_by=manager
        )
        
        assert assignment.calculate_hours() == 0

    def test_calculate_hours_no_show_returns_zero(self, day_shift, nurse, manager):
        """Test that no-show assignments return 0 hours."""
        assignment = ShiftAssignment.objects.create(
            shift=day_shift,
            employee=nurse,
            role=ShiftAssignment.Role.NURSE,
            status=ShiftAssignment.Status.NO_SHOW,
            assigned_by=manager
        )
        
        assert assignment.calculate_hours() == 0
