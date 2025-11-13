"""
Employee-related models (Qualifications, Certifications, Documents, and Skills).
Employee data is now part of the User model in apps.accounts.
"""

from django.db import models
from datetime import date, timedelta
from django.utils import timezone
from apps.core.models import BaseModel


class Qualification(BaseModel):
    """
    Qualifications and certifications for employees.
    Examples: RN (Registered Nurse), CNA (Certified Nursing Assistant), ACLS, BLS, etc.

    This model defines the TYPE of qualification. Individual employee certifications
    are tracked in the EmployeeQualification model.
    """

    class QualificationCategory(models.TextChoices):
        """Categories for qualification priority and requirements."""
        MUST_HAVE = 'MUST_HAVE', 'Must Have (Cannot work without)'
        SPECIALIZED = 'SPECIALIZED', 'Specialized (Required for specific roles)'
        OPTIONAL = 'OPTIONAL', 'Optional (Professional development)'

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Unique qualification code (e.g., RN, CNA, ACLS, BLS)'
    )
    name = models.CharField(
        max_length=100,
        help_text='Full name of the qualification'
    )
    description = models.TextField(
        blank=True,
        help_text='Detailed description of this qualification'
    )
    category = models.CharField(
        max_length=20,
        choices=QualificationCategory.choices,
        default=QualificationCategory.OPTIONAL,
        help_text='How critical is this qualification?'
    )
    required_for_roles = models.TextField(
        blank=True,
        help_text='Which roles require this qualification (e.g., "RN, NURSE")'
    )
    is_required = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Is this required for employment (affects scheduling)'
    )
    renewal_period_months = models.IntegerField(
        null=True,
        blank=True,
        help_text='How often must this be renewed? (e.g., 24 for BLS/ACLS)'
    )
    issuing_organization = models.CharField(
        max_length=200,
        blank=True,
        help_text='Organization that issues this qualification (e.g., AHA, Red Cross)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Is this qualification still being used/tracked?'
    )

    class Meta:
        db_table = 'qualifications'
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_required']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_renewal_period_display(self):
        """Return human-readable renewal period."""
        if not self.renewal_period_months:
            return "No expiration"
        years = self.renewal_period_months // 12
        months = self.renewal_period_months % 12
        if years and months:
            return f"{years} year(s) {months} month(s)"
        elif years:
            return f"{years} year(s)"
        else:
            return f"{months} month(s)"


class EmployeeQualification(BaseModel):
    """
    Junction model tracking which employees have which qualifications.
    This represents an individual employee's certification/qualification instance.

    Example: John Smith (employee) has ACLS (qualification) issued 2023-01-15, expires 2025-01-15
    """

    # Threshold for expiry warning (in days)
    EXPIRY_WARNING_DAYS = 30

    class CertificationStatus(models.TextChoices):
        """Status of this specific certification."""
        ACTIVE = 'ACTIVE', 'Active (Valid and current)'
        EXPIRING_SOON = 'EXPIRING_SOON', 'Expiring Soon (Within warning period)'
        EXPIRED = 'EXPIRED', 'Expired (Past expiry date)'
        PENDING_VERIFICATION = 'PENDING_VERIFICATION', 'Pending Verification'

    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='certifications',
        help_text='Employee who holds this certification'
    )
    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.PROTECT,  # Don't delete qualifications if certs exist
        related_name='employee_certifications',
        help_text='Type of qualification/certification'
    )
    issue_date = models.DateField(
        help_text='Date when this certification was issued'
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,  # Important for querying expiring certs
        help_text='Date when this certification expires (null if non-expiring)'
    )
    certificate_document = models.FileField(
        upload_to='certifications/%Y/%m/',
        null=True,
        blank=True,
        help_text='Uploaded certificate document (PDF, image, etc.)'
    )
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_certifications',
        help_text='Manager/admin who verified this certification'
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this certification was verified'
    )
    status = models.CharField(
        max_length=30,
        choices=CertificationStatus.choices,
        default=CertificationStatus.ACTIVE,
        db_index=True,
        help_text='Current status of this certification'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this certification'
    )

    class Meta:
        db_table = 'employee_qualifications'
        verbose_name = 'Employee Certification'
        verbose_name_plural = 'Employee Certifications'
        ordering = ['-issue_date']
        unique_together = [['employee', 'qualification', 'issue_date']]  # One cert per employee per qual per issue date
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['status']),
            models.Index(fields=['qualification']),
        ]

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.qualification.code}"

    def save(self, *args, **kwargs):
        """Auto-update status based on expiry date before saving."""
        self.status = self.calculate_status()
        super().save(*args, **kwargs)

    def calculate_status(self):
        """
        Calculate the current status based on expiry date.

        Returns:
            str: One of the CertificationStatus choices
        """
        # If no expiry date, check verification status
        if not self.expiry_date:
            if self.verified_by and self.verified_at:
                return self.CertificationStatus.ACTIVE
            else:
                return self.CertificationStatus.PENDING_VERIFICATION

        # Check if expired
        if self.is_expired():
            return self.CertificationStatus.EXPIRED

        # Check if expiring soon (within threshold days)
        if self.is_expiring_soon(days=self.EXPIRY_WARNING_DAYS):
            return self.CertificationStatus.EXPIRING_SOON

        # Check verification for non-expired certs
        if not self.verified_by or not self.verified_at:
            return self.CertificationStatus.PENDING_VERIFICATION

        return self.CertificationStatus.ACTIVE

    def is_expired(self):
        """
        Check if this certification has expired.

        Returns:
            bool: True if expired, False otherwise
        """
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()

    def is_expiring_soon(self, days=30):
        """
        Check if this certification is expiring within X days.

        Args:
            days (int): Number of days to check ahead

        Returns:
            bool: True if expiring within the specified days
        """
        if not self.expiry_date or self.is_expired():
            return False
        threshold_date = date.today() + timedelta(days=days)
        return self.expiry_date <= threshold_date

    def days_until_expiry(self):
        """
        Calculate days until this certification expires.

        Returns:
            int: Days until expiry (negative if already expired, None if no expiry)
        """
        if not self.expiry_date:
            return None
        delta = self.expiry_date - date.today()
        return delta.days

    def is_verified(self):
        """
        Check if this certification has been verified by a manager.

        Returns:
            bool: True if verified
        """
        return bool(self.verified_by and self.verified_at)

    def verify(self, verified_by_user):
        """
        Mark this certification as verified.

        Args:
            verified_by_user: User object who is verifying
        """
        self.verified_by = verified_by_user
        self.verified_at = timezone.now()
        self.save()

    def get_expiry_warning_level(self):
        """
        Get the urgency level of expiry warning.

        Returns:
            str: 'CRITICAL' (< 14 days), 'HIGH' (< 30 days), 'MEDIUM' (< 60 days), 'LOW' (< 90 days), or None
        """
        days = self.days_until_expiry()
        if days is None or days < 0:
            return None

        if days <= 14:
            return 'CRITICAL'
        elif days <= 30:
            return 'HIGH'
        elif days <= 60:
            return 'MEDIUM'
        elif days <= 90:
            return 'LOW'
        return None


class EmployeeDocument(BaseModel):
    """
    Document storage for employee-related files.
    Links to User model (which now contains employee data).
    """

    class DocumentType(models.TextChoices):
        """Document type choices."""
        CONTRACT = 'CONTRACT', 'Employment Contract'
        CERTIFICATE = 'CERTIFICATE', 'Certificate/Qualification'
        ID_DOCUMENT = 'ID_DOCUMENT', 'Identification Document'
        TRAINING = 'TRAINING', 'Training Certificate'
        OTHER = 'OTHER', 'Other'

    employee = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='documents',
        help_text='Employee (User) this document belongs to'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices
    )
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='employee_documents/',
        help_text='Uploaded document file'
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expiry date for certificates/documents'
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'employee_documents'
        verbose_name = 'Employee Document'
        verbose_name_plural = 'Employee Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"

    def is_expired(self):
        """Check if document has expired."""
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()
