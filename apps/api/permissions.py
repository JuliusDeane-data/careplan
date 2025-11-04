"""
Custom API Permissions
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the object has a 'user' or 'employee' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'employee'):
            return obj.employee == request.user
        return obj == request.user


class IsAdminOrManager(permissions.BasePermission):
    """
    Permission to only allow admins or managers.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or
            request.user.is_staff or
            request.user.role == 'MANAGER'
        )


class IsOwnerOrAdminOrManager(permissions.BasePermission):
    """
    Permission to allow owners, admins, or managers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin or manager can access anything
        if request.user.is_superuser or request.user.is_staff or request.user.role == 'MANAGER':
            return True

        # Check if owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'employee'):
            return obj.employee == request.user
        return obj == request.user


class IsManagerAtSameLocation(permissions.BasePermission):
    """
    Permission for managers to only manage employees at their location.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Manager can only access users at their location
        if request.user.role == 'MANAGER':
            user_to_check = obj if hasattr(obj, 'primary_location') else getattr(obj, 'employee', None)
            if user_to_check:
                return user_to_check.primary_location == request.user.primary_location

        # Owner can access their own data
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'employee'):
            return obj.employee == request.user
        return obj == request.user
