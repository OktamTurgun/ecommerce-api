from django.db.models import Avg
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

# To'g'ri kesh importi
from django.core.cache import cache
import hashlib

from apps.products.models import Category, Product
from apps.products.serializers import (
    CategorySerializer,
    CategoryListSerializer,
    ProductSerializer,
    ProductListSerializer,
)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Kategoriyalar uchun ViewSet.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'pk'
    
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('parent').prefetch_related('subcategories')
        if self.action == 'list' and 'is_active' not in self.request.query_params:
            queryset = queryset.filter(is_active=True)
        return queryset

class ProductViewSet(viewsets.ModelViewSet):
    """
    Mahsulotlar uchun ViewSet (Redis kesh bilan boyitilgan).
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(is_active=True)\
            .select_related('category')\
            .prefetch_related('images')\
            .annotate(avg_rating=Avg('reviews__rating'))

    def list(self, request, *args, **kwargs):
        """
        Mahsulotlar ro'yxatini keshlash.
        Kalit har bir filtr va sahifa uchun alohida generatsiya qilinadi.
        """
        # So'rov parametrlaridan unikal kesh kaliti yaratish
        query_params = str(request.GET.dict())
        query_hash = hashlib.md5(query_params.encode()).hexdigest()
        cache_key = f"products_list_{query_hash}"
        
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            print(f"🚀 KESHDAN OLINDI: {cache_key}")
            return Response(cached_data)

        print("🐢 BAZADAN OLINMOQDA...")
        response = super().list(request, *args, **kwargs)
        
        # 15 daqiqaga keshga saqlash
        cache.set(cache_key, response.data, 60 * 15)
        return response

    def retrieve(self, request, *args, **kwargs):
        """Mahsulot detali uchun kesh."""
        cache_key = f"product_detail_{kwargs.get('pk')}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            print(f"🚀 DETAL KESHDAN OLINDI: {cache_key}")
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 60) # Detalni 1 soatga saqlash
        return response

    # Ma'lumot o'zgarganda keshni tozalash
    def perform_create(self, serializer):
        serializer.save()
        self._clear_product_cache()

    def perform_update(self, serializer):
        serializer.save()
        self._clear_product_cache()

    def perform_destroy(self, instance):
        instance.delete()
        self._clear_product_cache()

    def _clear_product_cache(self):
        """Mahsulotlar bilan bog'liq barcha keshni o'chirish."""
        cache.clear() # Soddalik uchun barcha keshni tozalaymiz
        print("🧹 KESH TOZALANDI")