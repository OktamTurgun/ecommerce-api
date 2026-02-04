"""
Email Service
-------------
Email sending wrapper (core.emails'dan foydalanadi)
"""

from core.emails import (
    send_verification_code_email,
    send_password_reset_code_email,
    send_email_change_code
)


class EmailService:
    """Email sending business logic"""
    
    @staticmethod
    def send_verification(user, code):
        """Email verification code yuborish"""
        return send_verification_code_email(user, code)
    
    @staticmethod
    def send_password_reset(user, reset_url):
        """Password reset link yuborish (LINK uchun - legacy)"""
        # core.emails'da send_password_reset_code_email mavjud
        # Lekin LINK uchun alohida function kerak
        # Hozircha shunchaki placeholder
        pass
    
    @staticmethod
    def send_password_reset_code(user, code):
        """Password reset code yuborish"""
        return send_password_reset_code_email(user, code)
    
    @staticmethod
    def send_email_change(user, new_email, code):
        """Email change verification code yuborish"""
        return send_email_change_code(user, new_email, code)
