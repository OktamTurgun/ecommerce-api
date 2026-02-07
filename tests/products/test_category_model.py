"""
Tests for Category Model - TDD Approach

This module contains tests for the Category model.
Following TDD: Write tests FIRST, then implement the model.

Category Model Requirements:
- Unique name and slug
- Hierarchical structure (parent categories)
- Active/inactive status
- Auto-generated slug from name
- Ordering by name
- Soft delete capability
"""
import pytest
from django.db import IntegrityError
from django.utils.text import slugify


@pytest.mark.django_db
class TestCategoryModel:
    """
    Test suite for Category model.
    
    TDD Approach: These tests will FAIL initially.
    We'll implement the model to make them pass.
    """
    
    def test_category_creation(self):
        """
        Test creating a basic category.
        
        Expected behavior:
        - Category is created successfully
        - Has required fields: name, slug, is_active
        - Default is_active is True
        """
        from apps.products.models import Category
        
        # Arrange & Act
        category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        # Assert
        assert category.id is not None
        assert category.name == 'Electronics'
        assert category.slug == 'electronics'
        assert category.is_active == True
        assert str(category) == 'Electronics'
    
    def test_category_name_unique(self):
        """
        Test that category names must be unique.
        
        Expected behavior:
        - Cannot create two categories with same name
        - Raises IntegrityError
        """
        from apps.products.models import Category
        
        # Arrange
        Category.objects.create(name='Electronics', slug='electronics')
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            Category.objects.create(name='Electronics', slug='electronics-2')
    
    def test_category_slug_unique(self):
        """
        Test that category slugs must be unique.
        
        Expected behavior:
        - Cannot create two categories with same slug
        - Raises IntegrityError
        """
        from apps.products.models import Category
        
        # Arrange
        Category.objects.create(name='Electronics', slug='electronics')
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            Category.objects.create(name='Electronics Dept', slug='electronics')
    
    def test_category_slug_auto_generation(self):
        """
        Test automatic slug generation from name.
        
        Expected behavior:
        - If slug not provided, auto-generate from name
        - Slug is URL-friendly (lowercase, hyphens)
        """
        from apps.products.models import Category
        
        # Arrange & Act
        category = Category.objects.create(name='Mobile Phones')
        
        # Assert
        assert category.slug == 'mobile-phones'
    
    def test_category_parent_child_relationship(self):
        """
        Test hierarchical category structure.
        
        Expected behavior:
        - Category can have a parent category
        - Parent can have multiple children
        - Can query subcategories
        """
        from apps.products.models import Category
        
        # Arrange
        parent = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        # Act
        child1 = Category.objects.create(
            name='Mobile Phones',
            slug='mobile-phones',
            parent=parent
        )
        
        child2 = Category.objects.create(
            name='Laptops',
            slug='laptops',
            parent=parent
        )
        
        # Assert
        assert child1.parent == parent
        assert child2.parent == parent
        assert parent.subcategories.count() == 2
        assert child1 in parent.subcategories.all()
    
    def test_category_can_be_root(self):
        """
        Test that category can be a root (no parent).
        
        Expected behavior:
        - Parent can be None/null
        - Root categories exist
        """
        from apps.products.models import Category
        
        # Arrange & Act
        category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            parent=None
        )
        
        # Assert
        assert category.parent is None
    
    def test_category_active_inactive(self):
        """
        Test category active/inactive status.
        
        Expected behavior:
        - Can set category as inactive
        - Inactive categories can be filtered
        """
        from apps.products.models import Category
        
        # Arrange
        active_cat = Category.objects.create(
            name='Active Category',
            slug='active-category',
            is_active=True
        )
        
        inactive_cat = Category.objects.create(
            name='Inactive Category',
            slug='inactive-category',
            is_active=False
        )
        
        # Assert
        assert active_cat.is_active == True
        assert inactive_cat.is_active == False
        
        # Can filter active categories
        active_categories = Category.objects.filter(is_active=True)
        assert active_cat in active_categories
        assert inactive_cat not in active_categories
    
    def test_category_ordering(self):
        """
        Test category ordering.
        
        Expected behavior:
        - Categories ordered by name by default
        - Alphabetical ordering
        """
        from apps.products.models import Category
        
        # Arrange
        cat_b = Category.objects.create(name='Bravo', slug='bravo')
        cat_c = Category.objects.create(name='Charlie', slug='charlie')
        cat_a = Category.objects.create(name='Alpha', slug='alpha')
        
        # Act
        categories = list(Category.objects.all())
        
        # Assert
        assert categories[0] == cat_a
        assert categories[1] == cat_b
        assert categories[2] == cat_c
    
    def test_category_str_representation(self):
        """
        Test string representation of category.
        
        Expected behavior:
        - str(category) returns category name
        - Useful for admin panel and debugging
        """
        from apps.products.models import Category
        
        # Arrange
        category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        # Assert
        assert str(category) == 'Electronics'
    
    def test_category_description_optional(self):
        """
        Test that category description is optional.
        
        Expected behavior:
        - Can create category without description
        - Can add description
        """
        from apps.products.models import Category
        
        # Without description
        cat1 = Category.objects.create(
            name='Category 1',
            slug='category-1'
        )
        assert cat1.description == '' or cat1.description is None
        
        # With description
        cat2 = Category.objects.create(
            name='Category 2',
            slug='category-2',
            description='This is a test category'
        )
        assert cat2.description == 'This is a test category'
    
    def test_category_timestamps(self):
        """
        Test automatic timestamp fields.
        
        Expected behavior:
        - created_at set on creation
        - updated_at updates on save
        """
        from apps.products.models import Category
        from django.utils import timezone
        from datetime import timedelta
        
        # Arrange & Act
        category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Assert: created_at exists
        assert category.created_at is not None
        assert category.updated_at is not None
        
        # Assert: created_at is recent
        assert timezone.now() - category.created_at < timedelta(seconds=5)
        
        # Update and check updated_at changes
        old_updated_at = category.updated_at
        import time
        time.sleep(0.1)
        
        category.name = 'Updated Category'
        category.save()
        
        assert category.updated_at > old_updated_at


@pytest.mark.django_db
class TestCategoryManager:
    """
    Test suite for Category custom manager (if implemented).
    
    Tests for custom querysets and manager methods.
    """
    
    def test_active_categories_queryset(self):
        """
        Test filtering only active categories.
        
        Expected behavior:
        - Manager method returns only active categories
        - Excludes inactive ones
        """
        from apps.products.models import Category
        
        # Arrange
        active1 = Category.objects.create(
            name='Active 1',
            slug='active-1',
            is_active=True
        )
        
        active2 = Category.objects.create(
            name='Active 2',
            slug='active-2',
            is_active=True
        )
        
        inactive = Category.objects.create(
            name='Inactive',
            slug='inactive',
            is_active=False
        )
        
        # Act
        active_cats = Category.objects.filter(is_active=True)
        
        # Assert
        assert active_cats.count() == 2
        assert active1 in active_cats
        assert active2 in active_cats
        assert inactive not in active_cats
    
    def test_root_categories_queryset(self):
        """
        Test getting only root categories (no parent).
        
        Expected behavior:
        - Returns categories with parent=None
        - Excludes subcategories
        """
        from apps.products.models import Category
        
        # Arrange
        root1 = Category.objects.create(name='Root 1', slug='root-1')
        root2 = Category.objects.create(name='Root 2', slug='root-2')
        
        child = Category.objects.create(
            name='Child',
            slug='child',
            parent=root1
        )
        
        # Act
        root_cats = Category.objects.filter(parent__isnull=True)
        
        # Assert
        assert root_cats.count() == 2
        assert root1 in root_cats
        assert root2 in root_cats
        assert child not in root_cats


@pytest.mark.django_db
class TestCategoryValidation:
    """
    Test suite for Category model validation.
    
    Tests for field validation and constraints.
    """
    
    def test_category_name_max_length(self):
        """
        Test category name max length constraint.
        
        Expected behavior:
        - Name should have reasonable max length (e.g., 100 chars)
        - Can create category with name at max length
        """
        from apps.products.models import Category
        
        # Arrange
        long_name = 'A' * 100  # Assuming max_length=100
        
        # Act
        category = Category.objects.create(
            name=long_name,
            slug='long-category'
        )
        
        # Assert
        assert len(category.name) == 100
        assert category.name == long_name
    
    def test_category_slug_format(self):
        """
        Test that slug is URL-friendly.
        
        Expected behavior:
        - Slug is lowercase
        - Spaces replaced with hyphens
        - No special characters
        """
        from apps.products.models import Category
        
        # Arrange & Act
        category = Category.objects.create(
            name='Test Category With Spaces'
        )
        
        # Assert
        assert category.slug == 'test-category-with-spaces'
        assert ' ' not in category.slug
        assert category.slug.islower()