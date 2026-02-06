from django.conf import settings
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ResendVerificationSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    VerifyEmailChangeSerializer,
    UserSerializer,
)
from .services.auth_service import AuthService
from .services.password_service import PasswordService, User
from .services.verification_service import VerificationService
from .services.email_service import EmailService
from .services.token_service import TokenService
from core.utils import get_user_from_uid

# --------------------------
# Registration / Login
# --------------------------
class UserRegistrationView(APIView):
    """Yangi user ro'yxatdan o'tkazish"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, tokens = AuthService.register_user(**serializer.validated_data)

        return Response({
            "user": UserSerializer(user).data,
            "tokens": tokens,
            "message": "Ro'yxatdan o'tish muvaffaqiyatli!"
        }, status=status.HTTP_201_CREATED)


# apps/users/views.py

class UserLoginView(APIView):
    """User login va JWT token olish"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user, tokens = AuthService.login_user(email, password)
        if not user:
            return Response({"error": "Email yoki parol noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)

        # QOSHILDI: Update last_login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response({
            "user": UserSerializer(user).data,
            "tokens": tokens,
            "message": "Login muvaffaqiyatli!"
        })


class UserLogoutView(APIView):
    """User logout qilish (refresh token blacklist qilish)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token majburiy!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            TokenService.blacklist_token(refresh_token)
        except Exception:
            return Response({"error": "Token noto'g'ri yoki allaqachon bekor qilingan!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Logout muvaffaqiyatli!"})


# --------------------------
# Profile
# --------------------------
class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profilini ko'rish va yangilash"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# --------------------------
# Password Management
# --------------------------
class ChangePasswordView(APIView):
    """Hozirgi parolni o'zgartirish"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        PasswordService.change_password(
            user=request.user,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password']
        )

        return Response({"message": "Parol muvaffaqiyatli o'zgartirildi!"})

class ForgotPasswordView(APIView):
    """Parolni tiklash uchun email yuborish"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = AuthService.get_user_by_email(email)
            token, uidb64 = AuthService.generate_password_reset(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uidb64}&token={token}"
            EmailService.send_password_reset(user, reset_url)
        except Exception:
            pass  # Security: user mavjudligini oshkor qilmaymiz

        return Response({"message": "Agar email ro'yxatdan o'tgan bo'lsa, parolni tiklash uchun ko'rsatmalar yuborildi."})
    
# class ResetPasswordView(APIView):
#     """Yangi parol o'rnatish"""
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = ResetPasswordSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         uidb64 = serializer.validated_data['uidb64']
#         token = serializer.validated_data['token']
#         new_password = serializer.validated_data['new_password']

#         user = get_user_from_uid(uidb64)
#         if not user:
#             return Response({"error": "Noto'g'ri link!"}, status=status.HTTP_400_BAD_REQUEST)

#         if not VerificationService.verify_email(user, token):
#             return Response({"error": "Link muddati o'tgan yoki noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)
        

#         PasswordService.reset_password(user, new_password)

#         return Response({"message": "Parol muvaffaqiyatli o'zgartirildi! Endi login qilishingiz mumkin."})
    
class ResetPasswordView(APIView):
    """Yangi parol o'rnatish"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        user = get_user_from_uid(uidb64)
        if not user:
            return Response({"error": "Noto'g'ri link!"}, status=status.HTTP_400_BAD_REQUEST)

        # TO'G'RILANDI: Password reset tokenini tekshirish
        if not AuthService.verify_password_reset_token(user, token):
            return Response({"error": "Link muddati o'tgan yoki noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)

        PasswordService.reset_password(user, new_password)

        return Response({"message": "Parol muvaffaqiyatli o'zgartirildi! Endi login qilishingiz mumkin."})


# --------------------------
# Email Verification
# --------------------------
class VerifyEmailView(APIView):
    """
    Email verification - LINK va CODE ikkalasini ham qo'llab-quvvatlaydi
    
    GET  /api/users/verify-email/?uid=...&token=...  (LINK uchun)
    POST /api/users/verify-email/  Body: {"code": "123456"}  (CODE uchun)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        LINK-based email verification
        Email'dagi linkni bosganda
        """
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')
        
        if not uidb64 or not token:
            return Response({
                "error": "UID va token majburiy!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_user_from_uid(uidb64)
        if not user:
            return Response({
                "error": "Noto'g'ri link!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_active:
            return Response({
                "message": "Email allaqachon tasdiqlangan!"
            })
        
        if not VerificationService.verify_email(user, token):
            return Response({
                "error": "Link muddati o'tgan yoki noto'g'ri!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "message": "Email muvaffaqiyatli tasdiqlandi! Endi login qilishingiz mumkin."
        })
    
    def post(self, request):
        """
        CODE-based email verification
        Body'da code yuboriladi
        """
        # 1. User authenticated bo'lishi kerak
        if not request.user.is_authenticated:
            return Response({
                "error": "Authentication talab qilinadi!"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # 2. Code olish
        code = request.data.get('code')
        
        if not code:
            return Response({
                "error": "Code majburiy!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Code tekshirish
        success, message = VerificationService.verify_email_code(
            user=request.user,
            code=code
        )
        
        # 4. Response
        if success:
            return Response({
                "message": message,
                "email_verified": True
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": message
            }, status=status.HTTP_400_BAD_REQUEST)
    
class ResendVerificationView(APIView):
    """Verification email'ni qayta yuborish"""
    permission_classes = [AllowAny]

    def post(self, request):
        # TO'G'RILANDI: Endi to'g'ri serializer ishlatiladi
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = AuthService.get_user_by_email(email)
            VerificationService.send_email_verification(user)
        except Exception:
            pass  # Security

        return Response({"message": "Agar email ro'yxatdan o'tgan bo'lsa, tasdiqlash linki yuborildi."})


# --------------------------
# Email Change
# --------------------------
class ChangeEmailView(APIView):
    """Email o'zgartirish so'rovi yuborish"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeEmailSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_email = serializer.validated_data['new_email']

        VerificationService.send_email_change_verification(user, new_email)

        return Response({"message": "Tasdiqlash linki yangi email manzilingizga yuborildi."})


class VerifyEmailChangeView(APIView):
    """Email o'zgarishini tasdiqlash"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_email = serializer.validated_data['new_email']

        user = get_user_from_uid(uidb64)
        if not user:
            return Response({"error": "Noto'g'ri link!"}, status=status.HTTP_400_BAD_REQUEST)

        if not VerificationService.verify_email(user, token):
            return Response({"error": "Link muddati o'tgan yoki noto'g'ri!"}, status=status.HTTP_400_BAD_REQUEST)

        if AuthService.is_email_taken(new_email, exclude_user=user):
            return Response({"error": "Bu email allaqachon ishlamoqda!"}, status=status.HTTP_400_BAD_REQUEST)

        AuthService.update_email(user, new_email)

        return Response({"message": "Email muvaffaqiyatli o'zgartirildi! Keyingi loginda yangi email ishlatishingiz mumkin."})

class UserListView(generics.ListAPIView):
    """Barcha userlarni ko'rsatish (faqat admin uchun)"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]