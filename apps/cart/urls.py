"""
Cart App URL Configuration

Defines API endpoints for shopping cart.
Uses DRF Router for automatic ViewSet routing.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.cart.views import CartViewSet, CartItemViewSet

app_name = "cart"

router = DefaultRouter()

router.register(r'items', CartItemViewSet, basename='cartitem')

urlpatterns = [
    # Cart detail (GET /api/cart/)
    path("", CartViewSet.as_view({"get": "retrieve"}), name="cart-detail"),

    # Clear cart (POST /api/cart/clear/)
    path("clear/", CartViewSet.as_view({"post": "clear"}), name="cart-clear"),

    # Cart items (router handles these)
    path("", include(router.urls)),
]

"""
Generated URLs:

Cart:
    GET    /api/cart/              - Get current cart
    POST   /api/cart/clear/        - Clear cart

Cart Items:
    GET    /api/cart/items/        - List cart items
    POST   /api/cart/items/        - Add item to cart
    GET    /api/cart/items/{id}/   - Get item detail
    PATCH  /api/cart/items/{id}/   - Update quantity
    DELETE /api/cart/items/{id}/   - Remove from cart
"""
