"""
Location API ViewSet
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.locations.models import Location
from apps.api.serializers.locations import (
    LocationSerializer,
    LocationDetailSerializer,
    LocationCreateUpdateSerializer
)
from apps.api.serializers.users import UserSerializer
from apps.api.permissions import IsAdminOrManager


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Location CRUD operations

    Permissions:
    - List/Retrieve: Any authenticated user
    - Create/Update/Delete: Admin or Manager only
    """
    queryset = Location.objects.select_related('manager').filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'code', 'city', 'state']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return LocationSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return LocationCreateUpdateSerializer
        return LocationDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrManager()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """
        Get all employees at this location

        GET /api/locations/{id}/employees/
        """
        location = self.get_object()

        # Get employees where this is their primary location
        employees = location.primary_employees.filter(is_active=True).select_related(
            'primary_location', 'supervisor'
        ).prefetch_related(
            'qualifications'
        )

        # Apply search if provided
        search = request.query_params.get('search', None)
        if search:
            employees = employees.filter(
                first_name__icontains=search
            ) | employees.filter(
                last_name__icontains=search
            ) | employees.filter(
                employee_id__icontains=search
            )

        serializer = UserSerializer(employees, many=True)
        return Response({
            'location': LocationSerializer(location).data,
            'employee_count': employees.count(),
            'employees': serializer.data
        })

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        Get location statistics

        GET /api/locations/{id}/stats/
        """
        location = self.get_object()
        employees = location.primary_employees.filter(is_active=True)

        return Response({
            'location_id': location.id,
            'location_name': location.name,
            'total_employees': employees.count(),
            'active_employees': employees.filter(employment_status='ACTIVE').count(),
            'on_leave_employees': employees.filter(employment_status='ON_LEAVE').count(),
            'roles': {
                'managers': employees.filter(role='MANAGER').count(),
                'employees': employees.filter(role='EMPLOYEE').count(),
            },
        })
