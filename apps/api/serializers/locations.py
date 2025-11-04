"""
Location API Serializers
"""
from rest_framework import serializers
from apps.locations.models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Basic location serializer"""
    manager_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'code', 'address', 'city', 'state', 'postal_code',
            'phone', 'email', 'manager', 'manager_name',
            'employee_count', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_manager_name(self, obj):
        """Get manager's full name"""
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

    def get_employee_count(self, obj):
        """Get count of employees at this location"""
        return obj.primary_employees.filter(is_active=True).count()


class LocationDetailSerializer(serializers.ModelSerializer):
    """Detailed location serializer with manager details"""
    from apps.api.serializers.users import UserSerializer

    manager = UserSerializer(read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'code', 'address', 'city', 'state', 'postal_code',
            'phone', 'email', 'manager', 'employee_count',
            'is_active', 'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']

    def get_employee_count(self, obj):
        """Get count of employees at this location"""
        return obj.primary_employees.filter(is_active=True).count()


class LocationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating locations"""
    class Meta:
        model = Location
        fields = [
            'name', 'code', 'address', 'city', 'state', 'postal_code',
            'phone', 'email', 'manager', 'is_active'
        ]
