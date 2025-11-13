"""
Certification API ViewSets
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import date, timedelta

from apps.employees.models import Qualification, EmployeeQualification
from apps.api.serializers.certifications import (
    QualificationSerializer,
    QualificationListSerializer,
    EmployeeQualificationSerializer,
    EmployeeQualificationCreateSerializer,
    EmployeeQualificationUpdateSerializer,
    CertificationVerifySerializer,
    ExpiringCertificationsSerializer
)
from apps.api.permissions import IsAdminOrManager, IsOwnerOrAdminOrManager

User = get_user_model()


class QualificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Qualification CRUD operations

    Permissions:
    - List/Retrieve: Any authenticated user
    - Create/Update/Delete: Admin or Manager only

    Endpoints:
    - GET /api/certifications/qualifications/ - List all qualifications
    - GET /api/certifications/qualifications/{id}/ - Get qualification details
    - POST /api/certifications/qualifications/ - Create new qualification (Admin/Manager)
    - PUT/PATCH /api/certifications/qualifications/{id}/ - Update qualification (Admin/Manager)
    - DELETE /api/certifications/qualifications/{id}/ - Deactivate qualification (Admin/Manager)
    """
    queryset = Qualification.objects.filter(is_active=True).order_by('category', 'name')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_required', 'is_active']
    search_fields = ['code', 'name', 'description', 'issuing_organization']
    ordering_fields = ['created_at', 'name', 'category', 'renewal_period_months']
    ordering = ['category', 'name']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return QualificationListSerializer
        return QualificationSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrManager()]

    def perform_destroy(self, instance):
        """Soft delete - deactivate instead of deleting"""
        instance.is_active = False
        instance.save()

    @action(detail=False, methods=['get'])
    def required(self, request):
        """
        Get all required qualifications

        GET /api/certifications/qualifications/required/
        """
        queryset = self.queryset.filter(is_required=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get qualifications grouped by category

        GET /api/certifications/qualifications/by-category/
        """
        qualifications = {}
        for category in Qualification.QualificationCategory.choices:
            category_code, category_name = category
            quals = self.queryset.filter(category=category_code)
            qualifications[category_code] = {
                'name': category_name,
                'qualifications': QualificationListSerializer(quals, many=True).data
            }
        return Response(qualifications)


class EmployeeQualificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for EmployeeQualification (employee certifications) CRUD operations

    Permissions:
    - Employees can view their own certifications
    - Managers can view and manage certifications for employees at their location
    - Admins can view and manage all certifications

    Endpoints:
    - GET /api/certifications/employee-certifications/ - List certifications (filtered by permissions)
    - GET /api/certifications/employee-certifications/{id}/ - Get certification details
    - POST /api/certifications/employee-certifications/ - Create new certification
    - PUT/PATCH /api/certifications/employee-certifications/{id}/ - Update certification
    - DELETE /api/certifications/employee-certifications/{id}/ - Delete certification
    - POST /api/certifications/employee-certifications/{id}/verify/ - Verify certification (Manager/Admin)
    - GET /api/certifications/employee-certifications/my-certifications/ - Get current user's certifications
    - GET /api/certifications/employee-certifications/expiring/ - Get expiring certifications
    - GET /api/certifications/employee-certifications/expired/ - Get expired certifications
    - GET /api/certifications/employee-certifications/pending-verification/ - Get certifications needing verification
    """
    queryset = EmployeeQualification.objects.select_related(
        'employee', 'employee__primary_location', 'qualification', 'verified_by'
    ).all().order_by('-created_at')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'qualification', 'status']
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__employee_id',
        'qualification__name', 'qualification__code'
    ]
    ordering_fields = ['issue_date', 'expiry_date', 'created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return EmployeeQualificationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeQualificationUpdateSerializer
        elif self.action in ['expiring', 'expired', 'pending_verification']:
            return ExpiringCertificationsSerializer
        return EmployeeQualificationSerializer

    def get_queryset(self):
        """
        Filter queryset based on user role:
        - Admin: sees all certifications
        - Manager: sees certifications for employees at their location
        - Employee: sees only their own certifications
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Admin sees all
        if user.is_superuser or user.is_staff:
            return queryset

        # Managers see certifications for employees at their location
        if user.role == 'MANAGER' and user.primary_location:
            return queryset.filter(employee__primary_location=user.primary_location)

        # Employees see only their own certifications
        return queryset.filter(employee=user)

    def perform_create(self, serializer):
        """
        Create certification for specified employee or current user
        Managers/Admins can create for any employee they have access to
        Employees can only create for themselves
        """
        user = self.request.user
        employee_id = self.request.data.get('employee_id')

        if employee_id:
            # Validate employee access
            try:
                employee = User.objects.get(id=employee_id, is_active=True)

                # Check if user has permission to create certification for this employee
                if user.is_superuser or user.is_staff:
                    # Admin can create for anyone
                    pass
                elif user.role == 'MANAGER' and user.primary_location:
                    # Manager can create for employees at their location
                    if employee.primary_location != user.primary_location:
                        raise PermissionError("Cannot create certification for employee at different location")
                elif employee != user:
                    # Employee can only create for themselves
                    raise PermissionError("Can only create certifications for yourself")

                serializer.save(employee=employee, created_by=user)
            except User.DoesNotExist:
                raise ValueError("Employee not found")
        else:
            # No employee specified, create for current user
            serializer.save(employee=user, created_by=user)

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'verify':
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def verify(self, request, pk=None):
        """
        Verify an employee certification
        Only managers and admins can verify certifications

        POST /api/certifications/employee-certifications/{id}/verify/
        Body: {"verify": true, "notes": "Verified certificate document"}
        """
        certification = self.get_object()
        serializer = CertificationVerifySerializer(data=request.data)

        if serializer.is_valid():
            # Verify the certification
            certification.verify(request.user)

            # Update notes if provided
            notes = serializer.validated_data.get('notes')
            if notes:
                if certification.notes:
                    certification.notes += f"\n[Verified by {request.user.get_full_name()}]: {notes}"
                else:
                    certification.notes = f"[Verified by {request.user.get_full_name()}]: {notes}"
                certification.save()

            return Response(
                {
                    'message': 'Certification verified successfully',
                    'certification': EmployeeQualificationSerializer(certification).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_certifications(self, request):
        """
        Get current user's certifications

        GET /api/certifications/employee-certifications/my-certifications/
        """
        certifications = self.queryset.filter(employee=request.user)
        serializer = self.get_serializer(certifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        """
        Get certifications expiring soon (within 90 days)

        GET /api/certifications/employee-certifications/expiring/
        Query params:
        - days: Number of days to look ahead (default: 90)
        """
        days = int(request.query_params.get('days', 90))
        threshold_date = date.today() + timedelta(days=days)

        queryset = self.get_queryset().filter(
            expiry_date__lte=threshold_date,
            expiry_date__gte=date.today(),
            status__in=['ACTIVE', 'EXPIRING_SOON']
        ).order_by('expiry_date')

        serializer = ExpiringCertificationsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """
        Get expired certifications

        GET /api/certifications/employee-certifications/expired/
        """
        queryset = self.get_queryset().filter(
            status='EXPIRED'
        ).order_by('-expiry_date')

        serializer = ExpiringCertificationsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def pending_verification(self, request):
        """
        Get certifications pending verification
        Only managers and admins can access this

        GET /api/certifications/employee-certifications/pending-verification/
        """
        queryset = self.get_queryset().filter(
            status='PENDING_VERIFICATION'
        ).order_by('-created_at')

        serializer = ExpiringCertificationsSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def compliance_report(self, request):
        """
        Get certification compliance report
        Shows summary of certification statuses

        GET /api/certifications/employee-certifications/compliance-report/
        """
        queryset = self.get_queryset()

        # Count by status
        status_counts = {}
        for status_choice in EmployeeQualification.CertificationStatus.choices:
            status_code, status_name = status_choice
            count = queryset.filter(status=status_code).count()
            status_counts[status_code] = {
                'name': status_name,
                'count': count
            }

        # Count expiring in different timeframes
        today = date.today()
        expiring_counts = {
            'critical': queryset.filter(
                expiry_date__lte=today + timedelta(days=14),
                expiry_date__gte=today
            ).count(),
            'high': queryset.filter(
                expiry_date__lte=today + timedelta(days=30),
                expiry_date__gt=today + timedelta(days=14)
            ).count(),
            'medium': queryset.filter(
                expiry_date__lte=today + timedelta(days=60),
                expiry_date__gt=today + timedelta(days=30)
            ).count(),
            'low': queryset.filter(
                expiry_date__lte=today + timedelta(days=90),
                expiry_date__gt=today + timedelta(days=60)
            ).count(),
        }

        # Count pending verification
        pending_verification_count = queryset.filter(status='PENDING_VERIFICATION').count()

        # Count expired
        expired_count = queryset.filter(status='EXPIRED').count()

        return Response({
            'total_certifications': queryset.count(),
            'status_breakdown': status_counts,
            'expiring_breakdown': expiring_counts,
            'pending_verification': pending_verification_count,
            'expired': expired_count,
            'report_date': today.isoformat()
        })
