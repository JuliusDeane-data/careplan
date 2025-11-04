"""
Dashboard API Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.locations.models import Location
from apps.vacation.models import VacationRequest

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics based on user role

    GET /api/dashboard/stats/
    """
    user = request.user
    stats = {}

    # Base stats for everyone
    stats['user'] = {
        'id': user.id,
        'name': f"{user.first_name} {user.last_name}",
        'role': user.role,
        'vacation_balance': user.remaining_vacation_days,
        'annual_vacation_days': user.annual_vacation_days,
    }

    # Admin and Manager stats
    if user.is_superuser or user.is_staff or user.role == 'MANAGER':
        # Employee statistics
        if user.is_superuser or user.is_staff:
            # Admin sees all
            employees = User.objects.filter(is_active=True)
            locations = Location.objects.filter(is_active=True)
            vacation_requests = VacationRequest.objects.all()
        else:
            # Manager sees their location only
            employees = User.objects.filter(
                is_active=True,
                primary_location=user.primary_location
            )
            locations = Location.objects.filter(
                id=user.primary_location.id
            ) if user.primary_location else Location.objects.none()
            vacation_requests = VacationRequest.objects.filter(
                employee__primary_location=user.primary_location
            )

        stats['employees'] = {
            'total': employees.count(),
            'active': employees.filter(employment_status='ACTIVE').count(),
            'on_leave': employees.filter(employment_status='ON_LEAVE').count(),
            'terminated': employees.filter(employment_status='TERMINATED').count(),
        }

        stats['locations'] = {
            'total': locations.count(),
            'active': locations.count(),
        }

        stats['vacation_requests'] = {
            'pending': vacation_requests.filter(status='PENDING').count(),
            'approved': vacation_requests.filter(status='APPROVED').count(),
            'denied': vacation_requests.filter(status='DENIED').count(),
            'cancelled': vacation_requests.filter(status='CANCELLED').count(),
            'total': vacation_requests.count(),
        }

    # Employee-specific stats
    my_requests = VacationRequest.objects.filter(employee=user)
    stats['my_vacation_requests'] = {
        'pending': my_requests.filter(status='PENDING').count(),
        'approved': my_requests.filter(status='APPROVED').count(),
        'denied': my_requests.filter(status='DENIED').count(),
        'total': my_requests.count(),
    }

    # Upcoming approved vacations for the user
    from django.utils import timezone
    upcoming_vacations = my_requests.filter(
        status='APPROVED',
        start_date__gte=timezone.now().date()
    ).order_by('start_date')[:3]

    stats['upcoming_vacations'] = [
        {
            'id': vac.id,
            'start_date': vac.start_date,
            'end_date': vac.end_date,
            'vacation_days': vac.vacation_days,
            'days_until_start': vac.days_until_start(),
        }
        for vac in upcoming_vacations
    ]

    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """
    Simple health check endpoint

    GET /api/health/
    """
    return Response({
        'status': 'ok',
        'message': 'API is running',
        'user': request.user.email if request.user.is_authenticated else None,
    })
