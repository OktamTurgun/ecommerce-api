"""
Token Service
-------------
JWT token operations
"""

from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:
    """JWT token business logic"""
    
    @staticmethod
    def generate_tokens(user):
        """
        User uchun JWT tokens yaratish
        
        Args:
            user (User): User instance
        
        Returns:
            dict: {'access': '...', 'refresh': '...'}
        """
        refresh = RefreshToken.for_user(user)
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    @staticmethod
    def blacklist_token(refresh_token):
        """
        Refresh token'ni blacklist qilish
        
        Args:
            refresh_token (str): Refresh token string
        
        Returns:
            bool: Success
        
        Raises:
            Exception: Token invalid
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return True
        except Exception as e:
            raise Exception("Token noto'g'ri yoki allaqachon bekor qilingan!")