"""
Vacation API ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from apps.vacation.models import VacationRequest, PublicHoliday
from apps.api.serializers.vacation import (
    VacationRequestSerializer,
    VacationRequestDetailSerializer,
    VacationRequestCreateSerializer,
    VacationRequestUpdateSerializer,
    PublicHolidaySerializer
)
from apps.api.permissions import IsOwnerOrAdminOrManager, IsAdminOrManager


class VacationRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Vacation Request CRUD operations

    Permissions:
    - List/Create: Any authenticated user
    - Retrieve/Update/Delete: Owner, Admin, or Manager
    - Approve/Deny: Admin or Manager only
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'request_type', 'employee']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering_fields = ['start_date', 'created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return VacationRequestSerializer
        elif self.action == 'create':
            return VacationRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VacationRequestUpdateSerializer
        return VacationRequestDetailSerializer

    def get_queryset(self):
        """
        Filter queryset based on user role:
        - Admin: sees all requests
        - Manager: sees requests from their location
        - Employee: sees only their own requests
        """
        user = self.request.user
        queryset = VacationRequest.objects.select_related(
            'employee', 'approved_by', 'denied_by', 'cancelled_by'
        )

        # Admin sees all requests
        if user.is_superuser or user.is_staff:
            return queryset

        # Managers see requests from their location
        if user.role == 'MANAGER' and user.primary_location:
            return queryset.filter(employee__primary_location=user.primary_location)

        # Employees see only their own requests
        return queryset.filter(employee=user)

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['approve', 'deny']:
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated(), IsOwnerOrAdminOrManager()]

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """
        Get current user's vacation requests

        GET /api/vacation/requests/my-requests/
        """
        queryset = VacationRequest.objects.filter(
            employee=request.user
        ).select_related(
            'approved_by', 'denied_by', 'cancelled_by'
        ).order_by('-created_at')

        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        serializer = VacationRequestSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a vacation request

        POST /api/vacation/requests/{id}/approve/
        """
        vacation_request = self.get_object()

        # Security: Check employee cannot approve their own request
        if vacation_request.employee == request.user:
            return Response(
                {'error': 'You cannot approve your own vacation request'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Security: Manager can only approve requests from their location
        if request.user.role == 'MANAGER' and not request.user.is_superuser:
            if vacation_request.employee.primary_location != request.user.primary_location:
                return Response(
                    {'error': 'You can only approve requests from employees at your location'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Check if already approved/denied/cancelled
        if vacation_request.status != 'PENDING':
            return Response(
                {'error': f'Cannot approve request with status: {vacation_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vacation_request.approve(approved_by=request.user)
            serializer = VacationRequestDetailSerializer(vacation_request)
            return Response({
                'message': 'Vacation request approved successfully',
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """
        Deny a vacation request

        POST /api/vacation/requests/{id}/deny/
        Body: {"reason": "Not enough coverage during this period"}
        """
        vacation_request = self.get_object()
        reason = request.data.get('reason', '')

        if not reason:
            return Response(
                {'error': 'Denial reason is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Security: Check employee cannot deny their own request
        if vacation_request.employee == request.user:
            return Response(
                {'error': 'You cannot deny your own vacation request'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Security: Manager can only deny requests from their location
        if request.user.role == 'MANAGER' and not request.user.is_superuser:
            if vacation_request.employee.primary_location != request.user.primary_location:
                return Response(
                    {'error': 'You can only deny requests from employees at your location'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Check if already approved/denied/cancelled
        if vacation_request.status != 'PENDING':
            return Response(
                {'error': f'Cannot deny request with status: {vacation_request.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vacation_request.deny(denied_by=request.user, reason=reason)
            serializer = VacationRequestDetailSerializer(vacation_request)
            return Response({
                'message': 'Vacation request denied',
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a vacation request (only by the employee who created it)

        POST /api/vacation/requests/{id}/cancel/
        Body: {"reason": "Plans changed"}
        """
        vacation_request = self.get_object()
        reason = request.data.get('reason', '')

        # Only employee can cancel their own request
        if vacation_request.employee != request.user:
            return Response(
                {'error': 'You can only cancel your own vacation requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if cancellable
        if not vacation_request.is_cancellable():
            return Response(
                {'error': 'This vacation request cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            vacation_request.cancel(cancelled_by=request.user, reason=reason)
            serializer = VacationRequestDetailSerializer(vacation_request)
            return Response({
                'message': 'Vacation request cancelled',
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """
        Get vacation calendar for team (approved vacations only)

        GET /api/vacation/requests/calendar/
        Query params:
            - start_date: Filter from this date
            - end_date: Filter until this date
            - location: Filter by location ID
        """
        # Start with approved vacations that the user can see
        queryset = self.get_queryset().filter(status='APPROVED')

        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(end_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)

        # Filter by location if provided
        location_id = request.query_params.get('location')
        if location_id:
            queryset = queryset.filter(employee__primary_location_id=location_id)

        serializer = VacationRequestSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'vacations': serializer.data
        })

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """
        Get current user's vacation balance

        GET /api/vacation/requests/balance/
        """
        user = request.user
        pending_requests = VacationRequest.objects.filter(
            employee=user,
            status='PENDING'
        )
        pending_days = sum(req.vacation_days for req in pending_requests)

        return Response({
            'user_id': user.id,
            'employee_id': user.employee_id,
            'name': f"{user.first_name} {user.last_name}",
            'annual_vacation_days': user.annual_vacation_days,
            'remaining_vacation_days': user.remaining_vacation_days,
            'used_vacation_days': user.annual_vacation_days - user.remaining_vacation_days,
            'pending_days': pending_days,
            'available_days': user.remaining_vacation_days - pending_days,
        })

    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """
        Get pending vacation requests that need approval (for managers)

        GET /api/vacation/requests/pending-approvals/
        """
        # Only managers and admins can see pending approvals
        if not (request.user.is_superuser or request.user.is_staff or request.user.role == 'MANAGER'):
            return Response(
                {'error': 'Only managers can view pending approvals'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset().filter(status='PENDING').order_by('created_at')
        serializer = VacationRequestSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'requests': serializer.data
        })


class PublicHolidayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Public Holidays (read-only for most users)

    Permissions:
    - List/Retrieve: Any authenticated user
    - Create/Update/Delete: Admin only (via Django admin)
    """
    queryset = PublicHoliday.objects.filter(is_deleted=False)
    serializer_class = PublicHolidaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['location', 'is_nationwide', 'is_recurring']
    ordering = ['date']

    def get_queryset(self):
        """Filter holidays by year and location if provided"""
        queryset = super().get_queryset()

        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(date__year=year)

        # Filter by location (or nationwide)
        location_id = self.request.query_params.get('location')
        if location_id:
            queryset = queryset.filter(
                Q(location_id=location_id) | Q(is_nationwide=True)
            )

        return queryset
