"""
Product Category Model

Hierarchical category structure for organizing products.
Supports parent-child relationships for subcategories.
"""
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