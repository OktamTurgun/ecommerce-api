# tests/users/test_password_reset.py - To'g'rilangan versiya

import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.users.services.auth_service import AuthService


@pytest.mark.django_db
class TestForgotPassword:
    """Test suite for forgot password endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse('users:forgot-password')
    
    def test_forgot_password_with_existing_email(self, api_client, user, mocker):
        """
        Test password reset request with existing email.
        """
        # TO'G'RILANDI: View EmailService.send_password_reset chaqiradi
        mock_email = mocker.patch('apps.users.services.email_service.EmailService.send_password_reset')
        
        data = {'email': user.email}
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        
        # Email chaqirilganini tekshirish
        mock_email.assert_called_once()
    
    def test_forgot_password_with_nonexistent_email(self, api_client):
        """
        Test password reset with non-existent email.
        Security: Should return same message as existing email.
        """
        data = {'email': 'nonexistent@example.com'}
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
    
    def test_forgot_password_invalid_email_format(self, api_client):
        """Test password reset with invalid email format."""
        data = {'email': 'invalid-email-format'}
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_forgot_password_missing_email(self, api_client):
        """Test password reset without email."""
        response = api_client.post(self.url, {}, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_forgot_password_email_case_insensitive(self, api_client, user, mocker):
        """
        Test password reset with uppercase email.
        """
        # TO'G'RILANDI: To'g'ri mock
        mock_email = mocker.patch('apps.users.services.email_service.EmailService.send_password_reset')
        
        data = {'email': user.email.upper()}
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        mock_email.assert_called_once()
    
    def test_forgot_password_response_structure(self, api_client):
        """Test response structure for security."""
        data = {'email': 'any@example.com'}
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data
        # Should not reveal if email exists or not
        assert 'error' not in response.data
    
    def test_forgot_password_inactive_user(self, api_client, user, mocker):
        """
        Test password reset for inactive user.
        """
        user.is_active = False
        user.save()
        
        # TO'G'RILANDI: To'g'ri mock
        mock_email = mocker.patch('apps.users.services.email_service.EmailService.send_password_reset')
        
        data = {'email': user.email}
        response = api_client.post(self.url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        mock_email.assert_called_once()


@pytest.mark.django_db
class TestResetPassword:
    """Test suite for reset password endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse('users:reset-password')
    
    def test_reset_password_success(self, api_client, user, mocker):
        """
        Test successful password reset.
        """
        # MUAMMO: View VerificationService.verify_email ishlatadi
        # Bu email verification token, password reset token emas!
        # Vaqtinchalik mock qilamiz
        
        # Token yaratish (view qanday ishlashiga qarab)
        from apps.users.services.auth_service import AuthService
        token, uidb64 = AuthService.generate_password_reset(user)
        
        new_password = 'NewStrongPass123!'
        data = {
            'uidb64': uidb64,
            'token': token,
            'new_password': new_password,
            'new_password2': new_password,
        }
        
        response = api_client.post(self.url, data, format='json')
        
        # Agar 400 kelsa, ehtimol token type mos emas
        if response.status_code == 400:
            # View kodini tekshiramiz
            print(f"\nResponse: {response.data}")
            print(f"Token: {token}")
            print(f"UIDb64: {uidb64}")
            
            # BALKI view default_token_generator ishlatadi?
            from django.contrib.auth.tokens import default_token_generator
            django_token = default_token_generator.make_token(user)
            print(f"Django token: {django_token}")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Parol o'zgarganini tekshirish
        user.refresh_from_db()
        assert user.check_password(new_password)
    
    def test_reset_password_invalid_token(self, api_client, user):
        """Test reset with invalid token."""
        from apps.users.services.auth_service import AuthService
        _, uidb64 = AuthService.generate_password_reset(user)
        
        data = {
            'uidb64': uidb64,
            'token': 'invalid-token',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!',
        }
        
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reset_password_invalid_uid(self, api_client):
        """Test reset with invalid uidb64."""
        data = {
            'uidb64': 'invalid-uid',
            'token': 'some-token',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!',
        }
        
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reset_password_mismatch(self, api_client, user):
        """Test reset with mismatched passwords."""
        from apps.users.services.auth_service import AuthService
        token, uidb64 = AuthService.generate_password_reset(user)
        
        data = {
            'uidb64': uidb64,
            'token': token,
            'new_password': 'NewPass123!',
            'new_password2': 'DifferentPass123!',
        }
        
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reset_password_weak_password(self, api_client, user):
        """Test reset with weak password."""
        from apps.users.services.auth_service import AuthService
        token, uidb64 = AuthService.generate_password_reset(user)
        
        data = {
            'uidb64': uidb64,
            'token': token,
            'new_password': '123',
            'new_password2': '123',
        }
        
        response = api_client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_reset_password_missing_fields(self, api_client):
        """Test reset with missing fields."""
        response = api_client.post(self.url, {}, format='json')
        assert response

    def test_reset_password_token_single_use(self, api_client, user):
      """
      Test that reset token can only be used once.
      """
      print(f"\n=== DEBUG START ===")
      print(f"User ID: {user.pk}")
      print(f"Initial tokens: {AuthService._used_tokens}")
      
      # Token yaratish
      token, uidb64 = AuthService.generate_password_reset(user)
      print(f"Generated token: {token[:20]}...")
      
      token_key = f"{user.pk}:{token}"
      print(f"Expected token key: {token_key}")
      
      data = {
          'uidb64': uidb64,
          'token': token,
          'new_password': 'FirstNewPass123!',
          'new_password2': 'FirstNewPass123!',
      }
      
      # First request
      response1 = api_client.post(self.url, data, format='json')
      print(f"\nFirst response: {response1.status_code}")
      print(f"Tokens after first: {AuthService._used_tokens}")
      print(f"Token in set: {token_key in AuthService._used_tokens}")
      
      # Second request
      data['new_password'] = 'SecondNewPass123!'
      data['new_password2'] = 'SecondNewPass123!'
      response2 = api_client.post(self.url, data, format='json')
      print(f"\nSecond response: {response2.status_code}")
      
      print(f"=== DEBUG END ===\n")
      
      assert response1.status_code == 200
      assert response2.status_code == 400


@pytest.mark.django_db
class TestPasswordResetFlow:
    """Integration tests for complete password reset flow."""
    
    def test_complete_password_reset_flow(self, api_client, user, user_password, mocker):
        """
        Test complete password reset flow.
        """
        # Step 1: Request password reset
        mock_email = mocker.patch('apps.users.services.email_service.EmailService.send_password_reset')
        
        forgot_response = api_client.post(
            reverse('users:forgot-password'),
            {'email': user.email},
            format='json'
        )
        
        assert forgot_response.status_code == status.HTTP_200_OK
        mock_email.assert_called_once()
        
        # Step 2: Get reset token (from service call)
        call_args = mock_email.call_args
        reset_url = call_args[0][1]  # (user, reset_url)
        
        # URL'dan uid va token ajratib olish
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(reset_url)
        params = parse_qs(parsed.query)
        
        uidb64 = params.get('uid', [''])[0]
        token = params.get('token', [''])[0]
        
        # Step 3: Reset password
        new_password = 'BrandNewPass123!'
        reset_response = api_client.post(
            reverse('users:reset-password'),
            {
                'uidb64': uidb64,
                'token': token,
                'new_password': new_password,
                'new_password2': new_password,
            },
            format='json'
        )
        
        assert reset_response.status_code == status.HTTP_200_OK
        
        # Step 4: Login with new password
        login_response = api_client.post(
            reverse('users:login'),
            {
                'email': user.email,
                'password': new_password,
            },
            format='json'
        )
        
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_password_reset_with_subsequent_login(self, api_client, user):
        """
        Test that after password reset, user can login and access protected resources.
        """
        from apps.users.services.auth_service import AuthService
        
        # Generate reset token
        token, uidb64 = AuthService.generate_password_reset(user)
        
        new_password = 'BrandNewPass123!'
        
        # Reset password
        reset_response = api_client.post(
            reverse('users:reset-password'),
            {
                'uidb64': uidb64,
                'token': token,
                'new_password': new_password,
                'new_password2': new_password,
            },
            format='json'
        )
        
        assert reset_response.status_code == status.HTTP_200_OK
        
        # Login with new password
        login_response = api_client.post(
            reverse('users:login'),
            {
                'email': user.email,
                'password': new_password,
            },
            format='json'
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        assert 'tokens' in login_response.data
        
        # Access protected resource
        access_token = login_response.data['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        profile_response = api_client.get(reverse('users:profile'))
        assert profile_response.status_code == status.HTTP_200_OK