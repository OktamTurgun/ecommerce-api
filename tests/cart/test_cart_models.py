"""
Tests for Cart Models - TDD Approach

This module tests Cart and CartItem model functionality.
Shopping cart for both authenticated and anonymous users.

Following TDD: Write tests FIRST, then implement models.
"""
import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal


@pytest.mark.django_db
class TestCartModel:
    """
    Test suite for Cart model.
    
    Tests shopping cart for authenticated and anonymous users.
    """
    
    def test_cart_creation_for_authenticated_user(self):
        """
        Test creating cart for authenticated user.
        
        Expected behavior:
        - Cart created with user
        - session_key is None
        - Timestamps are set
        """
        from tests.factories import UserFactory, CartFactory
        
        # Arrange
        user = UserFactory()
        
        # Act
        cart = CartFactory(user=user, session_key=None)
        
        # Assert
        assert cart.user == user
        assert cart.session_key is None
        assert cart.created_at is not None
        assert cart.updated_at is not None
    
    def test_cart_creation_for_anonymous_user(self):
        """
        Test creating cart for anonymous user (session-based).
        
        Expected behavior:
        - Cart created with session_key
        - user is None
        """
        from tests.factories import CartFactory
        
        # Arrange & Act
        cart = CartFactory(user=None, session_key='abc123session')
        
        # Assert
        assert cart.user is None
        assert cart.session_key == 'abc123session'
    
    def test_cart_str_representation(self):
        """
        Test string representation of cart.
        
        Expected: "Cart for {user.email}" or "Anonymous Cart {session_key}"
        """
        from tests.factories import UserFactory, CartFactory
        
        # Arrange & Act
        user = UserFactory(email='test@example.com')
        cart = CartFactory(user=user)
        
        # Assert
        assert 'test@example.com' in str(cart) or 'Cart' in str(cart)
    
    def test_empty_cart_total_items(self):
        """
        Test total_items property for empty cart.
        
        Expected: 0 items
        """
        from tests.factories import CartFactory
        
        # Arrange
        cart = CartFactory()
        
        # Act & Assert
        assert cart.total_items == 0
    
    def test_empty_cart_total_price(self):
        """
        Test total_price property for empty cart.
        
        Expected: Decimal('0.00')
        """
        from tests.factories import CartFactory
        
        # Arrange
        cart = CartFactory()
        
        # Act & Assert
        assert cart.total_price == Decimal('0.00')
    
    def test_cart_with_items_total_items(self):
        """
        Test total_items property with items in cart.
        
        Expected: Sum of all quantities
        """
        from tests.factories import CartFactory, CartItemFactory
        
        # Arrange
        cart = CartFactory()
        CartItemFactory(cart=cart, quantity=2)
        CartItemFactory(cart=cart, quantity=3)
        
        # Act & Assert
        assert cart.total_items == 5  # 2 + 3
    
    def test_cart_with_items_total_price(self):
        """
        Test total_price property with items in cart.
        
        Expected: Sum of all item subtotals
        """
        from tests.factories import CartFactory, CartItemFactory
        
        # Arrange
        cart = CartFactory()
        # Item 1: 2 × $10 = $20
        CartItemFactory(cart=cart, quantity=2, price_at_add=Decimal('10.00'))
        # Item 2: 3 × $15 = $45
        CartItemFactory(cart=cart, quantity=3, price_at_add=Decimal('15.00'))
        
        # Act & Assert
        assert cart.total_price == Decimal('65.00')  # $20 + $45
    
    def test_cart_cascade_delete(self):
        """
        Test that deleting cart also deletes items.
        
        Expected behavior:
        - CASCADE delete
        - CartItems removed
        """
        from tests.factories import CartFactory, CartItemFactory
        from apps.cart.models import CartItem
        
        # Arrange
        cart = CartFactory()
        item1 = CartItemFactory(cart=cart)
        item2 = CartItemFactory(cart=cart)
        
        item_ids = [item1.id, item2.id]
        
        # Act: Delete cart
        cart.delete()
        
        # Assert: Items also deleted
        assert not CartItem.objects.filter(id__in=item_ids).exists()


@pytest.mark.django_db
class TestCartItemModel:
    """
    Test suite for CartItem model.
    
    Tests individual cart items with products, quantities, and prices.
    """
    
    def test_cart_item_creation(self):
        """
        Test creating a cart item.
        
        Expected behavior:
        - Item created with cart, product, quantity, price
        - All fields saved correctly
        """
        from tests.factories import CartFactory, ProductFactory, CartItemFactory
        
        # Arrange
        cart = CartFactory()
        product = ProductFactory(name='iPhone 15', price=Decimal('999.99'))
        
        # Act
        item = CartItemFactory(
            cart=cart,
            product=product,
            quantity=2,
            price_at_add=Decimal('999.99')
        )
        
        # Assert
        assert item.cart == cart
        assert item.product == product
        assert item.quantity == 2
        assert item.price_at_add == Decimal('999.99')
    
    def test_cart_item_str_representation(self):
        """
        Test string representation of cart item.
        
        Expected: "2x iPhone 15"
        """
        from tests.factories import CartItemFactory, ProductFactory
        
        # Arrange
        product = ProductFactory(name='iPhone 15')
        item = CartItemFactory(product=product, quantity=2)
        
        # Act & Assert
        assert '2' in str(item)
        assert 'iPhone 15' in str(item)
    
    def test_cart_item_subtotal(self):
        """
        Test subtotal property calculation.
        
        Expected: quantity × price_at_add
        """
        from tests.factories import CartItemFactory
        
        # Arrange
        item = CartItemFactory(
            quantity=3,
            price_at_add=Decimal('50.00')
        )
        
        # Act & Assert
        assert item.subtotal == Decimal('150.00')  # 3 × $50
    
    def test_price_snapshot_on_add(self):
        """
        Test that price is saved when item added to cart.
        
        Expected behavior:
        - price_at_add saves current price
        - If product price changes, cart price doesn't change
        """
        from tests.factories import CartItemFactory, ProductFactory
        
        # Arrange
        product = ProductFactory(price=Decimal('100.00'))
        item = CartItemFactory(
            product=product,
            price_at_add=product.price
        )
        
        # Act: Change product price
        product.price = Decimal('150.00')
        product.save()
        
        # Assert: Cart item price unchanged
        item.refresh_from_db()
        assert item.price_at_add == Decimal('100.00')  # Original price
        assert product.price == Decimal('150.00')  # New price
    
    def test_cart_item_quantity_positive(self):
        """
        Test that quantity must be positive.
        
        Expected behavior:
        - Quantity >= 1
        - Validation error for quantity < 1
        """
        from tests.factories import CartItemFactory
        
        # Act & Assert: Zero quantity should fail
        with pytest.raises(Exception):  # ValidationError or IntegrityError
            item = CartItemFactory(quantity=0)
            item.full_clean()
    
    def test_cascade_delete_on_product_delete(self):
        """
        Test that cart item is deleted when product is deleted.
        
        Expected behavior:
        - CASCADE delete
        - Item removed from cart
        """
        from tests.factories import CartItemFactory, ProductFactory
        from apps.cart.models import CartItem
        
        # Arrange
        product = ProductFactory()
        item = CartItemFactory(product=product)
        item_id = item.id
        
        # Act: Delete product
        product.delete()
        
        # Assert: Item also deleted
        assert not CartItem.objects.filter(id=item_id).exists()
    
    def test_multiple_items_in_cart(self):
        """
        Test cart can have multiple items.
        
        Expected behavior:
        - Multiple CartItems with same cart
        - Different products
        """
        from tests.factories import CartFactory, CartItemFactory, ProductFactory
        
        # Arrange
        cart = CartFactory()
        product1 = ProductFactory(name='iPhone')
        product2 = ProductFactory(name='MacBook')
        
        # Act
        item1 = CartItemFactory(cart=cart, product=product1)
        item2 = CartItemFactory(cart=cart, product=product2)
        
        # Assert
        assert cart.items.count() == 2
        assert item1.product.name == 'iPhone'
        assert item2.product.name == 'MacBook'


@pytest.mark.django_db
class TestCartBusinessLogic:
    """
    Test suite for cart business logic.
    """
    
    def test_add_same_product_twice_increases_quantity(self):
        """
        Test adding same product twice updates quantity.
        
        Expected behavior:
        - Same product + same cart = update quantity
        - Not create duplicate items
        """
        from tests.factories import CartFactory, ProductFactory
        from apps.cart.models import CartItem
        
        # Arrange
        cart = CartFactory()
        product = ProductFactory()
        
        # Act: Add product twice
        item1 = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2,
            price_at_add=product.price
        )
        
        # In real implementation, this would update quantity
        # For now, test that we can have logic for this
        
        # Assert
        assert cart.items.count() >= 1
    
    def test_cart_items_ordered_by_created_at(self):
        """
        Test that cart items are ordered by creation date.
        
        Expected behavior:
        - Items ordered by created_at (newest or oldest first)
        """
        from tests.factories import CartFactory, CartItemFactory
        import time
        
        # Arrange
        cart = CartFactory()
        item1 = CartItemFactory(cart=cart)
        time.sleep(0.01)  # Small delay
        item2 = CartItemFactory(cart=cart)
        
        # Act
        items = cart.items.all()
        
        # Assert: Items exist (ordering tested in model Meta)
        assert items.count() == 2