"""
Vacation API Serializers
"""
from rest_framework import serializers
from apps.vacation.models import VacationRequest, PublicHoliday
from apps.api.serializers.users import UserSerializer


class VacationRequestSerializer(serializers.ModelSerializer):
    """Basic vacation request serializer for list views"""
    employee = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    denied_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)

    class Meta:
        model = VacationRequest
        fields = [
            'id', 'employee', 'start_date', 'end_date', 'vacation_days',
            'total_days', 'request_type', 'request_type_display', 'status',
            'status_display', 'reason', 'approved_by', 'approved_at',
            'denied_by', 'denied_at', 'denial_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'vacation_days', 'total_days', 'status', 'approved_by',
            'approved_at', 'denied_by', 'denied_at', 'created_at', 'updated_at'
        ]


class VacationRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed vacation request serializer"""
    employee = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    denied_by = UserSerializer(read_only=True)
    cancelled_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    is_modifiable = serializers.ReadOnlyField()
    is_cancellable = serializers.ReadOnlyField()
    days_until_start = serializers.ReadOnlyField()

    class Meta:
        model = VacationRequest
        fields = [
            'id', 'employee', 'start_date', 'end_date', 'vacation_days',
            'total_days', 'request_type', 'request_type_display', 'status',
            'status_display', 'reason', 'notes', 'supporting_document',
            'approved_by', 'approved_at', 'denied_by', 'denied_at', 'denial_reason',
            'cancelled_by', 'cancelled_at', 'cancellation_reason',
            'is_modifiable', 'is_cancellable', 'days_until_start',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = [
            'vacation_days', 'total_days', 'status', 'approved_by', 'approved_at',
            'denied_by', 'denied_at', 'cancelled_by', 'cancelled_at',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


class VacationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vacation requests with validation"""

    class Meta:
        model = VacationRequest
        fields = [
            'start_date', 'end_date', 'request_type', 'reason',
            'notes', 'supporting_document'
        ]

    def validate(self, attrs):
        """Run model's clean() validation"""
        # Create a temporary instance for validation
        instance = VacationRequest(**attrs)
        instance.employee = self.context['request'].user

        # Run model validation
        instance.clean()

        return attrs

    def create(self, validated_data):
        """Create vacation request with current user as employee"""
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)


class VacationRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating vacation requests (only certain fields)"""

    class Meta:
        model = VacationRequest
        fields = ['start_date', 'end_date', 'request_type', 'reason', 'notes']

    def validate(self, attrs):
        """Run model's clean() validation"""
        instance = self.instance
        for attr, value in attrs.items():
            setattr(instance, attr, value)

        # Run model validation
        instance.clean()

        return attrs


class PublicHolidaySerializer(serializers.ModelSerializer):
    """Public holiday serializer"""
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = PublicHoliday
        fields = [
            'id', 'date', 'name', 'description', 'location', 'location_name',
            'is_nationwide', 'is_recurring', 'recurring_month', 'recurring_day',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_location_name(self, obj):
        """Get location name if not nationwide"""
        if obj.location:
            return obj.location.name
        return 'Nationwide'
