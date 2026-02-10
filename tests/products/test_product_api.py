"""
Tests for Product API Endpoints - TDD Approach

This module tests Product CRUD operations via REST API.

Endpoints:
- GET    /api/products/products/          - List products
- GET    /api/products/products/{id}/     - Retrieve product
- POST   /api/products/products/          - Create product (Admin only)
- PUT    /api/products/products/{id}/     - Update product (Admin only)
- PATCH  /api/products/products/{id}/     - Partial update (Admin only)
- DELETE /api/products/products/{id}/     - Delete product (Admin only)

Following TDD: Write tests FIRST, then views handle them.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestProductList:
    """
    Test suite for Product List endpoint.
    
    Endpoint: GET /api/products/products/
    Permission: AllowAny (public)
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:product-list')
    
    def test_list_products(self, api_client):
        """
        Test listing all products.
        
        Expected behavior:
        - Returns 200 OK
        - Returns list of products
        - Only active products shown by default
        """
        from tests.factories import ProductFactory
        
        # Arrange: Create products
        active1 = ProductFactory(name='iPhone 15', is_active=True)
        active2 = ProductFactory(name='MacBook Pro', is_active=True)
        inactive = ProductFactory(name='Old Product', is_active=False)
        
        # Act
        response = api_client.get(self.url)
        
        # Assert: Response
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) == 2  # Only active products
        
        # Assert: Product data
        product_names = [prod['name'] for prod in results]
        assert 'iPhone 15' in product_names
        assert 'MacBook Pro' in product_names
        assert 'Old Product' not in product_names
    
    def test_list_products_empty(self, api_client):
        """
        Test listing products when none exist.
        
        Expected behavior:
        - Returns 200 OK
        - Returns empty list
        """
        # Act
        response = api_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            assert len(results) == 0
            assert response.data['count'] == 0
        else:
            assert len(response.data) == 0
    
    def test_list_products_filter_by_category(self, api_client):
        """
        Test filtering products by category.
        
        Expected behavior:
        - Can filter by category ID
        - Returns only products in that category
        """
        from tests.factories import CategoryFactory, ProductFactory
        
        # Arrange
        electronics = CategoryFactory(name='Electronics')
        clothing = CategoryFactory(name='Clothing')
        
        phone = ProductFactory(name='iPhone', category=electronics)
        laptop = ProductFactory(name='MacBook', category=electronics)
        shirt = ProductFactory(name='T-Shirt', category=clothing)
        
        # Act: Filter by electronics category
        response = api_client.get(self.url, {'category': str(electronics.id)})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) == 2
        product_names = [prod['name'] for prod in results]
        assert 'iPhone' in product_names
        assert 'MacBook' in product_names
        assert 'T-Shirt' not in product_names
    
    def test_list_products_filter_by_price_range(self, api_client):
        """
        Test filtering products by price range.
        
        Expected behavior:
        - Can filter by price_min and price_max
        - Returns products within range
        """
        from tests.factories import ProductFactory
        
        # Arrange
        cheap = ProductFactory(name='Cheap', price=Decimal('10.00'))
        medium = ProductFactory(name='Medium', price=Decimal('50.00'))
        expensive = ProductFactory(name='Expensive', price=Decimal('1000.00'))
        
        # Act: Filter price range 20-100
        response = api_client.get(self.url, {
            'price_min': '20',
            'price_max': '100'
        })
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) == 1
        assert results[0]['name'] == 'Medium'
    
    def test_list_products_search(self, api_client):
        """
        Test searching products by name.
        
        Expected behavior:
        - Can search by name, description, SKU
        - Returns matching products
        """
        from tests.factories import ProductFactory
        
        # Arrange
        iphone = ProductFactory(name='iPhone 15 Pro', description='Latest iPhone')
        ipad = ProductFactory(name='iPad Air', description='Tablet device')
        macbook = ProductFactory(name='MacBook Pro', description='Laptop computer')
        
        # Act: Search for 'iPhone'
        response = api_client.get(self.url, {'search': 'iPhone'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) == 1
        assert results[0]['name'] == 'iPhone 15 Pro'
    
    def test_list_products_includes_computed_fields(self, api_client):
        """
        Test that product list includes computed fields.
        
        Expected behavior:
        - has_discount field
        - final_price field
        - is_in_stock field
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(
            name='Discounted Product',
            price=Decimal('100.00'),
            discount_price=Decimal('80.00'),
            stock=10
        )
        
        # Act
        response = api_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        product_data = results[0]
        assert 'has_discount' in product_data
        assert 'final_price' in product_data
        assert 'is_in_stock' in product_data
        assert product_data['has_discount'] == True
        assert product_data['final_price'] == '80.00'
        assert product_data['is_in_stock'] == True


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestProductDetail:
    """
    Test suite for Product Detail endpoint.
    
    Endpoint: GET /api/products/products/{id}/
    Permission: AllowAny (public)
    """
    
    def test_retrieve_product(self, api_client):
        """
        Test retrieving a single product.
        
        Expected behavior:
        - Returns 200 OK
        - Returns product details
        - Includes category details
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory(name='Electronics')
        product = ProductFactory(
            name='iPhone 15 Pro',
            description='Latest iPhone model',
            price=Decimal('999.99'),
            category=category,
            stock=50
        )
        
        url = reverse('products:product-detail', kwargs={'pk': product.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'iPhone 15 Pro'
        assert response.data['price'] == '999.99'
        assert 'category_detail' in response.data
        assert response.data['category_detail']['name'] == 'Electronics'
    
    def test_retrieve_nonexistent_product(self, api_client):
        """
        Test retrieving a product that doesn't exist.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        import uuid
        
        url = reverse('products:product-detail', kwargs={'pk': uuid.uuid4()})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestProductCreate:
    """
    Test suite for Product Create endpoint.
    
    Endpoint: POST /api/products/products/
    Permission: IsAdminUser (staff only)
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:product-list')
    
    def test_create_product_as_admin(self, admin_client):
        """
        Test creating product as admin.
        
        Expected behavior:
        - Returns 201 Created
        - Product is created in database
        - Slug is auto-generated
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        data = {
            'name': 'iPhone 15 Pro',
            'description': 'Latest iPhone',
            'price': '999.99',
            'category': str(category.id),
            'stock': 50,
            'sku': 'IPHONE-15-PRO'
        }
        
        # Act
        response = admin_client.post(self.url, data, format='json')
        
        # Assert: Response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'iPhone 15 Pro'
        assert response.data['slug'] == 'iphone-15-pro'
        assert response.data['price'] == '999.99'
        
        # Assert: Database
        from apps.products.models import Product
        assert Product.objects.filter(name='iPhone 15 Pro').exists()
    
    def test_create_product_unauthenticated(self, api_client):
        """
        Test creating product without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        - Product is not created
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        data = {
            'name': 'Test Product',
            'price': '10.00',
            'category': str(category.id)
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_product_as_regular_user(self, authenticated_client):
        """
        Test creating product as regular user (not admin).
        
        Expected behavior:
        - Returns 403 Forbidden
        - Product is not created
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        data = {
            'name': 'Test Product',
            'price': '10.00',
            'category': str(category.id)
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_product_with_discount(self, admin_client):
        """
        Test creating product with discount price.
        
        Expected behavior:
        - Returns 201 Created
        - Discount price is saved
        - has_discount is True
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        data = {
            'name': 'Discounted Product',
            'price': '100.00',
            'discount_price': '79.99',
            'category': str(category.id)
        }
        
        # Act
        response = admin_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['discount_price'] == '79.99'
        assert response.data['has_discount'] == True
        assert response.data['savings'] == '20.01'
    
    def test_create_product_invalid_discount(self, admin_client):
        """
        Test creating product with invalid discount (higher than price).
        
        Expected behavior:
        - Returns 400 Bad Request
        - Validation error
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        data = {
            'name': 'Invalid Product',
            'price': '50.00',
            'discount_price': '60.00',  # Higher than price!
            'category': str(category.id)
        }
        
        # Act
        response = admin_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'discount_price' in response.data


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestProductUpdate:
    """
    Test suite for Product Update endpoint.
    
    Endpoint: PUT/PATCH /api/products/products/{id}/
    Permission: IsAdminUser (staff only)
    """
    
    def test_update_product_as_admin(self, admin_client):
        """
        Test updating product as admin.
        
        Expected behavior:
        - Returns 200 OK
        - Product is updated
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(name='Old Name', price=Decimal('50.00'))
        
        url = reverse('products:product-detail', kwargs={'pk': product.id})
        data = {
            'name': 'New Name',
            'price': '99.99'
        }
        
        # Act
        response = admin_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'New Name'
        assert response.data['price'] == '99.99'
        
        # Database check
        product.refresh_from_db()
        assert product.name == 'New Name'
    
    def test_update_product_unauthenticated(self, api_client):
        """
        Test updating product without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(name='Test Product')
        
        url = reverse('products:product-detail', kwargs={'pk': product.id})
        data = {'name': 'New Name'}
        
        # Act
        response = api_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestProductDelete:
    """
    Test suite for Product Delete endpoint.
    
    Endpoint: DELETE /api/products/products/{id}/
    Permission: IsAdminUser (staff only)
    """
    
    def test_delete_product_as_admin(self, admin_client):
        """
        Test deleting product as admin.
        
        Expected behavior:
        - Returns 204 No Content
        - Product is deleted
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(name='Test Product')
        
        url = reverse('products:product-detail', kwargs={'pk': product.id})
        
        # Act
        response = admin_client.delete(url)
        
        # Assert: Response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Assert: Database
        from apps.products.models import Product
        assert not Product.objects.filter(id=product.id).exists()
    
    def test_delete_product_unauthenticated(self, api_client):
        """
        Test deleting product without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        - Product is not deleted
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory(name='Test Product')
        
        url = reverse('products:product-detail', kwargs={'pk': product.id})
        
        # Act
        response = api_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Product still exists
        from apps.products.models import Product
        assert Product.objects.filter(id=product.id).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestProductAPIIntegration:
    """
    Integration tests for complete Product CRUD flows.
    """
    
    def test_complete_product_crud_flow(self, admin_client, api_client):
        """
        Test complete CRUD flow: Create → Read → Update → Delete
        
        Steps:
        1. Admin creates product
        2. Public can view product
        3. Admin updates product
        4. Admin deletes product
        """
        from tests.factories import CategoryFactory
        
        list_url = reverse('products:product-list')
        category = CategoryFactory()
        
        # Step 1: Create
        create_data = {
            'name': 'iPhone 15 Pro',
            'description': 'Latest iPhone',
            'price': '999.99',
            'category': str(category.id),
            'stock': 50
        }
        
        create_response = admin_client.post(list_url, create_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        product_id = create_response.data['id']
        
        # Step 2: Public can view
        detail_url = reverse('products:product-detail', kwargs={'pk': product_id})
        view_response = api_client.get(detail_url)
        assert view_response.status_code == status.HTTP_200_OK
        assert view_response.data['name'] == 'iPhone 15 Pro'
        
        # Step 3: Update
        update_data = {'price': '899.99', 'stock': 100}
        update_response = admin_client.patch(detail_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['price'] == '899.99'
        assert update_response.data['stock'] == 100
        
        # Step 4: Delete
        delete_response = admin_client.delete(detail_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        verify_response = api_client.get(detail_url)
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND