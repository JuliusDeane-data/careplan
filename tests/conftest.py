"""
Pytest configuration and shared fixtures for Careplan tests.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user_password():
    """Return a default password for test users."""
    return 'testpass123'


@pytest.fixture
def create_user(db, user_password):
    """Factory fixture for creating users."""
    _counter = {'value': 0}
    
    def make_user(**kwargs):
        if 'password' not in kwargs:
            kwargs['password'] = user_password
        if 'email' not in kwargs:
            kwargs['email'] = f"user{User.objects.count() + 1}@example.com"
        if 'employee_id' not in kwargs:
            # Auto-generate unique employee_id if not provided
            # Use a counter to ensure uniqueness even in concurrent scenarios
            _counter['value'] += 1
            kwargs['employee_id'] = f"EMP{_counter['value']:03d}"

        password = kwargs.pop('password')
        user = User(**kwargs)
        user.set_password(password)
        user.save()
        return user

    return make_user


@pytest.fixture
def admin_user(create_user):
    """Create an admin user."""
    return create_user(
        username='admin',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user(username='testuser')
    api_client.force_authenticate(user=user)
    return api_client, user
