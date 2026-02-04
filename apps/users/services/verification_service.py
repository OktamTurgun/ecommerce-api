# apps/users/services/verification_service.py
"""
Verification Service
--------------------
UserConfirmation model bilan ishlash
"""

import random
import string
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.users.models import UserConfirmation
from core.emails import (
    send_verification_code_email,
    send_password_reset_code_email,
    send_email_change_code
)
from core.utils import account_activation_token

User = get_user_model()


class VerificationService:
    """Verification business logic"""
    
    CODE_LENGTH = 6
    CODE_EXPIRY_MINUTES = 15
    
    @classmethod
    def generate_code(cls, length=None):
        """
        Random kod yaratish
        
        Args:
            length (int): Kod uzunligi
        
        Returns:
            str: 6 raqamli kod
        """
        length = length or cls.CODE_LENGTH
        return ''.join(random.choices(string.digits, k=length))
    
    @classmethod
    def create_confirmation(cls, user, confirmation_type):
        """
        UserConfirmation yaratish
        
        Args:
            user (User): User instance
            confirmation_type (str): Confirmation turi
        
        Returns:
            tuple: (confirmation, code)
        """
        # Eski confirmation'larni bekor qilish
        UserConfirmation.objects.filter(
            user=user,
            confirmation_type=confirmation_type,
            is_used=False
        ).update(is_used=True)
        
        # Yangi confirmation yaratish
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=cls.CODE_EXPIRY_MINUTES)
        
        confirmation = UserConfirmation.objects.create(
            user=user,
            confirmation_type=confirmation_type,
            code=code,
            expires_at=expires_at
        )
        
        return confirmation, code
    
    @classmethod
    def verify_confirmation(cls, user, code, confirmation_type):
        """
        Confirmation code tekshirish
        
        Args:
            user (User): User instance
            code (str): Kiritilgan kod
            confirmation_type (str): Confirmation turi
        
        Returns:
            tuple: (success: bool, message: str, confirmation: UserConfirmation|None)
        """
        try:
            confirmation = UserConfirmation.objects.get(
                user=user,
                code=code,
                confirmation_type=confirmation_type,
                is_used=False
            )
        except UserConfirmation.DoesNotExist:
            return False, "Tasdiqlash kodi noto'g'ri!", None
        
        # Muddati o'tganligini tekshirish
        if confirmation.is_expired():
            return False, "Tasdiqlash kodi muddati o'tgan!", None
        
        # Kodni ishlatilgan deb belgilash
        confirmation.mark_as_used()
        
        return True, "Kod to'g'ri!", confirmation
    
    # ==================== EMAIL VERIFICATION ====================
    @classmethod
    def send_email_verification(cls, user):
        """
        Email verification code yuborish
        
        Args:
            user (User): User instance
        
        Returns:
            str: Yaratilgan kod
        """
        confirmation, code = cls.create_confirmation(
            user=user,
            confirmation_type='email_verification'
        )
        
        # Email yuborish
        send_verification_code_email(user, code)
        
        return code
    
    @classmethod
    def verify_email(cls, user, token):
        """
        Email verification (LINK uchun - legacy)
        
        Args:
            user (User): User instance
            token (str): Verification token
        
        Returns:
            bool: Success
        """
        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save(update_fields=['is_active'])
            return True
        return False
    
    @classmethod
    def verify_email_code(cls, user, code):
        """
        Email verification (CODE bilan)
        
        Args:
            user (User): User instance
            code (str): 6 raqamli kod
        
        Returns:
            tuple: (success: bool, message: str)
        """
        success, message, confirmation = cls.verify_confirmation(
            user=user,
            code=code,
            confirmation_type='email_verification'
        )
        
        if success:
            # Email'ni tasdiqlash
            user.is_active = True
            user.save(update_fields=['is_active'])
        
        return success, message
    
    # ==================== PASSWORD RESET ====================
    @classmethod
    def send_password_reset(cls, user):
        """
        Password reset code yuborish
        
        Args:
            user (User): User instance
        
        Returns:
            str: Yaratilgan kod
        """
        confirmation, code = cls.create_confirmation(
            user=user,
            confirmation_type='password_reset'
        )
        
        # Email yuborish
        send_password_reset_code_email(user, code)
        
        return code
    
    @classmethod
    def verify_password_reset_code(cls, user, code):
        """
        Password reset code tekshirish
        
        Args:
            user (User): User instance
            code (str): 6 raqamli kod
        
        Returns:
            tuple: (success: bool, message: str)
        """
        return cls.verify_confirmation(
            user=user,
            code=code,
            confirmation_type='password_reset'
        )[:2]  # Faqat success va message
    
    # ==================== EMAIL CHANGE ====================
    @classmethod
    def send_email_change_verification(cls, user, new_email):
        """
        Email change verification code yuborish
        
        Args:
            user (User): User instance
            new_email (str): Yangi email
        
        Returns:
            str: Yaratilgan kod
        """
        confirmation, code = cls.create_confirmation(
            user=user,
            confirmation_type='email_verification'  # Email verification type ishlatamiz
        )
        
        # Yangi email'ga code yuborish
        send_email_change_code(user, new_email, code)
        
        return code