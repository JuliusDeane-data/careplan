# Backend API Implementation Plan

**Date**: 2025-11-04
**Status**: Ready to Execute
**Priority**: HIGH - Required before frontend can function
**Estimated Time**: 6-8 hours

---

## 🎯 Overview

Before the React frontend can work, we need to implement REST API endpoints using Django REST Framework. The backend infrastructure is already in place (DRF, JWT, CORS configured), but we need to create serializers, viewsets, and API URLs.

---

## 📋 What We Already Have ✅

- ✅ Django models (User, Location, Vacation, Notifications, etc.)
- ✅ DRF installed and configured
- ✅ JWT authentication configured (Simple JWT)
- ✅ CORS enabled for frontend (localhost:3000)
- ✅ Pagination, filtering, throttling configured
- ✅ Admin interface working

---

## 🚀 What We Need to Build

### 1. Authentication API
- Login endpoint (get JWT tokens)
- Token refresh endpoint
- Logout endpoint
- Password reset endpoints

### 2. Users API
- Get current user profile
- Update profile
- Change password
- List users (admin/manager only)
- User vacation balance

### 3. Locations API
- List locations
- Location detail
- Employees at location

### 4. Vacation API
- List vacation requests
- Create vacation request
- Approve/deny/cancel vacation
- Vacation calendar
- User's vacation balance

### 5. Notifications API
- List notifications
- Unread notifications
- Mark as read
- Delete notification

---

## 📁 API Structure

```
/api/
├── auth/
│   ├── login/              POST - Get JWT tokens
│   ├── refresh/            POST - Refresh access token
│   ├── logout/             POST - Blacklist token
│   └── password-reset/     POST - Request password reset
│
├── users/
│   ├── /                   GET - List users (filtered by role)
│   ├── /me/                GET, PUT - Current user profile
│   ├── /me/change-password/ POST - Change password
│   ├── /{id}/              GET - User detail
│   ├── /{id}/vacation-balance/ GET - Vacation balance
│   └── /{id}/documents/    GET - Employee documents
│
├── locations/
│   ├── /                   GET - List locations
│   ├── /{id}/              GET - Location detail
│   └── /{id}/employees/    GET - Employees at location
│
├── vacation/
│   ├── requests/           GET, POST - List/create requests
│   ├── requests/{id}/      GET, PUT, DELETE - Request detail
│   ├── requests/{id}/approve/ POST - Approve request
│   ├── requests/{id}/deny/ POST - Deny request
│   ├── requests/{id}/cancel/ POST - Cancel request
│   ├── my-requests/        GET - Current user's requests
│   ├── calendar/           GET - Team vacation calendar
│   └── balance/            GET - Current user's balance
│
├── notifications/
│   ├── /                   GET - List notifications
│   ├── unread/             GET - Unread notifications
│   ├── /{id}/mark-read/    POST - Mark as read
│   └── /mark-all-read/     POST - Mark all as read
│
├── holidays/
│   └── /                   GET - Public holidays (filtered)
│
└── dashboard/
    └── stats/              GET - Dashboard statistics
```

---

## 📝 Implementation Steps

### Phase 1: Core Setup & Authentication (1.5 hours)

#### Step 1.1: Create API app structure
```bash
mkdir -p apps/api
cd apps/api
touch __init__.py views.py serializers.py permissions.py urls.py
```

#### Step 1.2: Create authentication endpoints
- JWT login view (extends Simple JWT)
- Token refresh (already provided by Simple JWT)
- Logout view with token blacklist
- Password reset views

#### Step 1.3: Create custom permissions
- IsOwner - User can only access their own resources
- IsAdminOrManager - Admin or manager role required
- IsOwnerOrAdminOrManager - Owner, admin, or manager

---

### Phase 2: Users API (1.5 hours)

#### Step 2.1: Create User Serializers
- UserSerializer (basic info)
- UserDetailSerializer (full info)
- UserCreateSerializer (for creating users)
- UserUpdateSerializer (for updating profile)
- PasswordChangeSerializer

#### Step 2.2: Create User ViewSet
- List users (filtered by role)
- Get current user (me/)
- Update profile
- Change password
- Vacation balance endpoint

---

### Phase 3: Locations API (1 hour)

#### Step 3.1: Create Location Serializers
- LocationSerializer (basic info)
- LocationDetailSerializer (with employees)

#### Step 3.2: Create Location ViewSet
- List locations
- Location detail
- Employees at location (custom action)

---

### Phase 4: Vacation API (2 hours)

#### Step 4.1: Create Vacation Serializers
- VacationRequestSerializer
- VacationRequestCreateSerializer (with validation)
- VacationRequestDetailSerializer

#### Step 4.2: Create Vacation ViewSet
- List requests (filtered by user role)
- Create request
- Approve/deny/cancel actions
- My requests endpoint
- Calendar endpoint
- Balance endpoint

---

### Phase 5: Notifications API (1 hour)

#### Step 5.1: Create Notification Serializers
- NotificationSerializer
- NotificationListSerializer

#### Step 5.2: Create Notification ViewSet
- List notifications
- Unread notifications
- Mark as read
- Mark all as read

---

### Phase 6: Dashboard & Miscellaneous (1 hour)

#### Step 6.1: Dashboard API
- Statistics endpoint (employee count, locations, pending requests)

#### Step 6.2: Public Holidays API
- List holidays (filtered by location/year)

---

## 🔧 Detailed Implementation

### 1. Authentication API

**File: `apps/api/views/auth.py`**

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user data"""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user data
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
        }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Logout by blacklisting the refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
```

---

### 2. Users API

**File: `apps/api/serializers/users.py`**

```python
from rest_framework import serializers
from apps.accounts.models import User
from apps.locations.models import Location
from apps.employees.models import Qualification


class LocationBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'code']


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = ['id', 'name', 'code', 'description']


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    primary_location = LocationBasicSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'employee_id',
            'role', 'employment_status', 'is_active', 'primary_location',
            'remaining_vacation_days', 'total_vacation_days'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer"""
    primary_location = LocationBasicSerializer(read_only=True)
    additional_locations = LocationBasicSerializer(many=True, read_only=True)
    qualifications = QualificationSerializer(many=True, read_only=True)
    supervisor = UserSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'employee_id',
            'phone_number', 'date_of_birth', 'address', 'city', 'state',
            'postal_code', 'emergency_contact_name', 'emergency_contact_phone',
            'hire_date', 'termination_date', 'employment_status', 'role',
            'primary_location', 'additional_locations', 'qualifications',
            'supervisor', 'remaining_vacation_days', 'total_vacation_days',
            'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at'
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user profile"""
    primary_location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.filter(is_active=True),
        required=False
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'address', 'city', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone',
            'primary_location'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value
```

**File: `apps/api/views/users.py`**

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.api.serializers.users import (
    UserSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from apps.api.permissions import IsOwnerOrAdminOrManager

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User API ViewSet"""
    queryset = User.objects.select_related('primary_location', 'supervisor').prefetch_related('additional_locations', 'qualifications')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        queryset = super().get_queryset()

        # Admin sees all users
        if user.is_superuser or user.is_staff:
            return queryset

        # Managers see users at their location
        if user.role == 'MANAGER':
            return queryset.filter(primary_location=user.primary_location)

        # Employees see only themselves
        return queryset.filter(id=user.id)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserDetailSerializer(request.user)
            return Response(serializer.data)
        else:
            serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def vacation_balance(self, request, pk=None):
        """Get user's vacation balance"""
        user = self.get_object()
        return Response({
            'total_vacation_days': user.total_vacation_days,
            'remaining_vacation_days': user.remaining_vacation_days,
            'used_vacation_days': user.total_vacation_days - user.remaining_vacation_days
        })
```

---

### 3. Vacation API

**File: `apps/api/serializers/vacation.py`**

```python
from rest_framework import serializers
from apps.vacation.models import VacationRequest
from apps.api.serializers.users import UserSerializer


class VacationRequestSerializer(serializers.ModelSerializer):
    """Basic vacation request serializer"""
    employee = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = VacationRequest
        fields = [
            'id', 'employee', 'start_date', 'end_date', 'vacation_days',
            'total_days', 'request_type', 'status', 'reason',
            'approved_by', 'approved_at', 'created_at'
        ]
        read_only_fields = ['vacation_days', 'total_days', 'status', 'approved_by', 'approved_at']


class VacationRequestCreateSerializer(serializers.ModelSerializer):
    """Create vacation request with validation"""

    class Meta:
        model = VacationRequest
        fields = ['start_date', 'end_date', 'request_type', 'reason', 'supporting_document']

    def validate(self, attrs):
        """Run model's clean() validation"""
        instance = VacationRequest(**attrs)
        instance.employee = self.context['request'].user
        instance.clean()  # This runs all validation rules
        return attrs

    def create(self, validated_data):
        validated_data['employee'] = self.context['request'].user
        return super().create(validated_data)
```

**File: `apps/api/views/vacation.py`**

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from apps.vacation.models import VacationRequest
from apps.api.serializers.vacation import VacationRequestSerializer, VacationRequestCreateSerializer


class VacationRequestViewSet(viewsets.ModelViewSet):
    """Vacation Request API ViewSet"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VacationRequestCreateSerializer
        return VacationRequestSerializer

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        queryset = VacationRequest.objects.select_related('employee', 'approved_by')

        # Admin sees all requests
        if user.is_superuser or user.is_staff:
            return queryset

        # Managers see requests from their location
        if user.role == 'MANAGER':
            return queryset.filter(employee__primary_location=user.primary_location)

        # Employees see only their own requests
        return queryset.filter(employee=user)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's vacation requests"""
        queryset = VacationRequest.objects.filter(employee=request.user).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve vacation request"""
        vacation_request = self.get_object()

        # Check permission
        if not (request.user.is_superuser or request.user.role == 'MANAGER'):
            return Response(
                {'error': 'Only managers can approve requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            vacation_request.approve(approved_by=request.user)
            serializer = self.get_serializer(vacation_request)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        """Deny vacation request"""
        vacation_request = self.get_object()
        reason = request.data.get('reason', '')

        # Check permission
        if not (request.user.is_superuser or request.user.role == 'MANAGER'):
            return Response(
                {'error': 'Only managers can deny requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            vacation_request.deny(denied_by=request.user, reason=reason)
            serializer = self.get_serializer(vacation_request)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel vacation request"""
        vacation_request = self.get_object()
        reason = request.data.get('reason', '')

        # Only employee can cancel their own request
        if vacation_request.employee != request.user:
            return Response(
                {'error': 'You can only cancel your own requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            vacation_request.cancel(cancelled_by=request.user, reason=reason)
            serializer = self.get_serializer(vacation_request)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """Get vacation calendar for team"""
        # Get approved vacations
        queryset = self.get_queryset().filter(status='APPROVED')

        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(end_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def balance(self, request):
        """Get current user's vacation balance"""
        user = request.user
        return Response({
            'total_vacation_days': user.total_vacation_days,
            'remaining_vacation_days': user.remaining_vacation_days,
            'used_vacation_days': user.total_vacation_days - user.remaining_vacation_days
        })
```

---

### 4. Main API URLs

**File: `apps/api/urls.py`**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.api.views.auth import CustomTokenObtainPairView, logout_view
from apps.api.views.users import UserViewSet
from apps.api.views.vacation import VacationRequestViewSet
# Import other viewsets...

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'vacation/requests', VacationRequestViewSet, basename='vacation-request')
# Register other viewsets...

urlpatterns = [
    # Authentication
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_view, name='logout'),

    # Router URLs
    path('', include(router.urls)),
]
```

**Update `config/urls.py`**:
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

---

## ✅ Implementation Checklist

### Phase 1: Core Setup ✓
- [ ] Create API app structure
- [ ] Create custom permissions
- [ ] Implement login endpoint
- [ ] Implement logout endpoint
- [ ] Test authentication flow

### Phase 2: Users API ✓
- [ ] Create user serializers
- [ ] Create user viewset
- [ ] Implement `/users/me/` endpoint
- [ ] Implement password change
- [ ] Test all user endpoints

### Phase 3: Locations API ✓
- [ ] Create location serializers
- [ ] Create location viewset
- [ ] Test location endpoints

### Phase 4: Vacation API ✓
- [ ] Create vacation serializers
- [ ] Create vacation viewset
- [ ] Implement approve/deny/cancel
- [ ] Implement calendar endpoint
- [ ] Test all vacation endpoints

### Phase 5: Notifications API ✓
- [ ] Create notification serializers
- [ ] Create notification viewset
- [ ] Test notification endpoints

### Phase 6: Dashboard API ✓
- [ ] Create dashboard stats endpoint
- [ ] Create holidays endpoint
- [ ] Test misc endpoints

---

## 🧪 Testing the API

**Using curl**:
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Get current user (use token from login)
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Create vacation request
curl -X POST http://localhost:8000/api/vacation/requests/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_date":"2025-12-20","end_date":"2025-12-27","request_type":"ANNUAL_LEAVE","reason":"Christmas vacation"}'
```

**Or use Django REST Framework's browsable API**:
- Visit http://localhost:8000/api/ in your browser
- Login with your admin credentials
- Browse and test endpoints interactively

---

## 📚 Documentation

Add API documentation using drf-spectacular:

```bash
pip install drf-spectacular
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]
```

Add to `REST_FRAMEWORK` settings:
```python
REST_FRAMEWORK = {
    # ...
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

Add URLs:
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

Access Swagger UI at: http://localhost:8000/api/docs/

---

## 🎯 Next Steps

After backend API is complete:
1. **Test all endpoints** with Postman or curl
2. **Create test users** in Django admin
3. **Start React frontend** implementation
4. **Connect frontend to API**

---

**Ready to implement? Let's start with Phase 1!** 🚀
