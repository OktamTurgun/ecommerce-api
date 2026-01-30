from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Yangi user ro'yxatdan o'tkazish uchun serializer

      Features:
        - Password validation (min 8 char, etc)
        - Password confirmation check
        - Secure password storage (hashed)
        - Email uniqueness check
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
        help_text="Kamida 8 ta belgi, harflar va raqamlar",
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="Parolni tasdiqlash",
        style={"input_type": "password"},
        help_text="Yuqoridagi parolni qayta kiriting",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "phone",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "email": {"required": True, "help_text": "Active email manzil"},
            "first_name": {"required": False, "help_text": "Ismingiz"},
        }

    def validate_email(self, value):
        """
        Email uniqueness check

        Args:
            value: email address

        Returns:
            Lowercase email

        Raises:
            ValidationError: agar email allaqachon mavjud bo'lsa
        """
        value = value.lower()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Bu email allaqachon ro'yxatdan o'tgan!"
            )
        return value

    def validate(self, attrs):
        """
        Barcha fieldlarni validatsiya qilish

        Bu metod barcha validate_<field> metodlaridan keyin ishlaydi

        Args:
            attrs: Barcha cleaned data

        Returns:
            Validated attrs
        """
        # Password confirmation check
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Parollar bir xil emas!"}
            )
        return attrs

    def create(self, validated_data):
        """
        Yangi user yaratish

        Args:
            validated_data: Tekshirilgan ma'lumotlar

        Returns:
            Yangi User obyekti
        """
        validated_data.pop("password2")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    User login qilish uchun

    Faqat email va password qabul qiladi
    Model bilan bog'lanmagan (Serializer, ModelSerializer emas)
    """

    email = serializers.EmailField(
        required=True,
        help_text="Ro'yxatdan o'tgan email",
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        help_text="Parolingiz",
    )

    def validate(self, attrs):
        """
        Email va password to'g'riligini tekshirish

        Returns:
            attrs with 'user' key
        """
        email = attrs.get("email", "").lower()
        password = attrs.get("password")

        # 1. User borligini tekshirish
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "Bu email ro'yxatdan o'tmagan!"}
            )

        # 2. Password to'g'riligini tekshirish
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Parol noto\'g\'ri'
            })
        
        # 3. User active ekanligini tekshirish
        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'Bu akkount faol emas! Admin bilan bog\'laning.'
            })
        
        attrs['user'] = user
        return attrs

class UserSerializer(serializers.ModelSerializer):
    """
      User profil ma'lumotlari uchun
      
      Ishlatiladi:
      - GET /api/users/profile/ - ko'rish
      - PUT/PATCH /api/users/profile/ - yangilash
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'address',
            'city',
            'country',
            'postal_code',
            'date_joined',
            'is_active',
        ]
        read_only_fields = [
            'id',
            'email',
            'date_joined',
            'is_active',
        ]

    def get_full_name(self, obj):
        """
          Custom field - full_name
          
          Args:
              obj: User instance
          
          Returns:
              "John Doe" yoki email
        """
        return obj.get_full_name()
    
class ChangePasswordSerializer(serializers.Serializer):
    """
      Parolni o'zgartirish uchun
      
      3 ta field:
      - old_password: Hozirgi parol (verification)
      - new_password: Yangi parol
      - new_password2: Yangi parol tasdiqlash
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Hozirgi parol',
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        validators=[validate_password],
        help_text='Yangi parol (min 8 char)',
    )

    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Yangi parolni tasdiqlang'
    )

    def validate_old_password(self, value):
        """
            Eski parolni tekshirish
        """
        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                "Eski parol noto'g'ri!"
            )
        return value
    def validate(self, attrs):
        """
          Yangi parollar bir xilligini tekshirish
        """
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password2': 'Yangi parollar bir xil emas!'
            })
        return attrs
    
    def save(self, **kwargs):
        """
          Yangi parolni saqlash
          
          Returns:
              Updated user
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
    
class UserTokenSerializer(serializers.Serializer):
    """
      Login/Register response uchun
      
      User + Tokens birga qaytariladi
    """
    user = UserSerializer()
    tokens = serializers.DictField()
    message = serializers.CharField()
