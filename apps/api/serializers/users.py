"""
User API Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.locations.models import Location
from apps.employees.models import Qualification

User = get_user_model()


class LocationBasicSerializer(serializers.ModelSerializer):
    """Basic location information"""
    class Meta:
        model = Location
        fields = ['id', 'name', 'code', 'city', 'state']


class QualificationSerializer(serializers.ModelSerializer):
    """Qualification serializer"""
    class Meta:
        model = Qualification
        fields = ['id', 'name', 'code', 'description', 'is_active']


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for lists"""
    primary_location = LocationBasicSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'employee_id',
            'role', 'employment_status', 'is_active', 'primary_location',
            'remaining_vacation_days', 'annual_vacation_days', 'phone'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all relationships"""
    primary_location = LocationBasicSerializer(read_only=True)
    additional_locations = LocationBasicSerializer(many=True, read_only=True)
    qualifications = QualificationSerializer(many=True, read_only=True)
    supervisor = UserSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'employee_id',
            'phone', 'date_of_birth', 'address', 'city', 'state',
            'postal_code', 'emergency_contact_name', 'emergency_contact_phone',
            'hire_date', 'termination_date', 'employment_status', 'role',
            'primary_location', 'additional_locations', 'qualifications',
            'supervisor', 'remaining_vacation_days', 'annual_vacation_days',
            'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    primary_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )
    additional_locations = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.filter(is_active=True),
        many=True,
        required=False
    )
    qualifications = serializers.PrimaryKeyRelatedField(
        queryset=Qualification.objects.filter(is_active=True),
        many=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'date_of_birth',
            'address', 'city', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone',
            'primary_location', 'additional_locations', 'qualifications'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    primary_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name', 'employee_id',
            'phone', 'date_of_birth', 'address', 'city', 'state',
            'postal_code', 'hire_date', 'employment_status', 'role',
            'primary_location', 'annual_vacation_days'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value

    def validate_new_password(self, value):
        # Add custom password validation if needed
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        return value
