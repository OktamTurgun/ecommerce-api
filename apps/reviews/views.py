"""
Review Views

API ViewSets for Review operations.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.reviews.models import Review
from apps.reviews.serializers import (
    ReviewSerializer,
    CreateReviewSerializer,
)
from apps.products.models import Product


class ProductReviewsViewSet(viewsets.ViewSet):
    """
    ViewSet for product reviews.
    
    Endpoints:
    - GET    /api/products/{id}/reviews/     - List product reviews
    - POST   /api/products/{id}/reviews/     - Create review
    
    Permissions:
    - GET: AllowAny
    - POST: IsAuthenticated
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def list(self, request, product_pk=None):
        """
        List all reviews for a product.
        
        Endpoint: GET /api/products/{id}/reviews/
        
        Returns:
            Reviews with average rating and count
        """
        product = get_object_or_404(Product, pk=product_pk)
        reviews = Review.objects.filter(product=product).select_related('user')
        
        # Paginate
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            # Add metadata
            response_data['average_rating'] = product.average_rating
            response_data['review_count'] = product.review_count
            return Response(response_data)
        
        serializer = ReviewSerializer(reviews, many=True)
        return Response({
            'results': serializer.data,
            'average_rating': product.average_rating,
            'review_count': product.review_count,
        })
    
    def create(self, request, product_pk=None):
        """
        Create a review for a product.
        
        Endpoint: POST /api/products/{id}/reviews/
        
        Body:
            {
                "rating": 5,
                "comment": "Great product!"
            }
        
        Returns:
            201 Created with review details
        """
        product = get_object_or_404(Product, pk=product_pk)
        
        serializer = CreateReviewSerializer(
            data=request.data,
            context={'request': request, 'product': product}
        )
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        # Return full review data
        response_serializer = ReviewSerializer(review)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @property
    def paginator(self):
        """Return paginator instance."""
        if not hasattr(self, '_paginator'):
            from rest_framework.pagination import PageNumberPagination
            self._paginator = PageNumberPagination()
            self._paginator.page_size = 10
        return self._paginator
    
    def paginate_queryset(self, queryset):
        """Paginate queryset."""
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get_paginated_response(self, data):
        """Get paginated response."""
        return self.paginator.get_paginated_response(data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review CRUD operations.
    
    Endpoints:
    - GET    /api/reviews/{id}/              - Get review detail
    - PATCH  /api/reviews/{id}/              - Update own review
    - DELETE /api/reviews/{id}/              - Delete own review
    
    Permissions:
    - IsAuthenticated (can only modify own reviews)
    """
    
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Get reviews for current user only.
        
        Returns:
            QuerySet: User's reviews
        """
        return Review.objects.filter(
            user=self.request.user
        ).select_related('user', 'product')
    
    def update(self, request, *args, **kwargs):
        """
        Update review (partial update supported).
        
        Endpoint: PATCH /api/reviews/{id}/
        
        Body:
            {
                "rating": 4,
                "comment": "Updated review"
            }
        """
        partial = kwargs.pop('partial', True)  # Always allow partial
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)