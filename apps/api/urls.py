"""
API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.api.views.auth import CustomTokenObtainPairView, logout_view, test_token_view
from apps.api.views.users import UserViewSet
from apps.api.views.locations import LocationViewSet
from apps.api.views.vacation import VacationRequestViewSet, PublicHolidayViewSet
from apps.api.views.notifications import NotificationViewSet
from apps.api.views.dashboard import dashboard_stats, health_check
from apps.api.views.certifications import QualificationViewSet, EmployeeQualificationViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'vacation/requests', VacationRequestViewSet, basename='vacation-request')
router.register(r'vacation/holidays', PublicHolidayViewSet, basename='public-holiday')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'certifications/qualifications', QualificationViewSet, basename='qualification')
router.register(r'certifications/employee-certifications', EmployeeQualificationViewSet, basename='employee-certification')

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/test/', test_token_view, name='test_token'),

    # Dashboard endpoints
    path('dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('health/', health_check, name='health_check'),

    # Router URLs (includes all viewsets)
    path('', include(router.urls)),
]
