"""
Unit tests for the Employee/Qualification system.
Tests cover Qualification, EmployeeQualification, and related methods.
"""

import pytest
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.employees.models import Qualification, EmployeeQualification


User = get_user_model()


@pytest.mark.django_db
class TestQualificationModel(TestCase):
    """Tests for the Qualification model."""

    def test_qualification_creation(self):
        """Test that a Qualification can be created with required fields."""
        qualification = Qualification.objects.create(
            code='RN',
            name='Registered Nurse',
            description='Licensed registered nurse certification',
            category=Qualification.QualificationCategory.MUST_HAVE,
            is_required=True,
            renewal_period_months=24,
            issuing_organization='State Board of Nursing'
        )
        
        self.assertEqual(qualification.code, 'RN')
        self.assertEqual(qualification.name, 'Registered Nurse')
        self.assertEqual(qualification.category, Qualification.QualificationCategory.MUST_HAVE)
        self.assertTrue(qualification.is_required)
        self.assertEqual(qualification.renewal_period_months, 24)
        self.assertTrue(qualification.is_active)

    def test_qualification_str_representation(self):
        """Test the __str__ method returns expected format."""
        qualification = Qualification.objects.create(
            code='ACLS',
            name='Advanced Cardiac Life Support'
        )
        
        self.assertEqual(str(qualification), 'ACLS - Advanced Cardiac Life Support')

    def test_qualification_renewal_period_display_years(self):
        """Test get_renewal_period_display for years only."""
        qualification = Qualification.objects.create(
            code='BLS',
            name='Basic Life Support',
            renewal_period_months=24
        )
        
        self.assertEqual(qualification.get_renewal_period_display(), '2 year(s)')

    def test_qualification_renewal_period_display_months(self):
        """Test get_renewal_period_display for months only."""
        qualification = Qualification.objects.create(
            code='TEST1',
            name='Test Qualification',
            renewal_period_months=6
        )
        
        self.assertEqual(qualification.get_renewal_period_display(), '6 month(s)')

    def test_qualification_renewal_period_display_combined(self):
        """Test get_renewal_period_display for years and months."""
        qualification = Qualification.objects.create(
            code='TEST2',
            name='Test Qualification 2',
            renewal_period_months=18  # 1 year 6 months
        )
        
        self.assertEqual(qualification.get_renewal_period_display(), '1 year(s) 6 month(s)')

    def test_qualification_renewal_period_display_none(self):
        """Test get_renewal_period_display when no renewal period set."""
        qualification = Qualification.objects.create(
            code='PERM',
            name='Permanent Qualification',
            renewal_period_months=None
        )
        
        self.assertEqual(qualification.get_renewal_period_display(), 'No expiration')

    def test_qualification_unique_code(self):
        """Test that qualification codes must be unique."""
        Qualification.objects.create(code='UNIQUE', name='First Qualification')
        
        with self.assertRaises(Exception):  # IntegrityError
            Qualification.objects.create(code='UNIQUE', name='Second Qualification')


@pytest.mark.django_db
class TestEmployeeQualificationModel(TestCase):
    """Tests for the EmployeeQualification model."""

    def setUp(self):
        """Set up test fixtures."""
        self.employee = User.objects.create_user(
            username='john.doe',
            email='john.doe@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.qualification = Qualification.objects.create(
            code='ACLS',
            name='Advanced Cardiac Life Support',
            renewal_period_months=24
        )
        self.verifier = User.objects.create_user(
            username='admin.user',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )

    def test_employee_qualification_creation(self):
        """Test that an EmployeeQualification can be created."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=730)  # 2 years
        )
        
        self.assertEqual(emp_qual.employee, self.employee)
        self.assertEqual(emp_qual.qualification, self.qualification)
        self.assertIsNotNone(emp_qual.issue_date)
        self.assertIsNotNone(emp_qual.expiry_date)

    def test_employee_qualification_str_representation(self):
        """Test the __str__ method returns expected format."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )
        
        expected = f"John Doe - ACLS"
        self.assertEqual(str(emp_qual), expected)

    def test_is_expired_true(self):
        """Test is_expired returns True for expired certifications."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=730),
            expiry_date=date.today() - timedelta(days=1)  # Expired yesterday
        )
        
        self.assertTrue(emp_qual.is_expired())

    def test_is_expired_false(self):
        """Test is_expired returns False for valid certifications."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)  # Expires in a year
        )
        
        self.assertFalse(emp_qual.is_expired())

    def test_is_expired_no_expiry_date(self):
        """Test is_expired returns False when no expiry date set."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=None
        )
        
        self.assertFalse(emp_qual.is_expired())

    def test_is_expiring_soon_true(self):
        """Test is_expiring_soon returns True when expiring within threshold."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=700),
            expiry_date=date.today() + timedelta(days=15)  # Expires in 15 days
        )
        
        self.assertTrue(emp_qual.is_expiring_soon(days=30))

    def test_is_expiring_soon_false(self):
        """Test is_expiring_soon returns False when expiry is far away."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)  # Expires in a year
        )
        
        self.assertFalse(emp_qual.is_expiring_soon(days=30))

    def test_is_expiring_soon_already_expired(self):
        """Test is_expiring_soon returns False when already expired."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=730),
            expiry_date=date.today() - timedelta(days=1)  # Already expired
        )
        
        self.assertFalse(emp_qual.is_expiring_soon(days=30))

    def test_is_expiring_soon_no_expiry_date(self):
        """Test is_expiring_soon returns False when no expiry date."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=None
        )
        
        self.assertFalse(emp_qual.is_expiring_soon(days=30))

    def test_days_until_expiry_positive(self):
        """Test days_until_expiry returns positive days for future expiry."""
        days_ahead = 100
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=days_ahead)
        )
        
        self.assertEqual(emp_qual.days_until_expiry(), days_ahead)

    def test_days_until_expiry_negative(self):
        """Test days_until_expiry returns negative days for past expiry."""
        days_ago = 10
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=730),
            expiry_date=date.today() - timedelta(days=days_ago)
        )
        
        self.assertEqual(emp_qual.days_until_expiry(), -days_ago)

    def test_days_until_expiry_none(self):
        """Test days_until_expiry returns None when no expiry date."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=None
        )
        
        self.assertIsNone(emp_qual.days_until_expiry())

    def test_relationship_employee_to_qualifications(self):
        """Test employee can have multiple qualifications via reverse relation."""
        qual2 = Qualification.objects.create(code='BLS', name='Basic Life Support')
        
        EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=730)
        )
        EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=qual2,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=730)
        )
        
        # Test reverse relation from User to EmployeeQualification
        self.assertEqual(self.employee.certifications.count(), 2)

    def test_relationship_qualification_to_employees(self):
        """Test qualification can be held by multiple employees via reverse relation."""
        employee2 = User.objects.create_user(
            username='jane.doe',
            email='jane.doe@example.com',
            password='testpass123'
        )
        
        EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )
        EmployeeQualification.objects.create(
            employee=employee2,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335)
        )
        
        # Test reverse relation from Qualification to EmployeeQualification
        self.assertEqual(self.qualification.employee_certifications.count(), 2)

    def test_auto_status_update_expired(self):
        """Test that status is auto-updated to EXPIRED on save."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=730),
            expiry_date=date.today() - timedelta(days=1)
        )
        
        self.assertEqual(emp_qual.status, EmployeeQualification.CertificationStatus.EXPIRED)

    def test_auto_status_update_expiring_soon(self):
        """Test that status is auto-updated to EXPIRING_SOON on save."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=700),
            expiry_date=date.today() + timedelta(days=15),
            verified_by=self.verifier,
            verified_at=date.today()
        )
        
        self.assertEqual(emp_qual.status, EmployeeQualification.CertificationStatus.EXPIRING_SOON)

    def test_verify_method(self):
        """Test the verify method sets verified_by and verified_at."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )
        
        self.assertFalse(emp_qual.is_verified())
        
        emp_qual.verify(self.verifier)
        
        self.assertTrue(emp_qual.is_verified())
        self.assertEqual(emp_qual.verified_by, self.verifier)
        self.assertIsNotNone(emp_qual.verified_at)

    def test_get_expiry_warning_level_critical(self):
        """Test expiry warning level returns CRITICAL for < 14 days."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=700),
            expiry_date=date.today() + timedelta(days=10)
        )
        
        self.assertEqual(emp_qual.get_expiry_warning_level(), 'CRITICAL')

    def test_get_expiry_warning_level_high(self):
        """Test expiry warning level returns HIGH for 14-30 days."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today() - timedelta(days=700),
            expiry_date=date.today() + timedelta(days=25)
        )
        
        self.assertEqual(emp_qual.get_expiry_warning_level(), 'HIGH')

    def test_get_expiry_warning_level_none_far_future(self):
        """Test expiry warning level returns None for > 90 days."""
        emp_qual = EmployeeQualification.objects.create(
            employee=self.employee,
            qualification=self.qualification,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )
        
        self.assertIsNone(emp_qual.get_expiry_warning_level())
