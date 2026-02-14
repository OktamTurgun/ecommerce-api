"""
Order App URL Configuration

Defines API endpoints for order management.
Uses DRF Router for automatic ViewSet routing.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.orders.views import OrderViewSet

app_name = 'orders'

# Create router
router = DefaultRouter()

# Register ViewSets
router.register(r'', OrderViewSet, basename='order')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

"""
Generated URLs:

Orders:
    GET    /api/orders/              - List user's orders
    POST   /api/orders/              - Create order from cart
    GET    /api/orders/{id}/         - Get order detail
    POST   /api/orders/{id}/cancel/  - Cancel order
"""