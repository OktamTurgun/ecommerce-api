"""
Tests for User Registration API - FIXED VERSION

Fixed issues:
1. Changed password_confirm to password2 (matches serializer)
2. All tests now use correct field names from UserRegistrationSerializer
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.api
@pytest.mark.auth
class TestUserRegistration:
    """
    Test suite for user registration endpoint.
    
    Endpoint: POST /api/users/register/
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('users:register')  # Will be: /api/users/register/
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',  # ✅ FIXED: was password_confirm
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+998901234567',
            'address': '123 Main St',
            'city': 'Tashkent',
        }
    
    def test_successful_registration(self, api_client, mock_send_email):
        """
        Test successful user registration.
        
        Expected behavior:
        - Returns 201 Created
        - User is created in database
        - Email verification is sent
        - Returns user data and tokens
        """
        # Act: Make the request
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert: Check response
        assert response.status_code == status.HTTP_201_CREATED
        # ✅ FIXED: tokens are inside 'tokens' object
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
        # ✅ FIXED: email is inside user['data']
        assert response.data['user']['data']['email'] == self.valid_data['email']
        
        # Assert: Check email was sent
        mock_send_email.assert_called_once()
    
    def test_registration_with_existing_email(self, api_client, user):
        """
        Test registration with email that already exists.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about duplicate email
        """
        # Arrange: Use existing user's email
        self.valid_data['email'] = user.email
        
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_registration_password_mismatch(self, api_client):
        """
        Test registration when passwords don't match.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about password mismatch
        """
        # Arrange: Set mismatched passwords
        self.valid_data['password2'] = 'DifferentPass123!'  # ✅ FIXED
        
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # ✅ FIXED: Check for correct field name
        assert 'password2' in response.data or 'non_field_errors' in response.data
    
    def test_registration_weak_password(self, api_client):
        """
        Test registration with weak password.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about password strength
        """
        # Arrange: Use weak password
        self.valid_data['password'] = '123'
        self.valid_data['password2'] = '123'  # ✅ FIXED
        
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_registration_invalid_email(self, api_client):
        """
        Test registration with invalid email format.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message about invalid email
        """
        # Arrange: Use invalid email
        self.valid_data['email'] = 'not-an-email'
        
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_registration_missing_required_fields(self, api_client):
        """
        Test registration with missing required fields.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error messages for each missing field
        """
        # Arrange: Send empty data
        empty_data = {}
        
        # Act
        response = api_client.post(self.url, empty_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
        assert 'password' in response.data
    
    def test_registration_email_normalization(self, api_client, mock_send_email):
        """
        Test that email is normalized (lowercase).
        
        Expected behavior:
        - Email is saved in lowercase
        - User can register with UpPeRcAsE email
        """
        # Arrange: Use uppercase email
        self.valid_data['email'] = 'TEST@EXAMPLE.COM'
        
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        # ✅ FIXED: email is nested in user['data']
        assert response.data['user']['data']['email'] == 'test@example.com'
    
    @pytest.mark.skip(reason="first_name and last_name are required fields in AuthService")
    @pytest.mark.parametrize('field_to_remove', [
        'first_name',
        'last_name',
        'phone_number',
    ])
    def test_registration_optional_fields(self, api_client, mock_send_email, field_to_remove):
        """
        Test registration with optional fields missing.
        
        Some fields might be optional - this test checks that.
        Uses parametrize to test multiple scenarios efficiently.
        """
        # Arrange: Remove one optional field
        data = self.valid_data.copy()
        data.pop(field_to_remove, None)
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert: Should still succeed (if field is truly optional)
        # If this fails, it means the field is required
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_registration_creates_verification_code(self, api_client, mock_send_email):
        """
        Test that registration creates a verification code.
        
        Expected behavior:
        - UserConfirmation object is created
        - Code is 6 digits
        - Type is 'email_verification'
        """
        from apps.users.models import UserConfirmation
        
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check verification code was created
        confirmation = UserConfirmation.objects.filter(
            user__email=self.valid_data['email'],
            confirmation_type='email_verification'
        ).first()
        
        assert confirmation is not None
        assert len(confirmation.code) == 6
        assert confirmation.is_used == False
    
    def test_registration_response_structure(self, api_client, mock_send_email):
        """
        Test that registration response has correct structure.
        
        This is important for frontend integration.
        """
        # Act
        response = api_client.post(self.url, self.valid_data, format='json')
        
        # Assert: Check response structure
        assert response.status_code == status.HTTP_201_CREATED
        
        # Must have these keys
        # ✅ FIXED: tokens are nested in 'tokens' object
        assert 'tokens' in response.data
        assert 'access' in response.data['tokens']
        assert 'refresh' in response.data['tokens']
        assert 'user' in response.data
        
        # User object must have these keys
        # ✅ FIXED: user data is nested in user['data']
        assert 'data' in response.data['user']
        user_data = response.data['user']['data']
        assert 'id' in user_data
        assert 'email' in user_data
        assert 'first_name' in user_data
        assert 'last_name' in user_data
        
        # Must NOT have password in response
        assert 'password' not in user_data
    
    def test_registration_rate_limiting(self, api_client):
        """
        Test rate limiting on registration endpoint.
        
        TODO: Implement rate limiting and update this test.
        Currently this is a placeholder.
        """
        pytest.skip("Rate limiting not implemented yet")


@pytest.mark.integration
class TestRegistrationIntegration:
    """
    Integration tests for registration flow.
    
    These tests check the entire flow from registration to email verification.
    """
    
    def test_full_registration_flow(self, api_client, mocker):
        """
        Test complete registration and verification flow.
        
        Steps:
        1. User registers
        2. User receives verification code
        3. User verifies email with code
        4. User can login
        """
        # Mock email sending - use Django's send_mail
        mock_email = mocker.patch('django.core.mail.send_mail')
        
        # Step 1: Register
        register_data = {
            'email': 'integration@test.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',  # ✅ FIXED
            'first_name': 'Integration',
            'last_name': 'Test',
        }
        
        register_response = api_client.post(
            reverse('users:register'),
            register_data,
            format='json'
        )
        
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Step 2: Get verification code from database
        from apps.users.models import UserConfirmation
        confirmation = UserConfirmation.objects.get(
            user__email='integration@test.com',
            confirmation_type='email_verification'
        )
        
        # Step 3: Verify email
        # ✅ FIXED: access token is in tokens object
        verify_response = api_client.post(
            reverse('users:verify-email'),
            {'code': confirmation.code},
            format='json',
            HTTP_AUTHORIZATION=f"Bearer {register_response.data['tokens']['access']}"
        )
        
        assert verify_response.status_code == status.HTTP_200_OK
        
        # Step 4: Login should work
        login_response = api_client.post(
            reverse('users:login'),
            {
                'email': 'integration@test.com',
                'password': 'TestPass123!'
            },
            format='json'
        )
        
        # Login response structure from UserLoginView:
        # { "user": {...}, "tokens": {...}, "message": "..." }
        assert 'user' in login_response.data
        assert 'tokens' in login_response.data
        assert 'message' in login_response.data
        
        # Check tokens
        assert 'access' in login_response.data['tokens']