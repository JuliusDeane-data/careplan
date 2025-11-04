"""
Core models - Base abstract models for the Careplan project.

These models provide common functionality like timestamps, soft delete,
and audit trails that can be inherited by other models.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that adds created_at and updated_at timestamps.
    All models should inherit from this or BaseModel.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteQuerySet(models.QuerySet):
    """Custom QuerySet with soft delete functionality."""

    def delete(self):
        """Soft delete all objects in the queryset."""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Permanently delete all objects in the queryset."""
        return super().delete()

    def alive(self):
        """Return only non-deleted objects."""
        return self.filter(is_deleted=False)

    def dead(self):
        """Return only deleted objects."""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default."""

    def get_queryset(self):
        """Return queryset excluding soft-deleted objects."""
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class SoftDeleteModel(models.Model):
    """
    Abstract base model that implements soft delete functionality.
    Objects are marked as deleted instead of being removed from the database.
    """
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Indicates if this object has been soft deleted'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the object was soft deleted'
    )
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted_objects',
        help_text='User who deleted this object'
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """
        Soft delete this object.

        Args:
            user: The user performing the deletion (optional)
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user:
            self.deleted_by = user
        self.save()

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()


class AuditModel(models.Model):
    """
    Abstract base model that tracks who created and last updated an object.
    """
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text='User who created this object'
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text='User who last updated this object'
    )

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel, AuditModel):
    """
    Ultimate base model combining timestamps, soft delete, and audit tracking.
    Use this as the base for most models in the application.

    Features:
    - Automatic created_at and updated_at timestamps
    - Soft delete functionality (is_deleted, deleted_at, deleted_by)
    - Audit trail (created_by, updated_by)
    - Custom manager that excludes soft-deleted objects
    """

    class Meta:
        abstract = True
