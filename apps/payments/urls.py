"""
Payment App URL Configuration

Defines API endpoints for payment processing.
Uses DRF Router for automatic ViewSet routing.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.payments.views import PaymentViewSet

app_name = 'payments'

# Create router
router = DefaultRouter()

# Register ViewSets
router.register(r'', PaymentViewSet, basename='payment')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

"""
Generated URLs:

Payments:
    GET    /api/payments/                   - List user's payments
    GET    /api/payments/{id}/              - Get payment detail
    POST   /api/payments/create-intent/     - Create payment intent
    POST   /api/payments/confirm/           - Confirm payment
"""