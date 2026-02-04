from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ==================== REGISTRATION ====================
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "email", "password", "password2", "first_name", "last_name", "phone_number"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan!")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Parollar bir xil emas!"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            email=validated_data.get("email"),
            password=validated_data.get("password"),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", "")
        )
        return user

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "Ro'yxatdan o'tish muvaffaqiyatli. Verification code yuborildi",
            "data": {
                "user_id": str(instance.id),
                "email": instance.email,
                "full_name": instance.get_full_name(),
                "phone_number": instance.phone_number,
                "auth_status": getattr(instance, "auth_status", "new"),
            }
        }


# ==================== LOGIN ====================
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Bu email ro'yxatdan o'tmagan!"})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Parol noto'g'ri"})

        if not user.is_active:
            raise serializers.ValidationError({"email": "Akkount faol emas"})

        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        user = instance.get("user")
        tokens = RefreshToken.for_user(user)
        return {
            "success": True,
            "message": "Login muvaffaqiyatli",
            "data": {
                "user_id": str(user.id),
                "email": user.email,
                "full_name": user.get_full_name(),
                "tokens": {
                    "access": str(tokens.access_token),
                    "refresh": str(tokens),
                }
            }
        }


# ==================== PROFILE ====================
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "phone_number", "address", "city", "country", "postal_code",
            "date_joined", "is_active"
        ]
        read_only_fields = ["id", "email", "date_joined", "is_active"]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "User profile",
            "data": super().to_representation(instance)
        }


# ==================== CHANGE PASSWORD ====================
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"}, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri!")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Yangi parollar bir xil emas!"})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "Parol muvaffaqiyatli yangilandi"
        }


# ==================== FORGOT PASSWORD ====================
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "Agar email mavjud bo'lsa, sizga tiklash link yuborildi"
        }


# ==================== RESET PASSWORD ====================
class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Parollar bir xil emas!"})
        return attrs

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "Parol muvaffaqiyatli tiklandi"
        }


# ==================== EMAIL CHANGE ====================
class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_new_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email allaqochon ishlatilmoqda!")
        return value

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Parol noto'g'ri!")
        return value

    def to_representation(self, instance):
        return {
            "success": True,
            "message": f"Email o'zgarishi so'rovi qabul qilindi: {instance.get('new_email', '')}"
        }


# ==================== VERIFY EMAIL CHANGE ====================
class VerifyEmailChangeSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        return value.lower()

    def to_representation(self, instance):
        return {
            "success": True,
            "message": "Email muvaffaqiyatli tasdiqlandi",
            "data": {"new_email": instance.get("new_email")}
        }
