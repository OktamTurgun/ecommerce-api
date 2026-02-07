"""
Base settings - umumiy sozlamalar
"""
from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='change-me-in-production')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = []

# Applications
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',  # API documentation
    
    # Local apps
    'apps.cart',
    'apps.users',
    'apps.products',
    'apps.orders',
    'apps.payments',
    'apps.reviews',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,

    # ============ SWAGGER SETTINGS ============
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),     # 1 soat
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 kun
    'ROTATE_REFRESH_TOKENS': True,                   # Refresh ham yangilanadi
    'BLACKLIST_AFTER_ROTATION': True,                # Eski refresh blacklist'ga
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

# ============ API DOCUMENTATION SETTINGS ============
SPECTACULAR_SETTINGS = {
    'TITLE': 'E-commerce API',
    'DESCRIPTION': '''
    Professional E-commerce REST API built with Django REST Framework.
    
    ## Features
    - User authentication with JWT tokens
    - Email verification system
    - Password reset functionality
    - Profile management
    - Complete user management
    
    ## Authentication
    Use JWT Bearer token authentication:
    1. Register or login to get tokens
    2. Click "Authorize" button above
    3. Enter: Bearer YOUR_ACCESS_TOKEN
    4. Try protected endpoints
    
    ## Getting Started
    1. Register: POST /api/users/register/
    2. Verify email: GET /api/users/verify-email/
    3. Login: POST /api/users/login/
    4. Use access token for authenticated requests
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # Sidebar settings
    'COMPONENT_SPLIT_REQUEST': True,
    
    # Authentication
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Enter: Bearer YOUR_ACCESS_TOKEN'
        }
    },
    
    # Tags (grouping)
    'TAGS': [
        {'name': 'Authentication', 'description': 'User registration, login, logout'},
        {'name': 'Email Verification', 'description': 'Email verification and resend'},
        {'name': 'Profile', 'description': 'User profile management'},
        {'name': 'Password Management', 'description': 'Change, forgot, reset password'},
        {'name': 'Email Management', 'description': 'Change and verify email'},
        {'name': 'Token Management', 'description': 'JWT token refresh'},
        {'name': 'Admin', 'description': 'Admin-only endpoints'},
    ],
    
    # Schema customization
    'SCHEMA_PATH_PREFIX': r'/api',
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    
    # UI settings
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'filter': True,
    },
    
    # Additional settings
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'Bearer': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}