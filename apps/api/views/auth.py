"""
Authentication API Views
"""
from rest_framework import status, serializers as rest_serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer to include user data in login response
    Allows login with either email or username
    """
    email = rest_serializers.EmailField(required=False, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username not required so we can use email instead
        self.fields['username'].required = False

    def validate(self, attrs):
        # Allow login with email or username
        email = attrs.get('email')
        username = attrs.get('username')

        from django.contrib.auth import get_user_model
        User = get_user_model()

        # If email is provided instead of username, look up the username
        if email and not username:
            try:
                user = User.objects.get(email=email)
                attrs['username'] = user.username
            except User.DoesNotExist:
                # Use generic error to prevent email enumeration
                raise rest_serializers.ValidationError({'error': 'Invalid email or password'})
        elif not username:
            raise rest_serializers.ValidationError({'error': 'Either email or username is required'})

        data = super().validate(attrs)

        # Add custom user data to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'employee_id': self.user.employee_id,
            'role': self.user.role,
            'employment_status': self.user.employment_status,
            'is_active': self.user.is_active,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
            'remaining_vacation_days': self.user.remaining_vacation_days,
            'annual_vacation_days': self.user.annual_vacation_days,
        }

        # Add primary location if exists
        if self.user.primary_location:
            data['user']['primary_location'] = {
                'id': self.user.primary_location.id,
                'name': self.user.primary_location.name,
                'city': self.user.primary_location.city,
            }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that returns JWT tokens and user data
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout by blacklisting the refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(
            {'message': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token_view(request):
    """
    Test endpoint to verify token authentication
    """
    return Response({
        'message': 'Token is valid',
        'user': {
            'id': request.user.id,
            'email': request.user.email,
            'name': f"{request.user.first_name} {request.user.last_name}",
        }
    })
