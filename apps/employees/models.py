"""
Employee-related models (Qualifications and Documents).
Employee data is now part of the User model in apps.accounts.
"""

from django.db import models
from datetime import date
from apps.core.models import BaseModel


class Qualification(BaseModel):
    """
    Qualifications and certifications for employees.
    Examples: RN (Registered Nurse), CNA (Certified Nursing Assistant), etc.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text='Unique qualification code (e.g., RN, CNA, LPN)'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    required_for_roles = models.TextField(
        blank=True,
        help_text='Which roles require this qualification'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'qualifications'
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


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
