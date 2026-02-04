# apps/users/services/password_service.py
"""
Password Service
----------------
Password change and reset business logic
"""

from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordService:
    """Password management business logic"""
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Hozirgi parolni o'zgartirish
        
        Args:
            user (User): User instance
            old_password (str): Eski parol
            new_password (str): Yangi parol
        
        Returns:
            User: Updated user
        
        Raises:
            ValueError: Eski parol noto'g'ri
        """
        if not user.check_password(old_password):
            raise ValueError("Eski parol noto'g'ri!")
        
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        return user
    
    @staticmethod
    def reset_password(user, new_password):
        """
        Parolni tiklash (forgot password uchun)
        
        Args:
            user (User): User instance
            new_password (str): Yangi parol
        
        Returns:
            User: Updated user
        """
        user.set_password(new_password)
        user.save(update_fields=['password'])
        
        return user