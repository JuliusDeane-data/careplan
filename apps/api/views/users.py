"""
User API ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.api.serializers.users import (
    UserSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    UserCreateSerializer,
    PasswordChangeSerializer
)
from apps.api.permissions import IsAdminOrManager, IsOwnerOrAdminOrManager

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations

    Permissions:
    - List/Create: Admin or Manager
    - Retrieve/Update/Delete: Owner, Admin, or Manager
    """
    queryset = User.objects.select_related(
        'primary_location', 'supervisor'
    ).prefetch_related(
        'additional_locations', 'qualifications'
    ).filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'employment_status', 'primary_location']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['date_joined', 'first_name', 'last_name', 'hire_date']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return UserSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'create']:
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated(), IsOwnerOrAdminOrManager()]

    def get_queryset(self):
        """
        Filter queryset based on user role:
        - Admin: sees all users
        - Manager: sees users at their location
        - Employee: sees only themselves
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Admin sees all users
        if user.is_superuser or user.is_staff:
            return queryset

        # Managers see users at their location
        if user.role == 'MANAGER' and user.primary_location:
            return queryset.filter(primary_location=user.primary_location)

        # Employees see only themselves
        return queryset.filter(id=user.id)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Get or update current user profile

        GET /api/users/me/ - Get current user
        PUT /api/users/me/ - Update current user
        PATCH /api/users/me/ - Partial update current user
        """
        if request.method == 'GET':
            serializer = UserDetailSerializer(request.user)
            return Response(serializer.data)
        else:
            serializer = UserUpdateSerializer(
                request.user,
                data=request.data,
                partial=(request.method == 'PATCH')
            )
            if serializer.is_valid():
                serializer.save()
                return Response(UserDetailSerializer(request.user).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change current user's password

        POST /api/users/change-password/
        Body: {"old_password": "...", "new_password": "..."}
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def vacation_balance(self, request, pk=None):
        """
        Get user's vacation balance

        GET /api/users/{id}/vacation-balance/
        """
        user = self.get_object()
        return Response({
            'user_id': user.id,
            'employee_id': user.employee_id,
            'name': f"{user.first_name} {user.last_name}",
            'annual_vacation_days': user.annual_vacation_days,
            'remaining_vacation_days': user.remaining_vacation_days,
            'used_vacation_days': user.annual_vacation_days - user.remaining_vacation_days,
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def terminate(self, request, pk=None):
        """
        Terminate an employee

        POST /api/users/{id}/terminate/
        Body: {"termination_date": "2025-12-31"}
        """
        user = self.get_object()
        termination_date = request.data.get('termination_date')

        if not termination_date:
            return Response(
                {'error': 'termination_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.employment_status = 'TERMINATED'
        user.termination_date = termination_date
        user.is_active = False
        user.save()

        return Response(
            {
                'message': 'Employee terminated successfully',
                'user': UserDetailSerializer(user).data
            },
            status=status.HTTP_200_OK
        )
