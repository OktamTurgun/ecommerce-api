from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom User Manager

    Vazifa:
    - create_user() - oddiy user yaratish
    - create_superuser() - admin yaratish
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Oddiy user yaratish

        Args:
            email: user email
            password: user password
            **extra_fields: qo'shimcha fieldlar (first_name, phone, etc)

        Returns:
            User obyekti
        """

        # 1. Email tekshirish
        if not email:
            raise ValueError("Email majburiy!")

        # 2. Email normalizatsiya (lowercase, trim)
        email = self.normalize_email(email)

        # 3. User obyekti yaratish
        user = self.model(email=email, **extra_fields)

        # 4. Password hash qilish (plain text emas!)
        user.set_password(password)

        # 5. Datebase'ga saqlash
        user.save(using=self._db)

        return user

    def create_suoeruser(self, email, password=None, **extra_fields):
        """
        Admin/Superuser yaratish

        Farqi:
        - is_staff = True
        - is_superuser = True
        - is_active = True
        """

        # 1. Default qiymatlar
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # 2. Tekshirish
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser is_staff=True bo'lishi kerak.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser is_superuser=True bo'lishi kerak.")

        # 3. Oddiy user yaratish method'ini chaqirish
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    
    Asosiy o'zgarishlar:
    - Username o'rniga Email ishlatiladi
    - Qo'shimcha fieldlar: phone, address, etc
    """
    
    # ==================== ASOSIY FIELDLAR ====================
    email = models.EmailField(          # Takrorlanmasligi kerak
        unique=True,                    # Admin panelda ko'rinishi
        verbose_name="Email manzil",    # Qo'shimcha ma'lumot
        help_text="User email manzili"
    )

    first_name = models.CharField(
        max_length=50, 
        blank=True,                     # Bo'sh bo'lishi mumkin (form'da)
        verbose_name="Ism"
    )
    last_name = models.CharField(
        max_length=50, 
        null=True,                      # Database'da NULL bo'lishi mumkin
        verbose_name="Familiya"
    )

    # ==================== CONTACT INFO ====================
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Telefon raqam",
        help_text="+998901234567 formatda",
    )

    # ==================== ADDRESS FIELDLARI ====================
    address = models.TextField(
        max_length=100, blank=True, null=True, verbose_name="To'liq manzil"
    )
    city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Shahar"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Uzbekistan",
        verbose_name="Mamlakat",
    )
    postal_code = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Pochta indeksi"
    )

    # ==================== PERMISSIONS ====================
    is_active = models.BooleanField(
        default=True, verbose_name="Active", help_text="User login qila oladimi?"
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff status",
        help_text="Admin panelga kirish xuquqi",
    )

    is_superuser = models.BooleanField(
        default=False, verbose_name="Superuser status", help_text="Barcha ruxsatlar"
    )

    # ==================== TIMESTAMPS ====================
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name="Ro'yxatdan o'tgan sana"
    )

    last_login = models.DateTimeField(
        blank=True, null=True, verbose_name="Oxirgi kirish"
    )

    # ==================== SETTINGS ====================
    objects = UserManager  # Custom manager'ni ulash

    USERNAME_FIELD = "email"  # Login uchun email. Login qilishda email so'raladi, username emas
    REQUIRED_FIELDS = []  # createsuperuser'da so'ralmaydigan fieldlar, 

    # ==================== META ====================
    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-date_joined"]
        db_table = "users"

        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["date_joined"]),
        ]

    # ==================== METODLAR ====================
    def __str__(self):
        """
        User'ni string sifatida ko'rsatish
        Admin panelda va shellda
        """
        return self.email

    def get_full_name(self):
        """
        To'liq ismni qaytarish

        Returns:
            str: "John Doe" yoki email
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email

    def get_short_name(self):
        """
        Qisqa ism

        Returns:
            str: Faqat first_name yoki email
        """
        return self.first_name if self.first_name else self.email
