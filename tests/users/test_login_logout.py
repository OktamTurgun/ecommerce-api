"""
Tests for User Login and Logout APIs

This module tests:
1. UserLoginView - POST /api/users/login/
2. UserLogoutView - POST /api/users/logout/

Testing Approach:
- AAA Pattern (Arrange-Act-Assert)
- Test both success and failure scenarios
- Verify JWT token generation and blacklisting
- Check response structure for frontend integration
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import User


@pytest.mark.api
@pytest.mark.auth
class TestUserLogin:
    """
    Test suite for user login endpoint.
    
    Endpoint: POST /api/users/login/
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('users:login')
        self.password = 'TestPass123!'
    
    def test_successful_login(self, api_client, user, user_password):
        """
        Test successful login with valid credentials.
        
        Expected behavior:
        - Returns 200 OK
        - Returns user data
        - Returns access and refresh tokens
        - User last_login is updated
        """
        # Arrange
        data = {
            'email': user.email,
            'password': user_password,
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert: Status code
        assert response.status_code == status.HTTP_200_OK
        
        # Assert: Response structure
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'message' in response.data
        
        # Assert: User data
        user_data = response.data['user']['data']
        assert user_data['email'] == user.email
        assert 'password' not in user_data
        
        # Assert: Tokens
        tokens = response.data['tokens']
        assert 'access' in tokens
        assert 'refresh' in tokens
        assert len(tokens['access']) > 0
        assert len(tokens['refresh']) > 0
        
        # Assert: Last login updated
        user.refresh_from_db()
        assert user.last_login is not None
    
    def test_login_with_invalid_email(self, api_client):
        """
        Test login with non-existent email.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about invalid credentials
        """
        # Arrange
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!',
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data or 'error' in response.data
    
    def test_login_with_invalid_password(self, api_client, user):
        """
        Test login with wrong password.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about invalid password
        """
        # Arrange
        data = {
            'email': user.email,
            'password': 'WrongPassword123!',
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data or 'error' in response.data
    
    def test_login_with_inactive_user(self, api_client, user, user_password):
        """
        Test login attempt by inactive user.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about inactive account
        """
        # Arrange: Deactivate user
        user.is_active = False
        user.save()
        
        data = {
            'email': user.email,
            'password': user_password,
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data or 'error' in response.data
    
    def test_login_email_case_insensitive(self, api_client, user, user_password):
        """
        Test login with email in different case.
        
        Expected behavior:
        - Login succeeds with uppercase email
        - Email is normalized to lowercase
        """
        # Arrange: Use uppercase email
        data = {
            'email': user.email.upper(),
            'password': user_password,
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['data']['email'] == user.email.lower()
    
    def test_login_missing_required_fields(self, api_client):
        """
        Test login with missing required fields.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error messages for missing fields
        """
        # Arrange: Empty data
        data = {}
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert 'password' in response.data
    
    def test_login_response_structure(self, api_client, user, user_password):
        """
        Test that login response has correct structure.
        
        This is critical for frontend integration.
        """
        # Arrange
        data = {
            'email': user.email,
            'password': user_password,
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert: Top-level keys
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert 'message' in response.data
        
        # Assert: User nested structure
        assert 'success' in response.data['user']
        assert 'data' in response.data['user']
        
        # Assert: Required user fields
        user_data = response.data['user']['data']
        required_fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
        for field in required_fields:
            assert field in user_data, f"Missing required field: {field}"
        
        # Assert: Tokens structure
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
    
    def test_login_jwt_tokens_valid(self, api_client, user, user_password):
        """
        Test that generated JWT tokens are valid and can be used.
        
        Expected behavior:
        - Access token can be used for authentication
        - Refresh token can be used to get new access token
        """
        # Arrange
        data = {
            'email': user.email,
            'password': user_password,
        }
        
        # Act: Login
        login_response = api_client.post(self.url, data, format='json')
        
        # Assert: Login successful
        assert login_response.status_code == status.HTTP_200_OK
        
        # Get tokens
        access_token = login_response.data['tokens']['access']
        refresh_token = login_response.data['tokens']['refresh']
        
        # Test 1: Access token works for protected endpoint
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = api_client.get(reverse('users:profile'))
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Test 2: Refresh token works
        refresh_response = api_client.post(
            reverse('token_refresh'),
            {'refresh': refresh_token},
            format='json'
        )
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data


@pytest.mark.api
@pytest.mark.auth
class TestUserLogout:
    """
    Test suite for user logout endpoint.
    
    Endpoint: POST /api/users/logout/
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('users:logout')
    
    def test_successful_logout(self, authenticated_client, user):
        """
        Test successful logout.
        
        Expected behavior:
        - Returns 200 OK
        - Refresh token is blacklisted
        - Token cannot be used after logout
        """
        # Arrange: Get refresh token
        refresh = RefreshToken.for_user(user)
        refresh_token = str(refresh)
        
        data = {
            'refresh': refresh_token,
        }
        
        # Act: Logout
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert: Logout successful
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Assert: Token is blacklisted (cannot refresh)
        from rest_framework.test import APIClient
        new_client = APIClient()
        
        refresh_response = new_client.post(
            reverse('token_refresh'),
            {'refresh': refresh_token},
            format='json'
        )
        
        # Token should be invalid/blacklisted
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout_without_token(self, authenticated_client):
        """
        Test logout without providing refresh token.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about missing token
        """
        # Arrange: Empty data
        data = {}
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_logout_with_invalid_token(self, authenticated_client):
        """
        Test logout with invalid refresh token.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about invalid token
        """
        # Arrange: Invalid token
        data = {
            'refresh': 'invalid-token-string',
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_logout_requires_authentication(self, api_client, user):
        """
        Test that logout requires authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized if not authenticated
        """
        # Arrange: Generate a valid refresh token but don't authenticate
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
        }
        
        # Act: Try logout without authentication
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestLoginLogoutFlow:
    """
    Integration tests for complete login-logout flow.
    
    These tests verify the entire authentication lifecycle.
    """
    
    def test_complete_login_logout_flow(self, api_client, user, user_password):
        """
        Test complete authentication flow.
        
        Steps:
        1. Login with credentials
        2. Use access token to access protected resource
        3. Logout
        4. Verify tokens are invalidated
        """
        # Step 1: Login
        login_data = {
            'email': user.email,
            'password': user_password,
        }
        
        login_response = api_client.post(
            reverse('users:login'),
            login_data,
            format='json'
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        
        access_token = login_response.data['tokens']['access']
        refresh_token = login_response.data['tokens']['refresh']
        
        # Step 2: Access protected resource
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_response = api_client.get(reverse('users:profile'))
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Step 3: Logout
        logout_response = api_client.post(
            reverse('users:logout'),
            {'refresh': refresh_token},
            format='json'
        )
        
        assert logout_response.status_code == status.HTTP_200_OK
        
        # Step 4: Verify token is blacklisted
        refresh_response = api_client.post(
            reverse('token_refresh'),
            {'refresh': refresh_token},
            format='json'
        )
        
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_multiple_logins_same_user(self, api_client, user, user_password):
        """
        Test that user can login multiple times.
        
        Expected behavior:
        - Each login generates new tokens
        - Old tokens remain valid until explicitly logged out
        """
        # Login 1
        login1 = api_client.post(
            reverse('users:login'),
            {'email': user.email, 'password': user_password},
            format='json'
        )
        
        assert login1.status_code == status.HTTP_200_OK
        tokens1 = login1.data['tokens']
        
        # Login 2
        login2 = api_client.post(
            reverse('users:login'),
            {'email': user.email, 'password': user_password},
            format='json'
        )
        
        assert login2.status_code == status.HTTP_200_OK
        tokens2 = login2.data['tokens']
        
        # Assert: Different tokens
        assert tokens1['access'] != tokens2['access']
        assert tokens1['refresh'] != tokens2['refresh']
        
        # Assert: Both tokens work
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens1["access"]}')
        assert api_client.get(reverse('users:profile')).status_code == 200
        
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens2["access"]}')
        assert api_client.get(reverse('users:profile')).status_code == 200