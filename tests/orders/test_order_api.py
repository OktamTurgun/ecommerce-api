"""
Tests for Order API Endpoints - TDD Approach

This module tests Order CRUD operations via REST API.

Endpoints:
- GET    /api/orders/              - List user's orders
- POST   /api/orders/              - Create order from cart
- GET    /api/orders/{id}/         - Get order detail
- PATCH  /api/orders/{id}/status/  - Update order status
- POST   /api/orders/{id}/cancel/  - Cancel order

Following TDD: Write tests FIRST, then implement API.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestOrderList:
    """
    Test suite for Order List endpoint.
    
    Endpoint: GET /api/orders/
    Permission: IsAuthenticated
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('orders:order-list')
    
    def test_list_orders_unauthenticated(self, api_client):
        """
        Test listing orders without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        """
        # Act
        response = api_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_orders_authenticated_empty(self, authenticated_client):
        """
        Test listing orders for user with no orders.
        
        Expected behavior:
        - Returns 200 OK
        - Empty list
        """
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0
    
    def test_list_user_orders_only(self, authenticated_client):
        """
        Test that users only see their own orders.
        
        Expected behavior:
        - Returns only current user's orders
        - Other users' orders not visible
        """
        from tests.factories import UserFactory, OrderFactory
        from apps.users.models import User
        
        # Arrange
        current_user = User.objects.first()  # authenticated_client's user
        other_user = UserFactory()
        
        # Current user's orders
        my_order1 = OrderFactory(user=current_user)
        my_order2 = OrderFactory(user=current_user)
        
        # Other user's orders
        OrderFactory(user=other_user)
        OrderFactory(user=other_user)
        
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        order_ids = [order['id'] for order in response.data['results']]
        assert str(my_order1.id) in order_ids
        assert str(my_order2.id) in order_ids


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCreateOrder:
    """
    Test suite for Create Order endpoint.
    
    Endpoint: POST /api/orders/
    Permission: IsAuthenticated
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('orders:order-list')
    
    def test_create_order_from_cart(self, authenticated_client):
        """
        Test creating order from cart items.
        
        Expected behavior:
        - Returns 201 Created
        - Order created with items
        - Cart cleared
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        from apps.cart.models import Cart
        
        # Arrange
        user = User.objects.first()
        cart = CartFactory(user=user)
        product1 = ProductFactory(name='iPhone', price=Decimal('999.99'), stock=10)
        product2 = ProductFactory(name='iPad', price=Decimal('599.99'), stock=10)
        
        CartItemFactory(cart=cart, product=product1, quantity=2, price_at_add=Decimal('999.99'))
        CartItemFactory(cart=cart, product=product2, quantity=1, price_at_add=Decimal('599.99'))
        
        data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA'
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'PENDING'
        assert len(response.data['items']) == 2
        assert float(response.data['total_amount']) == 2599.97
        assert response.data['total_items'] == 3
        
        # Cart should be cleared
        cart.refresh_from_db()
        assert cart.items.count() == 0
    
    def test_create_order_from_empty_cart(self, authenticated_client):
        """
        Test creating order with empty cart.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message
        """
        from tests.factories import CartFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        CartFactory(user=user)  # Empty cart
        
        data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'New York'
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_order_insufficient_stock(self, authenticated_client):
        """
        Test creating order with insufficient stock.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Stock error message
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        cart = CartFactory(user=user)
        product = ProductFactory(stock=5)  # Only 5 in stock
        
        CartItemFactory(cart=cart, product=product, quantity=10, price_at_add=Decimal('100.00'))  # Want 10!
        
        data = {'shipping_address': '123 Main St'}
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestOrderDetail:
    """
    Test suite for Order Detail endpoint.
    
    Endpoint: GET /api/orders/{id}/
    Permission: IsAuthenticated (own orders only)
    """
    
    def test_get_order_detail(self, authenticated_client):
        """
        Test getting order detail.
        
        Expected behavior:
        - Returns 200 OK
        - Order details with items
        """
        from tests.factories import OrderFactory, OrderItemFactory, ProductFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user)
        product1 = ProductFactory(name='iPhone')
        product2 = ProductFactory(name='iPad')
        
        OrderItemFactory(order=order, product=product1, product_name='iPhone', quantity=2, price=Decimal('999.99'))
        OrderItemFactory(order=order, product=product2, product_name='iPad', quantity=1, price=Decimal('599.99'))
        
        url = reverse('orders:order-detail', kwargs={'pk': order.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(order.id)
        assert len(response.data['items']) == 2
        assert float(response.data['total_amount']) == 2599.97
    
    def test_get_other_user_order(self, authenticated_client):
        """
        Test accessing another user's order.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        from tests.factories import UserFactory, OrderFactory
        
        # Arrange
        other_user = UserFactory()
        other_order = OrderFactory(user=other_user)
        
        url = reverse('orders:order-detail', kwargs={'pk': other_order.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCancelOrder:
    """
    Test suite for Cancel Order endpoint.
    
    Endpoint: POST /api/orders/{id}/cancel/
    Permission: IsAuthenticated
    """
    
    def test_cancel_pending_order(self, authenticated_client):
        """
        Test cancelling a pending order.
        
        Expected behavior:
        - Returns 200 OK
        - Status changed to CANCELLED
        """
        from tests.factories import OrderFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user, status='PENDING')
        
        url = reverse('orders:order-cancel', kwargs={'pk': order.id})
        
        # Act
        response = authenticated_client.post(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'CANCELLED'
        
        order.refresh_from_db()
        assert order.status == 'CANCELLED'
    
    def test_cancel_shipped_order(self, authenticated_client):
        """
        Test cancelling a shipped order.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Cannot cancel shipped orders
        """
        from tests.factories import OrderFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user, status='SHIPPED')
        
        url = reverse('orders:order-cancel', kwargs={'pk': order.id})
        
        # Act
        response = authenticated_client.post(url)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestOrderAPIIntegration:
    """
    Integration tests for complete Order API flows.
    """
    
    def test_complete_order_flow(self, authenticated_client):
        """
        Test complete order flow: Add to cart → Create order → View order → Cancel
        
        Steps:
        1. Add items to cart
        2. Create order from cart
        3. View order detail
        4. Cancel order
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        
        # Step 1: Add to cart
        user = User.objects.first()
        cart = CartFactory(user=user)
        product = ProductFactory(name='iPhone', price=Decimal('999.99'), stock=10)
        CartItemFactory(cart=cart, product=product, quantity=2, price_at_add=Decimal('999.99'))
        
        # Step 2: Create order
        create_url = reverse('orders:order-list')
        create_data = {
            'shipping_address': '123 Main St',
            'shipping_city': 'New York',
            'shipping_postal_code': '10001',
            'shipping_country': 'USA'
        }
        response = authenticated_client.post(create_url, create_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        order_id = response.data['id']
        
        # Step 3: View order
        detail_url = reverse('orders:order-detail', kwargs={'pk': order_id})
        response = authenticated_client.get(detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'PENDING'
        
        # Step 4: Cancel order
        cancel_url = reverse('orders:order-cancel', kwargs={'pk': order_id})
        response = authenticated_client.post(cancel_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'CANCELLED'
        
        # Verify cart is empty
        cart.refresh_from_db()
        assert cart.items.count() == 0