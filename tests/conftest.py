"""
Pytest configuration and shared fixtures.

This file contains fixtures that are available to all tests.
Fixtures are reusable test utilities that help set up test data.
"""
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

# Import factories for easy access in tests
from tests.factories import (
    UserFactory,
    AdminUserFactory,
    UserConfirmationFactory,
    create_user_with_verification,
    create_authenticated_client,
)


# ============================================================================
# DATABASE & SESSION FIXTURES
# ============================================================================

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Session-wide database setup.
    Runs migrations once for all tests.
    """
    with django_db_blocker.unblock():
        call_command('migrate', '--noinput')


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    You can override this with @pytest.mark.django_db when needed.
    """
    pass


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def api_client():
    """
    Provides a Django REST Framework API client for testing.
    
    Usage:
        def test_something(api_client):
            response = api_client.get('/api/users/')
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, verified_user):
    """
    Provides an authenticated API client with JWT token.
    Uses verified_user fixture to ensure user can login.
    
    Usage:
        def test_protected_endpoint(authenticated_client):
            response = authenticated_client.get('/api/users/profile/')
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(verified_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    Provides an authenticated API client for admin user.
    
    Usage:
        def test_admin_endpoint(admin_client):
            response = admin_client.get('/api/admin/dashboard/')
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return api_client


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def user(db):
    """
    Creates a basic test user (is_active=True, but not verified).
    
    Usage:
        def test_user_creation(user):
            assert user.email == 'user0@example.com'
    """
    return UserFactory()


@pytest.fixture
def verified_user(db):
    """
    Creates a verified test user (is_active=True).
    This user can login immediately without email verification.
    
    Usage:
        def test_login(verified_user, user_password):
            data = {'email': verified_user.email, 'password': user_password}
    """
    return UserFactory(is_active=True)


@pytest.fixture
def admin_user(db):
    """
    Creates an admin/staff user.
    
    Usage:
        def test_admin_access(admin_user):
            assert admin_user.is_staff == True
    """
    return AdminUserFactory()


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


@pytest.fixture
def unverified_user(db):
    """
    Creates an inactive user (is_active=False).
    Useful for testing email verification flows.
    
    Usage:
        def test_verification_required(unverified_user):
            assert unverified_user.is_active == False
    """
    return UserFactory(is_active=False)


# ============================================================================
# CONFIRMATION FIXTURES
# ============================================================================

@pytest.fixture
def email_confirmation(db, user):
    """
    Creates an email verification confirmation code for user.
    
    Usage:
        def test_email_verification(email_confirmation):
            # email_confirmation.code contains the verification code
            pass
    """
    return UserConfirmationFactory(
        user=user,
        confirmation_type='email_verification'
    )


@pytest.fixture
def password_reset_confirmation(db, user):
    """
    Creates a password reset confirmation code for user.
    
    Usage:
        def test_password_reset(password_reset_confirmation):
            # password_reset_confirmation.code contains the reset code
            pass
    """
    return UserConfirmationFactory(
        user=user,
        confirmation_type='password_reset'
    )


@pytest.fixture
def used_confirmation(db, user):
    """
    Creates an already used confirmation code.
    
    Usage:
        def test_used_code(used_confirmation):
            assert used_confirmation.is_used == True
    """
    return UserConfirmationFactory(
        user=user,
        confirmation_type='email_verification',
        is_used=True
    )


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_send_email(mocker):
    """
    Mock email sending to avoid sending real emails in tests.
    
    Usage:
        def test_registration(api_client, mock_send_email):
            response = api_client.post('/api/users/register/', data)
            mock_send_email.assert_called_once()
    """
    return mocker.patch('apps.users.services.verification_service.send_verification_code_email')


@pytest.fixture
def mock_celery_task(mocker):
    """
    Mock Celery tasks to run synchronously in tests.
    
    Usage:
        def test_async_task(mock_celery_task):
            # Task will run immediately instead of being queued
            pass
    """
    return mocker.patch('celery.app.task.Task.apply_async')