from django.conf import settings
from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    ForgotPasswordSerializer,
    ResendVerificationSerializer,
    ResetPasswordSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ChangeEmailSerializer,
    VerifyEmailChangeSerializer,
)

from core.emails import (
    send_password_reset_email,
    send_verification_email,
    send_email_change_verification,
)

from core.utils import (
    account_activation_token,
    encode_uid,
    get_user_from_uid,
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    POST /api/users/register/

    Yangi user ro'yxatdan o'tkazish

    Permissions:
    - AllowAny (hamma uchun ochiq)

    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123!",
        "password2": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe"
    }

    Response: 201 Created
    {
        "user": {...user data...},
        "tokens": {
            "access": "...",
            "refresh": "..."
        },
        "message": "Ro'yxatdan o'tish muvaffaqiyatli!"
    }
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwarks):
        """
        User yaratish va token qaytarish

        Steps:
        1. Serialize data
        2. Validate
        3. Create user
        4. Generate JWT tokens
        5. Return response with user + tokens
        """
        # 1. Serializer bilan validatsiya
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. User yaratish
        user = serializer.save()

        # 3. JWT Token yaratish
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "message": "Ro'yxatdan o'tish muvaffaqiyatli!",
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    """
    POST /api/users/login/

    User login qilish va JWT token olish

    Permissions:
    - AllowAny

    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }

    Response: 200 OK
    {
        "user": {...user data...},
        "tokens": {
            "access": "...",
            "refresh": "..."
        },
        "message": "Login muvaffaqiyatli!"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Login va token qaytarish
        
        Steps:
        1. Validate credentials
        2. Get authenticated user
        3. Generate tokens
        4. Return response
        """
        # 1. Serializers bilan validatsiya
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Authenticated user olish
        user = serializer.validated_data['user']

        # 3. JWT Token yaratish
        refresh = RefreshToken.for_user(user)

        # 4. Response
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': "Login muvaffaqiyatli!"
        }, status=status.HTTP_200_OK)
    
class UserLogoutView(APIView):
    """
    POST /api/users/logout/
    
    User logout qilish (refresh token'ni blacklist qilish)
    
    Permissions:
    - IsAuthenticated (faqat login qilgan userlar)
    
    Request body:
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJh..."
    }
    
    Response: 200 OK
    {
        "message": "Logout muvaffaqiyatli!"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Logout - refresh token'ni bekor qilish
        
        Steps:
        1. Get refresh token from request
        2. Blacklist token
        3. Return success message
        """
        try:
            # 1. Refresh token olish
            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response({
                    'error': 'Refresh token majburiy!'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. Token'ni balacklist qilish
            token = RefreshToken(refresh_token)
            token.blacklist()

            # 3. Success response
            return Response({
                'message': 'Logout muvaffaqiyatli!'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': "Token noto'g'ri yoki allaqachon bekor qilingan!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/users/profile/      - Profil ko'rish
    PUT /api/users/profile/      - To'liq yangilash
    PATCH /api/users/profile/    - Qisman yangilash
    
    Permissions:
    - IsAuthenticated (faqat login qilgan userlar)
    
    Response: 200 OK
    {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "phone": "+998901234567",
        "address": "Tashkent",
        ...
    }
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Hozirgi authenticated user'ni qaytarish
        
        Bu metod DRF tomonidan avtomatik chaqiriladi
        get_object() -> Qaysi obyektni ko'rsatish/yangilash?
        
        Returns:
            Current authenticated user
        """
        return self.request.user
    
class ChangePasswordView(APIView):
    """
    POST /api/users/change-password/
    
    Hozirgi parolni o'zgartirish
    
    Permissions:
    - IsAuthenticated
    
    Request body:
    {
        "old_password": "OldPass123!",
        "new_password": "NewPass123!",
        "new_password2": "NewPass123!"
    }
    
    Response: 200 OK
    {
        "message": "Parol muvaffaqiyatli o'zgartirildi!"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Parolni o'zgartirish
        
        Steps:
        1. Validate old password
        2. Validate new passwords match
        3. Save new password
        4. Return success
        """
        # 1. Serializer (context'ga request berishi kerak!)
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )

        # 2. Validatsiya
        serializer.is_valid(raise_exception=True)

        # 3. Saqlash
        serializer.save()

        # 4. Success response
        return Response({
            'message': "Parol muvaffaqiyatli o'zgartirildi!"
        }, status=status.HTTP_200_OK)
    
class UserListView(generics.ListAPIView):
    """
    GET /api/users/
    
    Barcha userlarni ko'rish (faqat admin)
    
    Permissions:
    - IsAdminUser (faqat admin)
    
    Query params:
    - page: Page number
    - page_size: Items per page
    - search: Search by email, name
    
    Response: 200 OK
    {
        "count": 100,
        "next": "http://api.example.com/users/?page=2",
        "previous": null,
        "results": [
            {user1},
            {user2},
            ...
        ]
    }
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permisson_classes = [permissions.IsAuthenticated]

# ============ PASSWORD RESET VIEWS ============
class ForgotPasswordView(APIView):
    """
    POST /api/users/forgot-password/
    
    Parolni tiklash uchun email yuborish
    
    Permissions:
    - AllowAny (hamma uchun)
    
    Request:
    {
        "email": "user@example.com"
    }
    
    Response: 200 OK
    {
        "message": "Agar email ro'yxatdan o'tgan bo'lsa, parolni tiklash uchun ko'rsatmalar yuborildi."
    }
    
    Security Note:
    - Email mavjud yoki yo'qligini aytmaymiz (security)
    - Har doim 200 OK qaytaramiz
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Password reset email yuborish
        """
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            # User topish
            user = User.objects.get(email=email)
            
            # Token yaratish
            token = account_activation_token.make_token(user)
            uidb64 = encode_uid(user)
            
            # Reset URL yaratish
            # Frontend URL (React, Vue, etc)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uidb64}&token={token}"
            
            # Email yuborish
            send_password_reset_email(user, reset_url)
            
        except User.DoesNotExist:
            # Security: User yo'qligini aytmaymiz
            pass
        
        # Har doim success message (security)
        return Response({
            'message': 'Agar email ro\'yxatdan o\'tgan bo\'lsa, parolni tiklash uchun ko\'rsatmalar yuborildi.'
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    POST /api/users/reset-password/
    
    Yangi parol o'rnatish
    
    Permissions:
    - AllowAny
    
    Request:
    {
        "uidb64": "MQ",
        "token": "abc123...",
        "new_password": "NewPass123!",
        "new_password2": "NewPass123!"
    }
    
    Response: 200 OK
    {
        "message": "Parol muvaffaqiyatli o'zgartirildi!"
    }
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Token tekshirish va yangi parol o'rnatish
        """
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Data olish
        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # User olish
        user = get_user_from_uid(uidb64)
        
        if not user:
            return Response({
                'error': 'Noto\'g\'ri link!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Token tekshirish
        if not account_activation_token.check_token(user, token):
            return Response({
                'error': 'Link muddati o\'tgan yoki noto\'g\'ri!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Yangi parolni o'rnatish
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Parol muvaffaqiyatli o\'zgartirildi! Endi login qilishingiz mumkin.'
        }, status=status.HTTP_200_OK)

# ============ EMAIL VERIFICATION VIEWS ============

class VerifyEmailView(APIView):
    """
    GET /api/users/verify-email/
    
    Email manzilni tasdiqlash
    
    Permissions:
    - AllowAny
    
    Query params:
    - uid: Encoded user ID
    - token: Verification token
    
    Example:
    GET /api/users/verify-email/?uid=MQ&token=abc123
    
    Response: 200 OK
    {
        "message": "Email muvaffaqiyatli tasdiqlandi!"
    }
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Email verification link'ni tekshirish
        """
        # Query params'dan olish
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')
        
        if not uidb64 or not token:
            return Response({
                'error': 'UID va token majburiy!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # User olish
        user = get_user_from_uid(uidb64)
        
        if not user:
            return Response({
                'error': 'Noto\'g\'ri link!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Allaqachon verified?
        if user.is_active:
            return Response({
                'message': 'Email allaqachon tasdiqlangan!'
            }, status=status.HTTP_200_OK)
        
        # Token tekshirish
        if not account_activation_token.check_token(user, token):
            return Response({
                'error': 'Link muddati o\'tgan yoki noto\'g\'ri!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Email'ni tasdiqlash
        user.is_active = True
        user.save()
        
        return Response({
            'message': 'Email muvaffaqiyatli tasdiqlandi! Endi login qilishingiz mumkin.'
        }, status=status.HTTP_200_OK)


class ResendVerificationView(APIView):
    """
    POST /api/users/resend-verification/
    
    Verification email'ni qayta yuborish
    
    Permissions:
    - AllowAny
    
    Request:
    {
        "email": "user@example.com"
    }
    
    Response: 200 OK
    {
        "message": "Agar email ro'yxatdan o'tgan bo'lsa, tasdiqlash linki yuborildi."
    }
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Verification email qayta yuborish
        """
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Allaqachon verified?
            if user.is_active:
                return Response({
                    'message': 'Email allaqachon tasdiqlangan!'
                }, status=status.HTTP_200_OK)
            
            # Token yaratish
            token = account_activation_token.make_token(user)
            uidb64 = encode_uid(user)
            
            # Verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?uid={uidb64}&token={token}"
            
            # Email yuborish
            send_verification_email(user, verification_url)
            
        except User.DoesNotExist:
            # Security: User yo'qligini aytmaymiz
            pass
        
        return Response({
            'message': 'Agar email ro\'yxatdan o\'tgan bo\'lsa, tasdiqlash linki yuborildi.'
        }, status=status.HTTP_200_OK)
    
# ============ EMAIL CHANGE VIEWS ============
class ChangeEmailView(APIView):
    """
    POST /api/users/change-email/
    
    Email o'zgartirish so'rovi yuborish
    
    Permissions:
    - IsAuthenticated
    
    Request:
    {
        "new_email": "newemail@example.com",
        "password": "CurrentPass123!"
    }
    
    Response: 200 OK
    {
        "message": "Tasdiqlash linki yangi email manzilingizga yuborildi."
    }
    
    Workflow:
    1. User yangi email va parol yuboradi
    2. Parol tekshiriladi
    3. Yangi email'ga verification link yuboriladi
    4. User link'ni bosadi
    5. Email o'zgaradi
    """
    permisson_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Email o'zgartirish so'rovi
        """
        serializer = ChangeEmailSerializer(
            data=request.data,
            contect={'request': request}
        )  
        serializer.is_vlaid(reise_exception=True)

        user = request.user
        new_email = serializer.validated_data['new_email']

        # Token yaratish
        token = account_activation_token.make_token(user)
        uidb64 = encode_uid(user)  

        # Verification URL
        # URL'da yangi email ham ketadi (tasdiqlash uchun)
        verification_url = (
            f"{settings.FRONTEND_URL}/vrify_email_change?"
            f"uid={uidb64}&token={token}&email={new_email}"
        )

        # Yangi email'ga verification link yuborish
        send_email_change_verification(user, new_email, verification_url)

        return Response({
            'message': 'Tasdiqlash linki yangi email manzilingizga yuborildi. '
                      'Linkni bosib, email o\'zgarishini tasdiqlang.'
        }, status=status.HTTP_200_OK)

class VerifyEmailChangeView(APIView):
    """
    POST /api/users/verify-email-change/
    
    Email o'zgarishini tasdiqlash
    
    Permissions:
    - AllowAny (token'dan user topiladi)
    
    Request:
    {
        "uidb64": "MQ",
        "token": "abc123...",
        "new_email": "newemail@example.com"
    }
    
    Response: 200 OK
    {
        "message": "Email muvaffaqiyatli o'zgartirildi!"
    }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Token tekshirish va email'ni yangilash
        """
        serializer = VerifyEmailChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        new_email = serializer.validated_data['new_email']

        # User olish
        user = get_user_from_uid(uidb64)

        if not user:
            return Response({
                'error': "Noto'g'ri link!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Token tekshirish
        if not account_activation_token.check_token(user, token):
            return Response({
                'error': "Link muddati o'tgan yoki noto'g'ri!"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Email allaqachon ishlatilayotganmi? (race condition)
        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            return Response({
                'error': 'Bu email allaqachon ishlamoqda!'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Email'ni yangilash
        user.email = new_email
        user.save()

        return Response({
            'message': "Email muvaffaqiyatli o'zgartirildi "
                        "Keyingi loginda yangi email ishlatishingiz mumkin."
        }, status=status.HTTP_200_OK)
