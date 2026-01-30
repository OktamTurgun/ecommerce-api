from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator

    Django'ning PasswordResetTokenGenerator'ini extend qiladi
    Email verification uchun ham ishlatish mumkin
    """
    def _make_hash_value(self, user, timestamp):
        """
        Token'ni unique qilish uchun
        
        Quyidagilardan hash yaratadi:
        - user.pk
        - timestamp
        - user.is_active
        - user.last_login (agar bo'lsa)
        """
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return f"{user.pk}{timestamp}{user.is_active}{login_timestamp}"

# Token generator instance  
account_activation_token = TokenGenerator()

def encode_uid(user):
    """
    User ID'ni encode qilish (URL-safe base64)
    
    Args:
        user: User instance
    
    Returns:
        Encoded UID string
    
    Example:
        encode_uid(user) → "MQ"
    """
    return urlsafe_base64_encode(force_bytes(user.pk))

def decode_uid(uidb64):
    """
    Encoded UID'ni decode qilish
    
    Args:
        uidb64: Encoded UID string
    
    Returns:
        User ID (int) yoki None
    
    Example:
        decode_uid("MQ") → 1
    """
    try:
        uid =force_str(urlsafe_base64_decode(uidb64))
        return uid
    except (TypeError, ValueError, OverflowError):
        return None
    
def get_user_from_uid(uidb64):
    """
    UID'dan User obyektini olish
    
    Args:
        uidb64: Encoded UID
    
    Returns:
        User instance yoki None
    """
    uid = decode_uid(uidb64)
    if uid:
        try:
            user = User.objects.get(pk=uid)
            return user
        except User.DoesNotExist:
            return None
    return None
