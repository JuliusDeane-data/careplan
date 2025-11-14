"""
Certification API Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.employees.models import Qualification, EmployeeQualification
from apps.api.serializers.users import UserSerializer

User = get_user_model()


class QualificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Qualification model
    """
    renewal_period_display = serializers.SerializerMethodField()

    class Meta:
        model = Qualification
        fields = [
            'id', 'code', 'name', 'description', 'category',
            'required_for_roles', 'is_required', 'renewal_period_months',
            'renewal_period_display', 'issuing_organization', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_renewal_period_display(self, obj):
        """Get human-readable renewal period"""
        return obj.get_renewal_period_display()


class QualificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for qualification lists
    """
    class Meta:
        model = Qualification
        fields = ['id', 'code', 'name', 'category', 'is_required', 'is_active']


class EmployeeQualificationSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeQualification model (employee certifications)
    """
    employee = UserSerializer(read_only=True)
    qualification = QualificationListSerializer(read_only=True)
    qualification_id = serializers.PrimaryKeyRelatedField(
        queryset=Qualification.objects.filter(is_active=True),
        source='qualification',
        write_only=True,
        required=True
    )
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        source='employee',
        write_only=True,
        required=False  # Will be set from context in views
    )
    verified_by = UserSerializer(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    expiry_warning_level = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeQualification
        fields = [
            'id', 'employee', 'employee_id', 'qualification', 'qualification_id',
            'issue_date', 'expiry_date', 'certificate_document',
            'verified_by', 'verified_at', 'status', 'notes',
            'days_until_expiry', 'expiry_warning_level', 'is_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'status', 'verified_by', 'verified_at',
            'created_at', 'updated_at'
        ]

    def get_days_until_expiry(self, obj):
        """Get days until expiry"""
        return obj.days_until_expiry()

    def get_expiry_warning_level(self, obj):
        """Get expiry warning level"""
        return obj.get_expiry_warning_level()

    def get_is_verified(self, obj):
        """Check if certification is verified"""
        return obj.is_verified()


class EmployeeQualificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating employee certifications
    """
    qualification_id = serializers.PrimaryKeyRelatedField(
        queryset=Qualification.objects.filter(is_active=True),
        source='qualification',
        required=True
    )

    class Meta:
        model = EmployeeQualification
        fields = [
            'qualification_id', 'issue_date', 'expiry_date',
            'certificate_document', 'notes'
        ]

    def create(self, validated_data):
        """Create certification with employee from context"""
        # Employee will be set in the view
        return super().create(validated_data)


class EmployeeQualificationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating employee certifications
    """
    class Meta:
        model = EmployeeQualification
        fields = [
            'issue_date', 'expiry_date', 'certificate_document', 'notes'
        ]


class CertificationVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying a certification
    """
    verify = serializers.BooleanField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_verify(self, value):
        """Ensure verify is True"""
        if not value:
            raise serializers.ValidationError("Set verify to true to verify certification")
        return value


class ExpiringCertificationsSerializer(serializers.ModelSerializer):
    """
    Serializer for expiring certifications report
    """
    employee = UserSerializer(read_only=True)
    qualification = QualificationListSerializer(read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    expiry_warning_level = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    employee_location = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeQualification
        fields = [
            'id', 'employee', 'employee_name', 'employee_location',
            'qualification', 'issue_date', 'expiry_date',
            'days_until_expiry', 'expiry_warning_level', 'status'
        ]

    def get_days_until_expiry(self, obj):
        """Get days until expiry"""
        return obj.days_until_expiry()

    def get_expiry_warning_level(self, obj):
        """Get expiry warning level"""
        return obj.get_expiry_warning_level()

    def get_employee_name(self, obj):
        """Get employee full name"""
        return obj.employee.get_full_name()

    def get_employee_location(self, obj):
        """Get employee primary location"""
        if obj.employee.primary_location:
            return {
                'id': obj.employee.primary_location.id,
                'name': obj.employee.primary_location.name,
                'code': obj.employee.primary_location.code
            }
        return None
