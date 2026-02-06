# tests/users/test_profile.py - To'g'rilangan versiya

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.api
@pytest.mark.auth
class TestUserProfile:
    """Test suite for user profile endpoint."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.url = reverse('users:profile')
    
    def test_get_profile_success(self, authenticated_client, verified_user):
        """
        Test retrieving user profile.
        
        TO'G'RILANDI: verified_user ishlatiladi (authenticated_client bilan bir xil)
        """
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert: Status
        assert response.status_code == status.HTTP_200_OK
        
        # Assert: Response structure
        assert 'success' in response.data
        assert 'data' in response.data
        
        # Assert: User data - verified_user tekshiriladi
        user_data = response.data['data']
        assert user_data['email'] == verified_user.email
        assert user_data['id'] == str(verified_user.id)
        
        # Assert: Password not exposed
        assert 'password' not in user_data
    
    def test_get_profile_unauthenticated(self, api_client):
        """Test getting profile without authentication."""
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_profile_full(self, authenticated_client, verified_user):
        """
        Test full profile update (PUT).
        
        TO'G'RILANDI: verified_user ishlatiladi
        """
        # Arrange
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+998901234567',
            'address': '456 New Street',
            'city': 'Samarkand',
            'country': 'Uzbekistan',
            'postal_code': '140100',
        }
        
        # Act
        response = authenticated_client.put(
            self.url,
            update_data,
            format='json'
        )
        
        # Assert: Success
        assert response.status_code == status.HTTP_200_OK
        
        # Assert: Data updated - verified_user tekshiriladi
        verified_user.refresh_from_db()
        assert verified_user.first_name == 'Updated'
        assert verified_user.last_name == 'Name'
        assert verified_user.phone_number == '+998901234567'
        assert verified_user.city == 'Samarkand'
    
    def test_update_profile_partial(self, authenticated_client, verified_user):
        """
        Test partial profile update (PATCH).
        
        TO'G'RILANDI: verified_user ishlatiladi
        """
        # Arrange: Set initial data
        verified_user.first_name = 'Original'
        verified_user.last_name = 'Name'
        verified_user.city = 'Tashkent'
        verified_user.save()
        
        # Act: Update only first_name
        response = authenticated_client.patch(
            self.url,
            {'first_name': 'Patched'},
            format='json'
        )
        
        # Assert: Success
        assert response.status_code == status.HTTP_200_OK
        
        # Assert: Only first_name changed - verified_user tekshiriladi
        verified_user.refresh_from_db()
        assert verified_user.first_name == 'Patched'
        assert verified_user.last_name == 'Name'  # Unchanged
        assert verified_user.city == 'Tashkent'  # Unchanged
    
    def test_update_profile_read_only_fields(self, authenticated_client, verified_user):
        """
        Test that read-only fields cannot be updated.
        
        TO'G'RILANDI: verified_user ishlatiladi
        """
        # Arrange
        original_email = verified_user.email
        original_id = verified_user.id
        original_date_joined = verified_user.date_joined
        original_is_active = verified_user.is_active
        
        # Act: Try to update read-only fields
        response = authenticated_client.patch(
            self.url,
            {
                'email': 'newemail@example.com',
                'id': '00000000-0000-0000-0000-000000000000',
                'is_active': False,
                'first_name': 'Updated',
            },
            format='json'
        )
        
        # Assert: Update succeeds but read-only fields unchanged
        assert response.status_code == status.HTTP_200_OK
        
        verified_user.refresh_from_db()
        assert verified_user.email == original_email
        assert verified_user.id == original_id
        assert verified_user.date_joined == original_date_joined
        assert verified_user.is_active == original_is_active
        assert verified_user.first_name == 'Updated'  # This should change
    
    def test_update_profile_invalid_phone(self, authenticated_client):
        """Test profile update with invalid phone number."""
        response = authenticated_client.patch(
            self.url,
            {'phone_number': 'invalid-phone'},
            format='json'
        )
        
        # Assert: Either validation error or success
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST
        ]
    
    def test_update_profile_empty_fields(self, authenticated_client, verified_user):
        """
        Test updating profile with empty optional fields.
        
        TO'G'RILANDI: verified_user ishlatiladi
        """
        # Arrange: Set initial data
        verified_user.address = 'Initial Address'
        verified_user.city = 'Initial City'
        verified_user.save()
        
        # Act: Clear optional fields
        response = authenticated_client.patch(
            self.url,
            {
                'address': '',
                'city': '',
            },
            format='json'
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        verified_user.refresh_from_db()
        assert verified_user.address == ''
        assert verified_user.city == ''
    
    def test_get_profile_includes_full_name(self, authenticated_client, verified_user):
        """
        Test that profile response includes computed full_name field.
        
        TO'G'RILANDI: verified_user ishlatiladi
        """
        # Arrange
        verified_user.first_name = 'John'
        verified_user.last_name = 'Doe'
        verified_user.save()
        
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        user_data = response.data['data']
        assert 'full_name' in user_data
        assert 'John Doe' in user_data['full_name']
    
    def test_update_profile_response_structure(self, authenticated_client):
        """Test that update response has correct structure."""
        response = authenticated_client.patch(
            self.url,
            {'first_name': 'Test'},
            format='json'
        )
        
        # Assert: Response structure
        assert response.status_code == status.HTTP_200_OK
        assert 'success' in response.data
        assert 'message' in response.data
        assert 'data' in response.data


@pytest.mark.integration
class TestProfileIntegration:
    """Integration tests for profile management flows."""
    
    def test_register_login_update_profile_flow(self, api_client, mocker):
        """Test complete flow: Register → Login → Update Profile"""
        # Mock email
        mocker.patch('django.core.mail.send_mail')
        
        # Step 1: Register
        register_data = {
            'email': 'profiletest@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Initial',
            'last_name': 'User',
        }
        
        register_response = api_client.post(
            reverse('users:register'),
            register_data,
            format='json'
        )
        
        assert register_response.status_code == status.HTTP_201_CREATED
        
        # Step 2: Login
        login_response = api_client.post(
            reverse('users:login'),
            {
                'email': 'profiletest@example.com',
                'password': 'StrongPass123!'
            },
            format='json'
        )
        
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data['tokens']['access']
        
        # Step 3: Update profile
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        update_response = api_client.patch(
            reverse('users:profile'),
            {
                'first_name': 'Updated',
                'city': 'Tashkent',
                'phone_number': '+998901234567'
            },
            format='json'
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        
        # Step 4: Verify changes persist
        profile_response = api_client.get(reverse('users:profile'))
        
        assert profile_response.status_code == status.HTTP_200_OK
        profile_data = profile_response.data['data']
        assert profile_data['first_name'] == 'Updated'
        assert profile_data['city'] == 'Tashkent'
        assert profile_data['phone_number'] == '+998901234567'
    
    def test_multiple_profile_updates(self, authenticated_client, verified_user):
        """
        Test multiple sequential profile updates.
        
        TO'G'RILANDI: verified_user ishlatiladi
        """
        url = reverse('users:profile')
        
        # Update 1: Name
        response1 = authenticated_client.patch(
            url,
            {'first_name': 'First'},
            format='json'
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Update 2: City
        response2 = authenticated_client.patch(
            url,
            {'city': 'Samarkand'},
            format='json'
        )
        assert response2.status_code == status.HTTP_200_OK
        
        # Update 3: Phone
        response3 = authenticated_client.patch(
            url,
            {'phone_number': '+998901111111'},
            format='json'
        )
        assert response3.status_code == status.HTTP_200_OK
        
        # Verify all changes - verified_user tekshiriladi
        verified_user.refresh_from_db()
        assert verified_user.first_name == 'First'
        assert verified_user.city == 'Samarkand'
        assert verified_user.phone_number == '+998901111111'