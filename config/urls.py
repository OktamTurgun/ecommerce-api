from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),

    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name='schema'),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("api/redoc/", SpectacularSwaggerView.as_view(url_name='schema'), name='redoc'),

    # JWT Token endpoints
    path("api/token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),

    # API-v1 endpoints
    path("api/users/", include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),  # Includes nested reviews
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/reviews/', include('apps.reviews.urls')),
]

# Media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


## Complete URL Mapping
"""
═══════════════════════════════════════════════════════════════
ADMIN PANEL
═══════════════════════════════════════════════════════════════
/admin/                                    → Django Admin Panel

═══════════════════════════════════════════════════════════════
API DOCUMENTATION
═══════════════════════════════════════════════════════════════
/api/schema/                               → OpenAPI Schema (JSON)
/api/docs/                                 → Swagger UI (Interactive API Docs)
/api/redoc/                                → ReDoc (Alternative API Docs)

═══════════════════════════════════════════════════════════════
AUTHENTICATION (JWT)
═══════════════════════════════════════════════════════════════
/api/token/refresh/                        → Refresh JWT Token

═══════════════════════════════════════════════════════════════
USERS API
═══════════════════════════════════════════════════════════════
/api/users/register/                       → User Registration
/api/users/login/                          → User Login
/api/users/logout/                         → User Logout
/api/users/profile/                        → User Profile (GET, PATCH)
/api/users/change-password/                → Change Password
/api/users/                                → User List (Admin only)

═══════════════════════════════════════════════════════════════
PRODUCTS API
═══════════════════════════════════════════════════════════════
GET    /api/products/categories/           → List all categories
POST   /api/products/categories/           → Create category (Admin)
GET    /api/products/categories/{id}/      → Category detail
PATCH  /api/products/categories/{id}/      → Update category (Admin)
DELETE /api/products/categories/{id}/      → Delete category (Admin)

GET    /api/products/products/             → List all products
POST   /api/products/products/             → Create product (Admin)
GET    /api/products/products/{id}/        → Product detail
PATCH  /api/products/products/{id}/        → Update product (Admin)
DELETE /api/products/products/{id}/        → Delete product (Admin)

GET    /api/products/products/{id}/images/ → List product images
POST   /api/products/products/{id}/images/ → Add product image (Admin)
DELETE /api/products/images/{id}/          → Delete product image (Admin)

GET    /api/products/{id}/reviews/         → List product reviews ⭐ NEW!
POST   /api/products/{id}/reviews/         → Create review ⭐ NEW!

═══════════════════════════════════════════════════════════════
CART API
═══════════════════════════════════════════════════════════════
GET    /api/cart/                          → Get current cart
POST   /api/cart/clear/                    → Clear cart
GET    /api/cart/items/                    → List cart items
POST   /api/cart/items/                    → Add item to cart
GET    /api/cart/items/{id}/               → Cart item detail
PATCH  /api/cart/items/{id}/               → Update cart item quantity
DELETE /api/cart/items/{id}/               → Remove item from cart

═══════════════════════════════════════════════════════════════
ORDERS API
═══════════════════════════════════════════════════════════════
GET    /api/orders/                        → List user's orders
POST   /api/orders/                        → Create order from cart
GET    /api/orders/{id}/                   → Get order detail
POST   /api/orders/{id}/cancel/            → Cancel order

═══════════════════════════════════════════════════════════════
PAYMENTS API
═══════════════════════════════════════════════════════════════
GET    /api/payments/                      → List user's payments
GET    /api/payments/{id}/                 → Get payment detail
POST   /api/payments/create-intent/        → Create Stripe payment intent
POST   /api/payments/confirm/              → Confirm payment

═══════════════════════════════════════════════════════════════
REVIEWS API ⭐ NEW!
═══════════════════════════════════════════════════════════════
GET    /api/reviews/                       → List user's reviews
GET    /api/reviews/{id}/                  → Get review detail
PATCH  /api/reviews/{id}/                  → Update own review
DELETE /api/reviews/{id}/                  → Delete own review

Note: Product reviews are also available via nested route:
      GET/POST /api/products/{id}/reviews/

═══════════════════════════════════════════════════════════════
MEDIA FILES (Development Only)
═══════════════════════════════════════════════════════════════
/media/{path}                              → Uploaded media files

═══════════════════════════════════════════════════════════════
TOTAL ENDPOINTS: 40+
═══════════════════════════════════════════════════════════════
"""

## 🎯 Key Points

### Nested vs Direct Routes
"""
**Reviews can be accessed two ways:**

1. **Nested** (recommended for listing/creating):
```
   GET  /api/products/{product_id}/reviews/
   POST /api/products/{product_id}/reviews/
```

2. **Direct** (for managing own reviews):
```
   GET    /api/reviews/
   GET    /api/reviews/{review_id}/
   PATCH  /api/reviews/{review_id}/
   DELETE /api/reviews/{review_id}/
```
"""