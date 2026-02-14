"""
Tests for Order Models - TDD Approach

This module tests Order and OrderItem model functionality.
Order management system for e-commerce.

Following TDD: Write tests FIRST, then implement models.
"""
import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal


@pytest.mark.django_db
class TestOrderModel:
    """
    Test suite for Order model.
    
    Tests order creation, status workflow, and calculations.
    """
    
    def test_order_creation(self):
        """
        Test creating an order.
        
        Expected behavior:
        - Order created with user
        - Status defaults to PENDING
        - Timestamps set
        """
        from tests.factories import UserFactory, OrderFactory
        
        # Arrange
        user = UserFactory()
        
        # Act
        order = OrderFactory(user=user)
        
        # Assert
        assert order.user == user
        assert order.status == 'PENDING'
        assert order.created_at is not None
        assert order.updated_at is not None
    
    def test_order_str_representation(self):
        """
        Test string representation of order.
        
        Expected: "Order #ID - Status"
        """
        from tests.factories import OrderFactory
        
        # Arrange & Act
        order = OrderFactory()
        
        # Assert
        assert 'Order' in str(order)
        assert str(order.id)[:8] in str(order)
    
    def test_order_status_choices(self):
        """
        Test order status choices.
        
        Expected: PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED
        """
        from apps.orders.models import Order
        
        # Act
        statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        
        # Assert
        assert 'PENDING' in statuses
        assert 'PROCESSING' in statuses
        assert 'SHIPPED' in statuses
        assert 'DELIVERED' in statuses
        assert 'CANCELLED' in statuses
    
    def test_empty_order_total_amount(self):
        """
        Test total_amount for order without items.
        
        Expected: Decimal('0.00')
        """
        from tests.factories import OrderFactory
        
        # Arrange
        order = OrderFactory()
        
        # Act & Assert
        assert order.total_amount == Decimal('0.00')
    
    def test_order_with_items_total_amount(self):
        """
        Test total_amount calculation with items.
        
        Expected: Sum of all item subtotals
        """
        from tests.factories import OrderFactory, OrderItemFactory
        
        # Arrange
        order = OrderFactory()
        # Item 1: 2 × $100 = $200
        OrderItemFactory(order=order, quantity=2, price=Decimal('100.00'))
        # Item 2: 3 × $50 = $150
        OrderItemFactory(order=order, quantity=3, price=Decimal('50.00'))
        
        # Act & Assert
        assert order.total_amount == Decimal('350.00')  # $200 + $150
    
    def test_order_total_items(self):
        """
        Test total_items count.
        
        Expected: Sum of all quantities
        """
        from tests.factories import OrderFactory, OrderItemFactory
        
        # Arrange
        order = OrderFactory()
        OrderItemFactory(order=order, quantity=2)
        OrderItemFactory(order=order, quantity=3)
        
        # Act & Assert
        assert order.total_items == 5  # 2 + 3
    
    def test_order_status_update(self):
        """
        Test updating order status.
        
        Expected: Status changes, updated_at changes
        """
        from tests.factories import OrderFactory
        import time
        
        # Arrange
        order = OrderFactory(status='PENDING')
        old_updated_at = order.updated_at
        
        # Small delay to ensure timestamp difference
        time.sleep(0.01)
        
        # Act
        order.status = 'PROCESSING'
        order.save()
        
        # Assert
        order.refresh_from_db()
        assert order.status == 'PROCESSING'
        assert order.updated_at > old_updated_at
    
    def test_cascade_delete_on_user_delete(self):
        """
        Test that order is deleted when user is deleted.
        
        Expected: CASCADE delete
        """
        from tests.factories import UserFactory, OrderFactory
        from apps.orders.models import Order
        
        # Arrange
        user = UserFactory()
        order = OrderFactory(user=user)
        order_id = order.id
        
        # Act
        user.delete()
        
        # Assert
        assert not Order.objects.filter(id=order_id).exists()
    
    def test_order_shipping_address_optional(self):
        """
        Test shipping address is optional.
        
        Expected: Order can be created without shipping address
        """
        from tests.factories import OrderFactory
        
        # Act
        order = OrderFactory(
            shipping_address=None,
            shipping_city=None,
            shipping_postal_code=None,
            shipping_country=None
        )
        
        # Assert
        assert order.shipping_address is None


@pytest.mark.django_db
class TestOrderItemModel:
    """
    Test suite for OrderItem model.
    
    Tests order items with product snapshots.
    """
    
    def test_order_item_creation(self):
        """
        Test creating an order item.
        
        Expected: Item created with product snapshot
        """
        from tests.factories import OrderFactory, OrderItemFactory, ProductFactory
        
        # Arrange
        order = OrderFactory()
        product = ProductFactory(name='iPhone 15', price=Decimal('999.99'))
        
        # Act
        item = OrderItemFactory(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            price=product.price,
            quantity=2
        )
        
        # Assert
        assert item.order == order
        assert item.product == product
        assert item.product_name == 'iPhone 15'
        assert item.price == Decimal('999.99')
        assert item.quantity == 2
    
    def test_order_item_str_representation(self):
        """
        Test string representation.
        
        Expected: "2x iPhone 15"
        """
        from tests.factories import OrderItemFactory
        
        # Arrange
        item = OrderItemFactory(
            product_name='iPhone 15',
            quantity=2
        )
        
        # Act & Assert
        assert '2' in str(item)
        assert 'iPhone 15' in str(item)
    
    def test_order_item_subtotal(self):
        """
        Test subtotal calculation.
        
        Expected: quantity × price
        """
        from tests.factories import OrderItemFactory
        
        # Arrange
        item = OrderItemFactory(
            quantity=3,
            price=Decimal('50.00')
        )
        
        # Act & Assert
        assert item.subtotal == Decimal('150.00')  # 3 × $50
    
    def test_product_snapshot(self):
        """
        Test product snapshot - data saved at order time.
        
        Expected: OrderItem keeps original data even if product changes
        """
        from tests.factories import OrderItemFactory, ProductFactory
        
        # Arrange
        product = ProductFactory(name='iPhone', price=Decimal('999.99'))
        item = OrderItemFactory(
            product=product,
            product_name=product.name,
            price=product.price
        )
        
        # Act: Change product
        product.name = 'iPhone 15 Pro Max'
        product.price = Decimal('1199.99')
        product.save()
        
        # Assert: Order item unchanged
        item.refresh_from_db()
        assert item.product_name == 'iPhone'  # Original name
        assert item.price == Decimal('999.99')  # Original price
    
    def test_cascade_delete_on_order_delete(self):
        """
        Test items deleted when order deleted.
        
        Expected: CASCADE delete
        """
        from tests.factories import OrderFactory, OrderItemFactory
        from apps.orders.models import OrderItem
        
        # Arrange
        order = OrderFactory()
        item1 = OrderItemFactory(order=order)
        item2 = OrderItemFactory(order=order)
        
        item_ids = [item1.id, item2.id]
        
        # Act
        order.delete()
        
        # Assert
        assert not OrderItem.objects.filter(id__in=item_ids).exists()
    
    def test_product_null_on_product_delete(self):
        """
        Test product field set to NULL when product deleted.
        
        Expected: SET_NULL behavior
        """
        from tests.factories import OrderItemFactory, ProductFactory
        
        # Arrange
        product = ProductFactory()
        item = OrderItemFactory(product=product)
        
        # Act
        product.delete()
        
        # Assert
        item.refresh_from_db()
        assert item.product is None  # Product deleted
        assert item.product_name is not None  # Snapshot preserved


@pytest.mark.django_db
class TestOrderBusinessLogic:
    """
    Test order business logic and workflows.
    """
    
    def test_create_order_from_cart(self):
        """
        Test creating order from cart items.
        
        Expected:
        - Order created
        - Cart items converted to order items
        - Cart cleared
        """
        from tests.factories import UserFactory, CartFactory, CartItemFactory, ProductFactory
        from apps.orders.models import Order, OrderItem
        
        # Arrange
        user = UserFactory()  # Create user first
        cart = CartFactory(user=user)  # Cart with user
        product1 = ProductFactory(price=Decimal('100.00'))
        product2 = ProductFactory(price=Decimal('50.00'))
        
        CartItemFactory(cart=cart, product=product1, quantity=2, price_at_add=Decimal('100.00'))
        CartItemFactory(cart=cart, product=product2, quantity=1, price_at_add=Decimal('50.00'))
        
        # Act: Create order (this will be in view/service layer)
        order = Order.objects.create(user=cart.user)
        
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                price=cart_item.price_at_add,
                quantity=cart_item.quantity
            )
        
        # Assert
        assert order.total_items == 3  # 2 + 1
        assert order.total_amount == Decimal('250.00')  # $200 + $50
        assert order.items.count() == 2
    
    def test_order_status_workflow(self):
        """
        Test order status transitions.
        
        Expected: PENDING → PROCESSING → SHIPPED → DELIVERED
        """
        from tests.factories import OrderFactory
        
        # Arrange
        order = OrderFactory(status='PENDING')
        
        # Act & Assert: Workflow
        assert order.status == 'PENDING'
        
        order.status = 'PROCESSING'
        order.save()
        assert order.status == 'PROCESSING'
        
        order.status = 'SHIPPED'
        order.save()
        assert order.status == 'SHIPPED'
        
        order.status = 'DELIVERED'
        order.save()
        assert order.status == 'DELIVERED'
    
    def test_cancel_order(self):
        """
        Test cancelling an order.
        
        Expected: Status changes to CANCELLED
        """
        from tests.factories import OrderFactory
        
        # Arrange
        order = OrderFactory(status='PENDING')
        
        # Act
        order.status = 'CANCELLED'
        order.save()
        
        # Assert
        assert order.status == 'CANCELLED'