"""
Products App URL Configuration

Defines API endpoints for products and categories.
Uses DRF Router for automatic ViewSet routing.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.views import CategoryViewSet, ProductViewSet

app_name = 'products'

# Create router
router = DefaultRouter()

# Register ViewSets
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

"""
Generated URLs:

Categories:
    GET    /api/products/categories/                - List categories
    POST   /api/products/categories/                - Create category (admin)
    GET    /api/products/categories/{id}/           - Retrieve category
    PUT    /api/products/categories/{id}/           - Update category (admin)
    PATCH  /api/products/categories/{id}/           - Partial update (admin)
    DELETE /api/products/categories/{id}/           - Delete category (admin)
    GET    /api/products/categories/roots/          - Root categories
    GET    /api/products/categories/{id}/products/  - Products in category

Products:
    GET    /api/products/products/                  - List products
    POST   /api/products/products/                  - Create product (admin)
    GET    /api/products/products/{id}/             - Retrieve product
    PUT    /api/products/products/{id}/             - Update product (admin)
    PATCH  /api/products/products/{id}/             - Partial update (admin)
    DELETE /api/products/products/{id}/             - Delete product (admin)
    GET    /api/products/products/featured/         - Featured products
    GET    /api/products/products/in_stock/         - In-stock products
"""