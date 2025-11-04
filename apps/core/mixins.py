"""
Reusable mixins for Django REST Framework views.
"""


class UserCreatedMixin:
    """
    Mixin to automatically set created_by field from request.

    Use this in DRF CreateAPIView or ViewSets that create objects.
    """

    def perform_create(self, serializer):
        """Set created_by to the current user before saving."""
        serializer.save(created_by=self.request.user)


class UserUpdatedMixin:
    """
    Mixin to automatically set updated_by field from request.

    Use this in DRF UpdateAPIView or ViewSets that update objects.
    """

    def perform_update(self, serializer):
        """Set updated_by to the current user before saving."""
        serializer.save(updated_by=self.request.user)


class UserAuditMixin(UserCreatedMixin, UserUpdatedMixin):
    """
    Combined mixin for both create and update audit tracking.

    Use this in DRF ViewSets that handle both create and update operations.
    """
    pass
