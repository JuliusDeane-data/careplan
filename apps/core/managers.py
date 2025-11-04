"""
Custom managers and querysets for optimized database queries.
"""

from django.db import models


class OptimizedQuerySet(models.QuerySet):
    """
    QuerySet with common query optimization methods.
    """

    def with_user(self):
        """Automatically select_related common User foreign keys."""
        return self.select_related('created_by', 'updated_by')

    def with_location(self):
        """Automatically select_related Location."""
        return self.select_related('location')

    def active(self):
        """Filter for active records (is_active=True)."""
        return self.filter(is_active=True)

    def inactive(self):
        """Filter for inactive records (is_active=False)."""
        return self.filter(is_active=False)


class OptimizedManager(models.Manager):
    """Manager that returns OptimizedQuerySet."""

    def get_queryset(self):
        """Return OptimizedQuerySet."""
        return OptimizedQuerySet(self.model, using=self._db)

    def active(self):
        """Shortcut for active records."""
        return self.get_queryset().active()

    def inactive(self):
        """Shortcut for inactive records."""
        return self.get_queryset().inactive()
