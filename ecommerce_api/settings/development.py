"""
Development settings
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS - Development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
]

# ============ EMAIL SETTINGS ============
# Console backend - Development uchun
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST_USER = 'noreply@ecommerce.local'
DEFAULT_FROM_EMAIL = 'E-commerce <noreply@ecommerce.local>'

# Frontend URL (email link'lar uchun)
FRONTEND_URL = 'http://localhost:3000'

# Token expiry (minutes)
PASSWORD_RESET_TIMEOUT = 60 * 24  # 24 soat
EMAIL_VERIFICATION_TIMEOUT = 60 * 24 * 7  # 7 kun

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}