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
def dashboard_activities(request):
    """
    Get recent activity feed

    GET /api/dashboard/activities/
    Query params:
    - limit: number of activities to return (default: 10)
    - offset: pagination offset (default: 0)
    """
    from django.utils import timezone
    from datetime import timedelta

    limit = int(request.query_params.get('limit', 10))
    offset = int(request.query_params.get('offset', 0))
    user = request.user

    # Get recent vacation requests relevant to the user
    activities = []

    # For managers/admins, show team activities
    if user.role in ['MANAGER', 'ADMIN']:
        if user.role == 'ADMIN':
            recent_requests = VacationRequest.objects.all()
        else:
            recent_requests = VacationRequest.objects.filter(
                employee__primary_location=user.primary_location
            )
    else:
        # For employees, show only their own requests
        recent_requests = VacationRequest.objects.filter(employee=user)

    # Get recent requests (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_requests = recent_requests.filter(
        created_at__gte=thirty_days_ago
    ).order_by('-created_at')

    for req in recent_requests:
        # Map status to activity type (must match frontend ActivityType)
        if req.status == 'PENDING':
            activity_type = 'vacation_requested'
        elif req.status == 'APPROVED':
            activity_type = 'vacation_approved'
        elif req.status == 'DENIED':
            activity_type = 'vacation_denied'
        elif req.status == 'CANCELLED':
            activity_type = 'vacation_cancelled'
        else:
            activity_type = 'vacation_requested'

        activities.append({
            'id': req.id,
            'type': activity_type,
            'title': f"Vacation request {req.status.lower()}",
            'description': f"{req.employee.first_name} {req.employee.last_name} - {req.start_date} to {req.end_date}",
            'timestamp': req.created_at.isoformat(),
            'is_read': False,  # Default to unread, could track this in future
            'actor': {
                'id': req.employee.id,
                'name': f"{req.employee.first_name} {req.employee.last_name}",
            },
            'target': {
                'type': 'vacation',
                'id': req.id,
                'name': f"Vacation Request #{req.id}"
            },
            'metadata': {
                'vacation_days': req.vacation_days,
                'status': req.status,
                'start_date': req.start_date.isoformat(),
                'end_date': req.end_date.isoformat(),
            }
        })

    # Pagination
    total_count = len(activities)
    activities_page = activities[offset:offset + limit]

    return Response({
        'count': total_count,
        'next': f"/api/dashboard/activities/?limit={limit}&offset={offset + limit}" if offset + limit < total_count else None,
        'previous': f"/api/dashboard/activities/?limit={limit}&offset={max(0, offset - limit)}" if offset > 0 else None,
        'results': activities_page
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_upcoming_events(request):
    """
    Get upcoming events (vacations and holidays)

    GET /api/dashboard/upcoming-events/
    Query params:
    - days: number of days to look ahead (default: 30)
    """
    from django.utils import timezone
    from datetime import timedelta
    from apps.vacation.models import PublicHoliday

    days = int(request.query_params.get('days', 30))
    user = request.user
    today = timezone.now().date()
    end_date = today + timedelta(days=days)

    events = []

    # Get upcoming approved vacations
    if user.role in ['MANAGER', 'ADMIN']:
        if user.role == 'ADMIN':
            vacation_requests = VacationRequest.objects.filter(
                status='APPROVED',
                start_date__lte=end_date,
                end_date__gte=today
            )
        else:
            vacation_requests = VacationRequest.objects.filter(
                status='APPROVED',
                employee__primary_location=user.primary_location,
                start_date__lte=end_date,
                end_date__gte=today
            )
    else:
        vacation_requests = VacationRequest.objects.filter(
            status='APPROVED',
            employee=user,
            start_date__lte=end_date,
            end_date__gte=today
        )

    for req in vacation_requests:
        events.append({
            'id': req.id,  # Use integer ID, not string
            'type': 'vacation',
            'title': f"{req.employee.first_name} {req.employee.last_name}'s Vacation",
            'start_date': req.start_date.isoformat(),
            'end_date': req.end_date.isoformat(),
            'all_day': True,  # Vacations are typically all-day events
            'status': 'approved',  # These are all approved vacations
            'employee': {
                'id': req.employee.id,
                'name': f"{req.employee.first_name} {req.employee.last_name}",
            },
            'location': req.employee.primary_location.name if req.employee.primary_location else None,
        })

    # Get upcoming public holidays (PublicHoliday uses is_deleted, not is_active)
    holidays = PublicHoliday.objects.filter(
        date__gte=today,
        date__lte=end_date
    )

    for holiday in holidays:
        events.append({
            'id': holiday.id,  # Use integer ID
            'type': 'holiday',
            'title': holiday.name,
            'start_date': holiday.date.isoformat(),
            'end_date': holiday.date.isoformat(),
            'all_day': True,  # Holidays are all-day events
            'status': 'confirmed',  # Holidays are always confirmed
            'employee': None,
            'location': None if holiday.is_nationwide else (holiday.location.name if holiday.location else None),
        })

    # Sort by start date
    events.sort(key=lambda x: x['start_date'])

    return Response(events)


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
