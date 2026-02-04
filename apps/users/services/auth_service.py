# apps/users/services/auth_service.py
"""
Authentication Service
----------------------
User registration, login, logout business logic
"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import AuthenticationFailed
from .verification_service import VerificationService
from .token_service import TokenService

User = get_user_model()


class AuthService:
    """Authentication business logic"""
    
    @staticmethod
    def register_user(email, password, first_name, last_name, phone_number=None, **kwargs):
        """
        Yangi user ro'yxatdan o'tkazish
        
        Args:
            email (str): User email
            password (str): User password
            first_name (str): First name
            last_name (str): Last name  
            phone_number (str, optional): Phone number
        
        Returns:
            tuple: (user, tokens)
        """
        # Remove password2 if present
        kwargs.pop('password2', None)
        
        # 1. User yaratish
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        
        # 2. Verification code yaratish va yuborish
        VerificationService.send_email_verification(user)
        
        # 3. JWT tokens yaratish
        tokens = TokenService.generate_tokens(user)
        
        return user, tokens
    
    @staticmethod
    def login_user(email, password):
        """
        User login qilish
        
        Args:
            email (str): User email
            password (str): User password
        
        Returns:
            tuple: (user, tokens)
        
        Raises:
            AuthenticationFailed: Invalid credentials
        """
        # 1. User olish
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            return None, None
        
        # 2. Password tekshirish
        if not user.check_password(password):
            return None, None
        
        # 3. User active ekanligini tekshirish
        if not user.is_active:
            raise AuthenticationFailed("Bu akkaunt faol emas!")
        
        # 4. Tokens yaratish
        tokens = TokenService.generate_tokens(user)
        
        return user, tokens
    
    @staticmethod
    def get_user_by_email(email):
        """
        Email orqali user olish
        
        Args:
            email (str): User email
        
        Returns:
            User: User instance
        
        Raises:
            User.DoesNotExist: User topilmasa
        """
        return User.objects.get(email=email.lower())
    
    @staticmethod
    def is_email_taken(email, exclude_user=None):
        """
        Email band yoki yo'qligini tekshirish
        
        Args:
            email (str): Email address
            exclude_user (User, optional): Exclude this user from check
        
        Returns:
            bool: Email band bo'lsa True
        """
        queryset = User.objects.filter(email=email.lower())
        
        if exclude_user:
            queryset = queryset.exclude(pk=exclude_user.pk)
        
        return queryset.exists()
    
    @staticmethod
    def update_email(user, new_email):
        """
        User email'ni yangilash
        
        Args:
            user (User): User instance
            new_email (str): Yangi email
        
        Returns:
            User: Updated user
        """
        user.email = new_email.lower()
        user.save(update_fields=['email'])
        return user
    
    @staticmethod
    def generate_password_reset(user):
        """
        Password reset token yaratish (LINK uchun)
        
        Args:
            user (User): User instance
        
        Returns:
            tuple: (token, uidb64)
        """
        from core.utils import account_activation_token, encode_uid
        
        token = account_activation_token.make_token(user)
        uidb64 = encode_uid(user)
        
        return token, uidb64