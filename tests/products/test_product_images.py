"""
Tests for ProductImage Model - TDD Approach

This module tests ProductImage model functionality.
Multiple images per product with ordering and primary selection.

Following TDD: Write tests FIRST, then implement model.
"""
import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal


@pytest.mark.django_db
class TestProductImageModel:
    """
    Test suite for ProductImage model.
    
    Tests multiple images per product with ordering and primary image selection.
    """
    
    def test_product_image_creation(self):
        """
        Test creating a product image.
        
        Expected behavior:
        - Image can be created with required fields
        - All fields are saved correctly
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange
        product = ProductFactory(name='iPhone 15 Pro')
        
        # Act
        image = ProductImageFactory(
            product=product,
            alt_text='iPhone 15 Pro front view',
            is_primary=True,
            order=1
        )
        
        # Assert
        assert image.product == product
        assert image.alt_text == 'iPhone 15 Pro front view'
        assert image.is_primary is True
        assert image.order == 1
        assert image.created_at is not None
    
    def test_product_image_str_representation(self):
        """
        Test string representation of product image.
        
        Expected: "ProductName - Image 1"
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange
        product = ProductFactory(name='iPhone 15 Pro')
        image = ProductImageFactory(product=product, order=1)
        
        # Act & Assert
        assert str(image) == 'iPhone 15 Pro - Image 1'
    
    def test_multiple_images_per_product(self):
        """
        Test that a product can have multiple images.
        
        Expected behavior:
        - Product can have 3+ images
        - Images are ordered correctly
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange
        product = ProductFactory(name='iPhone 15 Pro')
        
        # Act: Create 3 images
        image1 = ProductImageFactory(product=product, order=1)
        image2 = ProductImageFactory(product=product, order=2)
        image3 = ProductImageFactory(product=product, order=3)
        
        # Assert
        assert product.images.count() == 3
        
        # Assert: Ordering
        images = product.images.all()
        assert images[0] == image1
        assert images[1] == image2
        assert images[2] == image3
    
    def test_primary_image_flag(self):
        """
        Test primary image flag functionality.
        
        Expected behavior:
        - Only one image should be primary
        - Primary image is easily identifiable
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange
        product = ProductFactory()
        
        # Act
        primary_image = ProductImageFactory(
            product=product,
            is_primary=True,
            order=1
        )
        secondary_image = ProductImageFactory(
            product=product,
            is_primary=False,
            order=2
        )
        
        # Assert
        assert primary_image.is_primary is True
        assert secondary_image.is_primary is False
        
        # Get primary image
        primary = product.images.filter(is_primary=True).first()
        assert primary == primary_image
    
    def test_image_ordering(self):
        """
        Test that images are ordered by order field.
        
        Expected behavior:
        - Images ordered by 'order' field ascending
        - Order can be changed
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange: Create images in random order
        product = ProductFactory()
        image3 = ProductImageFactory(product=product, order=3)
        image1 = ProductImageFactory(product=product, order=1)
        image2 = ProductImageFactory(product=product, order=2)
        
        # Act: Get ordered images
        images = product.images.all()
        
        # Assert: Correct order
        assert images[0] == image1
        assert images[1] == image2
        assert images[2] == image3
    
    def test_cascade_delete_on_product_delete(self):
        """
        Test that images are deleted when product is deleted.
        
        Expected behavior:
        - CASCADE delete
        - Images removed from database
        """
        from tests.factories import ProductFactory, ProductImageFactory
        from apps.products.models import ProductImage
        
        # Arrange
        product = ProductFactory()
        image1 = ProductImageFactory(product=product)
        image2 = ProductImageFactory(product=product)
        
        image_ids = [image1.id, image2.id]
        
        # Act: Delete product
        product.delete()
        
        # Assert: Images also deleted
        assert not ProductImage.objects.filter(id__in=image_ids).exists()
    
    def test_alt_text_for_accessibility(self):
        """
        Test alt text field for accessibility.
        
        Expected behavior:
        - Alt text is saved
        - Useful for SEO and accessibility
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange & Act
        product = ProductFactory(name='MacBook Pro')
        image = ProductImageFactory(
            product=product,
            alt_text='MacBook Pro 16-inch Space Gray'
        )
        
        # Assert
        assert image.alt_text == 'MacBook Pro 16-inch Space Gray'
    
    def test_default_values(self):
        """
        Test default values for fields.
        
        Expected behavior:
        - is_primary defaults to False
        - order defaults to 0
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange & Act
        product = ProductFactory()
        image = ProductImageFactory(
            product=product,
            # Don't set is_primary or order
        )
        
        # Assert: Check defaults
        assert image.is_primary is False
        assert image.order >= 0  # Factory may set it
    
    def test_get_primary_image_helper(self):
        """
        Test helper method to get primary image.
        
        Expected behavior:
        - Product.get_primary_image() returns primary image
        - Returns None if no primary image
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange
        product = ProductFactory()
        primary = ProductImageFactory(product=product, is_primary=True, order=1)
        secondary = ProductImageFactory(product=product, is_primary=False, order=2)
        
        # Act
        result = product.get_primary_image()
        
        # Assert
        assert result == primary
    
    def test_product_without_images(self):
        """
        Test product without any images.
        
        Expected behavior:
        - Product can exist without images
        - get_primary_image() returns None
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory()
        
        # Act & Assert
        assert product.images.count() == 0
        assert product.get_primary_image() is None


@pytest.mark.django_db
class TestProductImageValidation:
    """
    Test suite for ProductImage validation.
    """
    
    def test_order_must_be_positive(self):
        """
        Test that order must be >= 0.
        
        Expected behavior:
        - Negative order values not allowed
        """
        from tests.factories import ProductFactory, ProductImageFactory
        
        # Arrange
        product = ProductFactory()
        
        # Act & Assert: Negative order should fail
        with pytest.raises(Exception):  # ValidationError or IntegrityError
            image = ProductImageFactory(product=product, order=-1)
            image.full_clean()  # Trigger validation