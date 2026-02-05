"""
Test Data Factories using Factory Boy.

Factories help create test data quickly and consistently.
Instead of manually creating objects, we use factories.

Example:
    # Old way (tedious):
    user = User.objects.create(
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        ...
    )
    
    # New way (simple):
    user = UserFactory()
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()


class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances for testing.
    
    Usage:
        # Create a user with default values
        user = UserFactory()
        
        # Create a user with custom email
        user = UserFactory(email='custom@example.com')
        
        # Create multiple users
        users = UserFactory.create_batch(5)
        
        # Create user without saving to DB (for unit tests)
        user = UserFactory.build()
    """
    class Meta:
        model = 'users.User'
        django_get_or_create = ('email',)
    
    # Basic fields
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    # Phone number
    phone_number = factory.Faker('phone_number')
    
    # Address fields
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    country = 'Uzbekistan'
    postal_code = factory.Faker('postcode')
    
    # Status fields
    is_active = True
    is_staff = False
    is_superuser = False
    
    # Password
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """
        Set password after user is generated.
        Default password: TestPass123!
        
        Usage:
            user = UserFactory(password='custom_password')
        """
        password = extracted if extracted else 'TestPass123!'
        obj.set_password(password)
        if create:
            obj.save()


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin users.
    
    Usage:
        admin = AdminUserFactory()
    """
    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f'admin{n}@example.com')


class UserConfirmationFactory(DjangoModelFactory):
    """
    Factory for creating UserConfirmation instances.
    
    Usage:
        # Email verification code
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='email_verification'
        )
        
        # Password reset code
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='password_reset'
        )
    """
    class Meta:
        model = 'users.UserConfirmation'
    
    user = factory.SubFactory(UserFactory)
    confirmation_type = 'email_verification'
    code = factory.Sequence(lambda n: f'{100000 + n}')  # 6-digit code
    is_used = False
    
    # Expiry: 15 minutes from now
    @factory.lazy_attribute
    def expires_at(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() + timedelta(minutes=15)


# Additional factories for future use
# These are commented out until Products app is implemented

# class ProductFactory(DjangoModelFactory):
#     """
#     Factory for Product model (to be implemented).
#     
#     This is a placeholder for when we implement Products app.
#     """
#     class Meta:
#         model = 'products.Product'
#     
#     name = factory.Faker('word')
#     description = factory.Faker('text')
#     price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
#     stock = factory.Faker('random_int', min=0, max=1000)


# class CategoryFactory(DjangoModelFactory):
#     """
#     Factory for Category model (to be implemented).
#     """
#     class Meta:
#         model = 'products.Category'
#     
#     name = factory.Faker('word')
#     description = factory.Faker('sentence')


# Helper functions for common test scenarios

def create_user_with_verification(email=None, verified=False):
    """
    Helper function to create a user with verification code.
    
    Args:
        email: Custom email (optional)
        verified: Whether user is verified (default: False)
    
    Returns:
        tuple: (user, confirmation_code)
    
    Usage:
        user, code = create_user_with_verification()
        user, code = create_user_with_verification(verified=True)
    """
    user = UserFactory(email=email) if email else UserFactory()
    
    if verified:
        user.is_active = True
        user.save()
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='email_verification',
            is_used=True
        )
    else:
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='email_verification'
        )
    
    return user, confirmation.code


def create_authenticated_client(user=None):
    """
    Helper function to create an authenticated API client.
    
    Args:
        user: Custom user (optional, creates new user if not provided)
    
    Returns:
        tuple: (api_client, user)
    
    Usage:
        client, user = create_authenticated_client()
    """
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    if user is None:
        user = UserFactory()
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client, user