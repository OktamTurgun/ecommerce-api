from django.shortcuts import render
"""
Product Views

API ViewSets for Category and Product models.
Provides CRUD operations via REST API.
"""

from django.db.models import Q, Avg
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from apps.products.models import Category, Product
from apps.products.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    ProductSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations.
    
    Endpoints:
    - GET    /api/products/categories/          - List categories
    - GET    /api/products/categories/{id}/     - Retrieve category
    - POST   /api/products/categories/          - Create category (Admin)
    - PUT    /api/products/categories/{id}/     - Update category (Admin)
    - PATCH  /api/products/categories/{id}/     - Partial update (Admin)
    - DELETE /api/products/categories/{id}/     - Delete category (Admin)
    
    Permissions:
    - List/Retrieve: Public (no authentication required)
    - Create/Update/Delete: Admin only
    
    Filtering:
    - is_active: Filter by active status
    - parent: Filter by parent category (root or subcategories)
    
    Ordering:
    - name (default alphabetical)
    
    Example:
        GET /api/products/categories/?is_active=true
        GET /api/products/categories/?parent__isnull=true  (root categories)
    """
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'pk'
    
    # Filters
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']  # Default ordering
    
    def get_permissions(self):
        """
        Set permissions based on action.
        
        - List/Retrieve: Public
        - Create/Update/Delete: Admin only
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = []  # Public access
        else:
            permission_classes = [IsAdminUser]  # Admin only
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Customize queryset.
        
        - For list: Only show active categories by default
        - For detail: Show any category
        - Optimize queries with select_related/prefetch_related
        """
        queryset = super().get_queryset()
        
        # Optimize queries
        queryset = queryset.select_related('parent')
        queryset = queryset.prefetch_related('subcategories', 'products')
        
        # For list view: filter active by default (unless explicitly queried)
        if self.action == 'list':
            # If is_active is not in query params, show only active
            if 'is_active' not in self.request.query_params:
                queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        - List: Lightweight serializer
        - Detail/Create/Update: Full serializer
        """
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        """
        Create category.
        
        Slug is auto-generated in model's save method.
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Update category.
        
        Slug is auto-updated if name changes.
        """
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete category.
        
        CASCADE delete will also remove associated products.
        """
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """
        Get all products in this category.
        
        Endpoint: GET /api/products/categories/{id}/products/
        
        Returns:
            List of products in this category
        """
        category = self.get_object()
        products = category.products.filter(is_active=True)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def roots(self, request):
        """
        Get all root categories (no parent).
        
        Endpoint: GET /api/products/categories/roots/
        
        Returns:
            List of root categories
        """
        roots = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations with search and filtering.
    
    Features:
    - Search: ?search=query (searches name and description)
    - Filter by category: ?category=uuid
    - Filter by price range: ?min_price=X&max_price=Y
    - Filter by rating: ?min_rating=X
    - Sort: ?ordering=price/-price/name/-created_at
    - Combined filters supported
    
    Examples:
        GET /api/products/products/?search=iphone
        GET /api/products/products/?category=uuid&min_price=500&max_price=1000
        GET /api/products/products/?min_rating=4&ordering=-price
    """
    
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    # Enable filters
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    
    # Search fields
    search_fields = ['name', 'description']
    
    # Ordering fields
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """
        Get queryset with filters applied.
        
        Filters:
        - category: Filter by category ID
        - min_price: Minimum price
        - max_price: Maximum price
        - min_rating: Minimum average rating
        """
        queryset = Product.objects.filter(is_active=True)
        
        # Optimize queries
        queryset = queryset.select_related('category')
        queryset = queryset.prefetch_related('images')
        
        # Annotate with average rating
        queryset = queryset.annotate(
            avg_rating=Avg('reviews__rating')
        )
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Price range filters
        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Rating filter
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=min_rating)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions.
        
        - List: Lightweight serializer
        - Detail/Create/Update: Full serializer
        """
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        """
        Create product.
        
        Slug is auto-generated in model's save method.
        """
        serializer.save()
    
    def perform_update(self, serializer):
        """
        Update product.
        
        Slug is auto-updated if name changes.
        """
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete product.
        """
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products.
        
        Endpoint: GET /api/products/featured/
        
        Returns:
            List of featured products
        """
        featured = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """
        Get products that are in stock.
        
        Endpoint: GET /api/products/in_stock/
        
        Returns:
            List of products with stock > 0
        """
        in_stock = self.get_queryset().filter(stock__gt=0)
        serializer = self.get_serializer(in_stock, many=True)
        return Response(serializer.data)