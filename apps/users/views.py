from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
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
        }, status=status.HTTP_201_OK)
    
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
    
            
