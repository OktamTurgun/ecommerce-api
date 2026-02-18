"""
Product Category Model

Hierarchical category structure for organizing products.
Supports parent-child relationships for subcategories.
"""
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid


class Category(models.Model):
    """
    Product category model with hierarchical structure.
    
    Features:
    - Unique name and slug
    - Parent-child relationships
    - Active/inactive status
    - Auto-generated slugs
    - Timestamps
    
    Examples:
        # Root category
        electronics = Category.objects.create(name='Electronics')
        
        # Subcategory
        phones = Category.objects.create(
            name='Mobile Phones',
            parent=electronics
        )
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Category name (e.g., Electronics)'
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text='URL-friendly version of name'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Category description'
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text='Parent category (null for root categories)'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Is this category active and visible?'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        """String representation: category name."""
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug from name.
        
        If slug is not provided, creates URL-friendly slug from name.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """
        Get full category path (e.g., 'Electronics > Mobile Phones').
        
        Returns:
            str: Full hierarchical path
        """
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_ancestors(self):
        """
        Get all ancestor categories.
        
        Returns:
            list: List of ancestor categories from root to immediate parent
        """
        ancestors = []
        current = self.parent
        
        while current:
            ancestors.insert(0, current)
            current = current.parent
        
        return ancestors
    
    def get_descendants(self):
        """
        Get all descendant categories (recursive).
        
        Returns:
            QuerySet: All descendants
        """
        descendants = list(self.subcategories.all())
        
        for child in self.subcategories.all():
            descendants.extend(child.get_descendants())
        
        return descendants
    
    @property
    def is_root(self):
        """Check if this is a root category (no parent)."""
        return self.parent is None
    
    @property
    def product_count(self):
        """
        Get count of products in this category.
        
        Returns:
            int: Number of products
        """
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Product model for e-commerce catalog.
    
    Features:
    - Name, description, price
    - Category relationship
    - Stock tracking
    - Discount pricing
    - Active/Featured status
    - Auto-generated slugs
    - SKU support
    
    Examples:
        product = Product.objects.create(
            name='iPhone 15 Pro',
            price=Decimal('999.99'),
            category=electronics,
            stock=50
        )
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        help_text='Product name'
    )
    
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text='URL-friendly version of name'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Product description'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        help_text='Product category'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Regular price'
    )
    
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Discounted price (optional)'
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        help_text='Available quantity'
    )
    
    sku = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text='Stock Keeping Unit'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Is product active and visible?'
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text='Is this a featured product?'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-created_at']  # Newest first
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        """String representation: product name."""
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug from name.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """
        Custom validation.
        
        Validates:
        - Price must be positive
        - Stock must be non-negative
        - Discount price must be less than regular price
        """
        from django.core.exceptions import ValidationError
        
        # Price validation
        if self.price and self.price <= 0:
            raise ValidationError({'price': 'Price must be greater than 0'})
        
        # Stock validation
        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative'})
        
        # Discount price validation
        if self.discount_price:
            if self.discount_price >= self.price:
                raise ValidationError({
                    'discount_price': 'Discount price must be less than regular price'
                })
    
    @property
    def has_discount(self):
        """Check if product has a discount."""
        return self.discount_price is not None and self.discount_price > 0
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock > 0
    
    def get_price(self):
        """
        Get the current selling price.
        
        Returns discount price if available, otherwise regular price.
        """
        if self.has_discount:
            return self.discount_price
        return self.price
    
    @property
    def savings(self):
        """
        Calculate savings amount.
        
        Returns:
            Decimal: Amount saved if discount is active, otherwise 0
        """
        if self.has_discount:
            return self.price - self.discount_price
        return Decimal('0.00')
    
    @property
    def discount_percentage(self):
        """
        Calculate discount percentage.
        
        Returns:
            int: Discount percentage (0-100)
        """
        if self.has_discount:
            return int((self.savings / self.price) * 100)
        return 0
    
    def get_primary_image(self):
        """
        Get the primary image for this product.
        
        Returns:
            ProductImage: Primary image or None
        """
        return self.images.filter(is_primary=True).first()
    
    @property
    def average_rating(self):
        """
        Calculate average rating for product.
        
        Returns:
            float: Average rating (0 if no reviews)
        """
        from django.db.models import Avg
        result = self.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else 0
    
    @property
    def review_count(self):
        """
        Get total number of reviews.
        
        Returns:
            int: Number of reviews
        """
        return self.reviews.count()


class ProductImage(models.Model):
    """
    Product image model for multiple images per product.
    
    Features:
    - Multiple images per product
    - Image ordering
    - Primary image selection
    - Alt text for accessibility/SEO
    - Auto timestamps
    
    Examples:
        # Add primary image
        image = ProductImage.objects.create(
            product=product,
            image='products/iphone-front.jpg',
            alt_text='iPhone 15 Pro front view',
            is_primary=True,
            order=1
        )
        
        # Get product's primary image
        primary = product.get_primary_image()
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text='Product this image belongs to'
    )
    
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        help_text='Product image file'
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text='Alternative text for accessibility and SEO'
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text='Mark as primary/main product image'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers first)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'order']),
            models.Index(fields=['product', 'is_primary']),
        ]
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
    
    def __str__(self):
        """String representation."""
        return f'{self.product.name} - Image {self.order}'
    
    def save(self, *args, **kwargs):
        """
        Override save to auto-generate alt_text if not provided.
        """
        if not self.alt_text:
            self.alt_text = f'{self.product.name} image {self.order}'
        
        super().save(*args, **kwargs)