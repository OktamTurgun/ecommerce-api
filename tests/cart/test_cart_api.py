"""
Tests for Cart API Endpoints - TDD Approach

This module tests Cart CRUD operations via REST API.

Endpoints:
- GET    /api/cart/              - Get current cart
- POST   /api/cart/items/        - Add item to cart
- PATCH  /api/cart/items/{id}/   - Update quantity
- DELETE /api/cart/items/{id}/   - Remove item
- POST   /api/cart/clear/        - Clear cart

Following TDD: Write tests FIRST, then implement API.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCartRetrieve:
    """
    Test suite for Cart Retrieve endpoint.
    
    Endpoint: GET /api/cart/
    Permission: AllowAny (works for authenticated and anonymous)
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('cart:cart-detail')
    
    def test_get_empty_cart_authenticated(self, authenticated_client):
        """
        Test getting empty cart for authenticated user.
        
        Expected behavior:
        - Returns 200 OK
        - Cart is empty
        - Total items = 0
        - Total price = 0.00
        """
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0
        assert response.data['total_price'] == '0.00'
        assert len(response.data['items']) == 0
    
    def test_get_empty_cart_anonymous(self, api_client):
        """
        Test getting empty cart for anonymous user.
        
        Expected behavior:
        - Returns 200 OK
        - Session-based cart created
        - Cart is empty
        """
        # Act
        response = api_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0
        assert len(response.data['items']) == 0
    
    def test_get_cart_with_items(self, authenticated_client):
        """
        Test getting cart with items.
        
        Expected behavior:
        - Returns 200 OK
        - Shows all cart items
        - Correct totals
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()  # authenticated_client's user
        cart = CartFactory(user=user)
        product1 = ProductFactory(name='iPhone', price=Decimal('999.99'))
        product2 = ProductFactory(name='iPad', price=Decimal('599.99'))
        
        CartItemFactory(cart=cart, product=product1, quantity=2, price_at_add=Decimal('999.99'))
        CartItemFactory(cart=cart, product=product2, quantity=1, price_at_add=Decimal('599.99'))
        
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 3  # 2 + 1
        assert float(response.data['total_price']) == 2599.97  # (999.99*2) + (599.99*1)
        assert len(response.data['items']) == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestAddToCart:
    """
    Test suite for Add to Cart endpoint.
    
    Endpoint: POST /api/cart/items/
    Permission: AllowAny
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('cart:cartitem-list')
    
    def test_add_item_to_cart_authenticated(self, authenticated_client):
        """
        Test adding item to cart (authenticated user).
        
        Expected behavior:
        - Returns 201 Created
        - Item added to cart
        - Correct quantity and price
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(name='iPhone', price=Decimal('999.99'), stock=10)
        
        data = {
            'product': str(product.id),
            'quantity': 2
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['product_detail']['name'] == 'iPhone'
        assert response.data['quantity'] == 2
        assert float(response.data['price_at_add']) == 999.99
        assert float(response.data['subtotal']) == 1999.98
    
    def test_add_item_to_cart_anonymous(self, api_client):
        """
        Test adding item to cart (anonymous user).
        
        Expected behavior:
        - Returns 201 Created
        - Session-based cart created
        - Item added
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(price=Decimal('50.00'), stock=10)
        
        data = {
            'product': str(product.id),
            'quantity': 1
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['quantity'] == 1
    
    def test_add_same_product_twice_increases_quantity(self, authenticated_client):
        """
        Test adding same product twice updates quantity.
        
        Expected behavior:
        - First add: Creates item with quantity 2
        - Second add: Updates quantity to 5 (2+3)
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(stock=10)
        
        # Act: Add first time
        data = {'product': str(product.id), 'quantity': 2}
        response1 = authenticated_client.post(self.url, data, format='json')
        
        # Act: Add second time
        data = {'product': str(product.id), 'quantity': 3}
        response2 = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_200_OK  # Updated, not created
        assert response2.data['quantity'] == 5  # 2 + 3
    
    def test_add_item_exceeds_stock(self, authenticated_client):
        """
        Test adding item with quantity exceeding stock.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Validation error
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(stock=5)
        
        data = {
            'product': str(product.id),
            'quantity': 10  # More than stock!
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_add_inactive_product(self, authenticated_client):
        """
        Test adding inactive product to cart.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Cannot add inactive products
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(is_active=False)
        
        data = {
            'product': str(product.id),
            'quantity': 1
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestUpdateCartItem:
    """
    Test suite for Update Cart Item endpoint.
    
    Endpoint: PATCH /api/cart/items/{id}/
    Permission: AllowAny (must own the cart)
    """
    
    def test_update_item_quantity(self, authenticated_client):
        """
        Test updating cart item quantity.
        
        Expected behavior:
        - Returns 200 OK
        - Quantity updated
        - Subtotal recalculated
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        cart = CartFactory(user=user)
        product = ProductFactory(stock=10)
        item = CartItemFactory(cart=cart, product=product, quantity=2, price_at_add=Decimal('50.00'))
        
        url = reverse('cart:cartitem-detail', kwargs={'pk': item.id})
        data = {'quantity': 5}
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] == 5
        assert float(response.data['subtotal']) == 250.00  # 5 × $50
    
    def test_update_quantity_exceeds_stock(self, authenticated_client):
        """
        Test updating quantity beyond available stock.
        
        Expected behavior:
        - Returns 400 Bad Request
        - Validation error
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        cart = CartFactory(user=user)
        product = ProductFactory(stock=5)
        item = CartItemFactory(cart=cart, product=product, quantity=2)
        
        url = reverse('cart:cartitem-detail', kwargs={'pk': item.id})
        data = {'quantity': 10}  # More than stock!
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestRemoveFromCart:
    """
    Test suite for Remove from Cart endpoint.
    
    Endpoint: DELETE /api/cart/items/{id}/
    Permission: AllowAny (must own the cart)
    """
    
    def test_remove_item_from_cart(self, authenticated_client):
        """
        Test removing item from cart.
        
        Expected behavior:
        - Returns 204 No Content
        - Item deleted
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        from apps.cart.models import CartItem
        
        # Arrange
        user = User.objects.first()
        cart = CartFactory(user=user)
        product = ProductFactory()
        item = CartItemFactory(cart=cart, product=product)
        
        url = reverse('cart:cartitem-detail', kwargs={'pk': item.id})
        
        # Act
        response = authenticated_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CartItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestClearCart:
    """
    Test suite for Clear Cart endpoint.
    
    Endpoint: POST /api/cart/clear/
    Permission: AllowAny
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('cart:cart-clear')
    
    def test_clear_cart(self, authenticated_client):
        """
        Test clearing all items from cart.
        
        Expected behavior:
        - Returns 200 OK
        - All items removed
        - Cart empty
        """
        from tests.factories import ProductFactory, CartFactory, CartItemFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=ProductFactory())
        CartItemFactory(cart=cart, product=ProductFactory())
        
        # Act
        response = authenticated_client.post(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert cart.items.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestCartAPIIntegration:
    """
    Integration tests for complete Cart API flows.
    """
    
    def test_complete_shopping_flow(self, authenticated_client):
        """
        Test complete shopping flow: Add → Update → Remove → Clear
        
        Steps:
        1. Get empty cart
        2. Add 2 products
        3. Update quantity
        4. Remove 1 product
        5. Clear cart
        """
        from tests.factories import ProductFactory
        
        # Step 1: Get empty cart
        cart_url = reverse('cart:cart-detail')
        response = authenticated_client.get(cart_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0
        
        # Step 2: Add product 1
        product1 = ProductFactory(name='iPhone', price=Decimal('999.99'), stock=10)
        add_url = reverse('cart:cartitem-list')
        response = authenticated_client.post(
            add_url,
            {'product': str(product1.id), 'quantity': 2},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        item1_id = response.data['id']
        
        # Step 3: Add product 2
        product2 = ProductFactory(name='iPad', price=Decimal('599.99'), stock=10)
        response = authenticated_client.post(
            add_url,
            {'product': str(product2.id), 'quantity': 1},
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        
        # Step 4: Check cart
        response = authenticated_client.get(cart_url)
        assert response.data['total_items'] == 3  # 2 + 1
        
        # Step 5: Update quantity
        update_url = reverse('cart:cartitem-detail', kwargs={'pk': item1_id})
        response = authenticated_client.patch(
            update_url,
            {'quantity': 5},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Step 6: Remove item
        response = authenticated_client.delete(update_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Step 7: Clear cart
        clear_url = reverse('cart:cart-clear')
        response = authenticated_client.post(clear_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Step 8: Verify empty
        response = authenticated_client.get(cart_url)
        assert response.data['total_items'] == 0