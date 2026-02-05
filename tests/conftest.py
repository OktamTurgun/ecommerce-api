"""
Pytest configuration and shared fixtures.

This file contains fixtures that are available to all tests.
Fixtures are reusable test utilities that help set up test data.
"""
import pytest
from django.conf import settings
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Session-wide database setup.
    Runs migrations once for all tests.
    """
    with django_db_blocker.unblock():
        call_command('migrate', '--noinput')


@pytest.fixture
def api_client():
    """
    Provides a Django REST Framework API client for testing.
    
    Usage in tests:
        def test_something(api_client):
            response = api_client.get('/api/users/')
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Provides an authenticated API client with JWT token.
    
    Usage in tests:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get('/api/users/profile/')
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    # Generate JWT token for user
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return api_client


@pytest.fixture
def user(db):
    """
    Creates a basic test user.
    
    Usage in tests:
        def test_user_creation(user):
            assert user.email == 'testuser@example.com'
    """
    from tests.factories import UserFactory
    return UserFactory()


@pytest.fixture
def verified_user(db):
    """
    Creates a verified test user (email confirmed).
    
    Usage in tests:
        def test_login(verified_user):
            # User can login because email is verified
    """
    from tests.factories import UserFactory
    return UserFactory(is_active=True, email_verified=True)


@pytest.fixture
def admin_user(db):
    """
    Creates an admin/staff user.
    
    Usage in tests:
        def test_admin_access(admin_user):
            assert admin_user.is_staff == True
    """
    from tests.factories import UserFactory
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def user_password():
    """
    Returns the default password used in factories.
    Useful for login tests.
    
    Usage:
        def test_login(user, user_password):
            data = {'email': user.email, 'password': user_password}
    """
    return 'TestPass123!'


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    You can override this with @pytest.mark.django_db when needed.
    """
    pass


@pytest.fixture
def mock_send_email(mocker):
    """
    Mock email sending to avoid sending real emails in tests.
    
    This mocks Django's core send_mail function that is imported
    in email_service.py
    
    Usage:
        def test_registration(api_client, mock_send_email):
            response = api_client.post('/api/users/register/', data)
            mock_send_email.assert_called_once()
    """
    # Mock the verification function used in verification_service
    return mocker.patch('apps.users.services.verification_service.send_verification_code_email')