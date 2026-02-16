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
    path('api/products/', include('apps.products.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),

    # TODO: Keyingi app
    # path('api/reviews/', include('apps.reviews.urls')),
]

# Media files (development only)
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

## URL Mapping
"""
/api/users/register/         → UserRegistrationView
/api/users/login/            → UserLoginView
/api/users/logout/           → UserLogoutView
/api/users/profile/          → UserProfileView
/api/users/change-password/  → ChangePasswordView
/api/users/                  → UserListView
"""


