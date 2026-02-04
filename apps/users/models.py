from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email majburiy")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model
    Faqat foydalanuvchiga tegishli data
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ===== AUTH =====
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    # ===== PROFILE =====
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True, default="")

    # ===== ADDRESS (E-COMMERCE UCHUN MUHIM) =====
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True, default="Uzbekistan")
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    # ===== STATUS =====
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # ===== TIMESTAMPS =====
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        return self.first_name or self.email
    
    def get_full_name(self):
        return self.full_name
    
class UserConfirmation(models.Model):
    """
    Universal confirmation model:
    - Email verification
    - Phone verification
    - Password reset
    """

    CONFIRMATION_TYPES = (
        ("email_verification", "Email verification"),
        ("phone_verification", "Phone verification"),
        ("password_reset", "Password reset"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="confirmations"
    )

    confirmation_type = models.CharField(
        max_length=30,
        choices=CONFIRMATION_TYPES
    )

    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_confirmations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "confirmation_type"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["is_used"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.confirmation_type}"

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])