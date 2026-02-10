from django.shortcuts import render
"""
Product Views

API ViewSets for Category and Product models.
Provides CRUD operations via REST API.
"""
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
    ViewSet for Product CRUD operations.
    
    Endpoints:
    - GET    /api/products/                - List products
    - GET    /api/products/{id}/           - Retrieve product
    - POST   /api/products/                - Create product (Admin)
    - PUT    /api/products/{id}/           - Update product (Admin)
    - PATCH  /api/products/{id}/           - Partial update (Admin)
    - DELETE /api/products/{id}/           - Delete product (Admin)
    
    Permissions:
    - List/Retrieve: Public
    - Create/Update/Delete: Admin only
    
    Filtering:
    - category: Filter by category ID
    - is_active: Filter by active status
    - is_featured: Filter featured products
    - price_min: Minimum price
    - price_max: Maximum price
    
    Search:
    - name, description, sku
    
    Ordering:
    - name, price, created_at (default: newest first)
    
    Example:
        GET /api/products/?category={category_id}
        GET /api/products/?is_featured=true
        GET /api/products/?price_min=100&price_max=500
        GET /api/products/?search=iphone
    """
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    
    # Filters
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'stock']
    ordering = ['-created_at']  # Default: newest first
    
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
        
        - For list: Only show active products by default
        - Optimize queries with select_related
        - Support price range filtering
        """
        queryset = super().get_queryset()
        
        # Optimize queries
        queryset = queryset.select_related('category')
        
        # For list view: filter active by default
        if self.action == 'list':
            if 'is_active' not in self.request.query_params:
                queryset = queryset.filter(is_active=True)
        
        # Price range filtering
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        
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