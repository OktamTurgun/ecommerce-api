# core/utils.py
"""
Core Utility Functions
----------------------
Sizning UserConfirmation modelingiz uchun helper functions
"""

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# ==================== UID ENCODING/DECODING ====================
def encode_uid(user):
    """
    User ID'ni encode qilish (base64)
    
    Args:
        user: User instance
    
    Returns:
        str: Encoded user ID
    
    Example:
        >>> encode_uid(user)
        'MQ'
    """
    return urlsafe_base64_encode(force_bytes(user.pk))


def get_user_from_uid(uidb64):
    """
    Encoded UID'dan user olish
    
    Args:
        uidb64: Encoded user ID
    
    Returns:
        User instance yoki None
    
    Example:
        >>> get_user_from_uid('MQ')
        <User: user@example.com>
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


# ==================== TOKEN GENERATOR ====================
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator
    Token yaratish va tekshirish uchun
    """
    
    def _make_hash_value(self, user, timestamp):
        """
        Token hash yaratish
        User state o'zgarganda token invalid bo'ladi
        """
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )


account_activation_token = AccountActivationTokenGenerator()


# ==================== IP ADDRESS ====================
def get_client_ip(request):
    """
    Client IP address'ni olish
    
    Args:
        request: Django request obyekti
    
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip