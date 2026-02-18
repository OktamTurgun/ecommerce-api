"""
Review App URL Configuration

Defines API endpoints for review management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.reviews.views import ReviewViewSet

app_name = 'reviews'

# Create router
router = DefaultRouter()

# Register ViewSets
router.register(r'', ReviewViewSet, basename='review')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]

"""
Generated URLs:

Reviews:
    GET    /api/reviews/              - List user's reviews
    GET    /api/reviews/{id}/         - Get review detail
    PATCH  /api/reviews/{id}/         - Update own review
    DELETE /api/reviews/{id}/         - Delete own review
"""