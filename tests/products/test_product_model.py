"""
Tests for Product Model - TDD Approach

Following TDD: Write tests FIRST, then implement the model.
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError


@pytest.mark.django_db
class TestProductModel:
    """Test suite for Product model - TDD approach."""
    
    def test_product_creation(self):
        """Test creating a basic product."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        
        product = Product.objects.create(
            name='iPhone 15 Pro',
            slug='iphone-15-pro',
            description='Latest iPhone',
            price=Decimal('999.99'),
            category=category,
            stock=50
        )
        
        assert product.id is not None
        assert product.name == 'iPhone 15 Pro'
        assert product.price == Decimal('999.99')
        assert product.is_active == True
        assert str(product) == 'iPhone 15 Pro'
    
    def test_product_requires_category(self):
        """Product must have a category."""
        from apps.products.models import Product
        
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name='Test',
                price=Decimal('10.00'),
                category=None
            )
    
    def test_product_slug_auto_generation(self):
        """Slug auto-generates from name."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        product = Product.objects.create(
            name='Samsung Galaxy S24 Ultra',
            price=Decimal('1199.99'),
            category=category
        )
        
        assert product.slug == 'samsung-galaxy-s24-ultra'
    
    def test_product_slug_unique(self):
        """Slugs must be unique."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        Product.objects.create(
            name='Product 1',
            slug='test-slug',
            price=Decimal('10.00'),
            category=category
        )
        
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name='Product 2',
                slug='test-slug',
                price=Decimal('20.00'),
                category=category
            )
    
    def test_product_price_positive(self):
        """Price must be positive."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        product = Product(
            name='Test',
            price=Decimal('-10.00'),
            category=category
        )
        
        with pytest.raises(ValidationError):
            product.full_clean()
    
    def test_product_stock_non_negative(self):
        """Stock cannot be negative."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        
        # Stock = 0 is valid
        product1 = Product.objects.create(
            name='Out of Stock',
            price=Decimal('50.00'),
            category=category,
            stock=0
        )
        assert product1.stock == 0
        
        # Negative stock fails
        product2 = Product(
            name='Invalid',
            price=Decimal('50.00'),
            category=category,
            stock=-5
        )
        
        with pytest.raises(ValidationError):
            product2.full_clean()
    
    def test_product_discount_price(self):
        """Test discount pricing."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        product = Product.objects.create(
            name='Discounted',
            price=Decimal('100.00'),
            discount_price=Decimal('79.99'),
            category=category
        )
        
        assert product.discount_price == Decimal('79.99')
        assert product.has_discount == True
        assert product.get_price() == Decimal('79.99')
        assert product.savings == Decimal('20.01')
    
    def test_product_without_discount(self):
        """Product without discount."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        product = Product.objects.create(
            name='Regular',
            price=Decimal('50.00'),
            category=category
        )
        
        assert product.discount_price is None
        assert product.has_discount == False
        assert product.get_price() == Decimal('50.00')
    
    def test_product_is_in_stock(self):
        """Test stock availability."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        
        in_stock = Product.objects.create(
            name='Available',
            price=Decimal('30.00'),
            category=category,
            stock=10
        )
        
        out = Product.objects.create(
            name='Unavailable',
            price=Decimal('30.00'),
            category=category,
            stock=0
        )
        
        assert in_stock.is_in_stock == True
        assert out.is_in_stock == False
    
    def test_product_sku_unique(self):
        """SKU must be unique if provided."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        
        Product.objects.create(
            name='Product 1',
            price=Decimal('20.00'),
            category=category,
            sku='IPHONE-15-PRO'
        )
        
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name='Product 2',
                price=Decimal('30.00'),
                category=category,
                sku='IPHONE-15-PRO'
            )
    
    def test_product_active_filtering(self):
        """Filter active/inactive products."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        
        active = Product.objects.create(
            name='Active',
            price=Decimal('30.00'),
            category=category,
            is_active=True
        )
        
        inactive = Product.objects.create(
            name='Inactive',
            price=Decimal('30.00'),
            category=category,
            is_active=False
        )
        
        active_products = Product.objects.filter(is_active=True)
        assert active in active_products
        assert inactive not in active_products
    
    def test_product_is_featured(self):
        """Test featured products."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        
        featured = Product.objects.create(
            name='Featured',
            price=Decimal('100.00'),
            category=category,
            is_featured=True
        )
        
        regular = Product.objects.create(
            name='Regular',
            price=Decimal('50.00'),
            category=category
        )
        
        assert featured.is_featured == True
        assert regular.is_featured == False
    
    def test_product_timestamps(self):
        """Test automatic timestamps."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        from django.utils import timezone
        from datetime import timedelta
        
        category = CategoryFactory()
        product = Product.objects.create(
            name='Test',
            price=Decimal('25.00'),
            category=category
        )
        
        assert product.created_at is not None
        assert product.updated_at is not None
        assert timezone.now() - product.created_at < timedelta(seconds=5)


@pytest.mark.django_db
class TestProductValidation:
    """Test product validation rules."""
    
    def test_discount_less_than_price(self):
        """Discount must be less than price."""
        from apps.products.models import Product
        from tests.factories import CategoryFactory
        
        category = CategoryFactory()
        product = Product(
            name='Invalid',
            price=Decimal('50.00'),
            discount_price=Decimal('60.00'),
            category=category
        )
        
        with pytest.raises(ValidationError):
            product.full_clean()