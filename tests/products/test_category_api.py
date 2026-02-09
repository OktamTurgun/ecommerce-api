"""
Tests for Category API Endpoints - TDD Approach

This module tests Category CRUD operations via REST API.

Endpoints:
- GET    /api/products/categories/          - List categories
- GET    /api/products/categories/{id}/     - Retrieve category
- POST   /api/products/categories/          - Create category (Admin only)
- PUT    /api/products/categories/{id}/     - Update category (Admin only)
- PATCH  /api/products/categories/{id}/     - Partial update (Admin only)
- DELETE /api/products/categories/{id}/     - Delete category (Admin only)

Following TDD: Write tests FIRST, then implement views and serializers.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCategoryList:
    """
    Test suite for Category List endpoint.
    
    Endpoint: GET /api/products/categories/
    Permission: AllowAny (public)
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:category-list')
    
    def test_list_categories(self, api_client):
        """
        Test listing all categories.
        
        Expected behavior:
        - Returns 200 OK
        - Returns list of categories
        - Only active categories shown by default
        """
        from tests.factories import CategoryFactory
        
        # Arrange: Create categories
        active1 = CategoryFactory(name='Electronics', is_active=True)
        active2 = CategoryFactory(name='Clothing', is_active=True)
        inactive = CategoryFactory(name='Inactive', is_active=False)
        
        # Act
        response = api_client.get(self.url)
        
        # Assert: Response
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination if enabled
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) == 2  # Only active categories
        
        # Assert: Category data
        category_names = [cat['name'] for cat in results]
        assert 'Electronics' in category_names
        assert 'Clothing' in category_names
        assert 'Inactive' not in category_names
    
    def test_list_categories_empty(self, api_client):
        """
        Test listing categories when none exist.
        
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
    
    def test_list_categories_includes_product_count(self, api_client):
        """
        Test that category list includes product count.
        
        Expected behavior:
        - Each category has product_count field
        - Count reflects active products only
        """
        from tests.factories import CategoryFactory, ProductFactory
        
        # Arrange
        category = CategoryFactory(name='Electronics')
        ProductFactory(category=category, is_active=True)
        ProductFactory(category=category, is_active=True)
        ProductFactory(category=category, is_active=False)  # Inactive
        
        # Act
        response = api_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) > 0  # At least one category
        
        # Find the category we created
        category_data = next((cat for cat in results if cat['name'] == category.name), None)
        assert category_data is not None
        assert category_data['product_count'] == 2  # Only active products
    
    def test_list_categories_hierarchical(self, api_client):
        """
        Test that subcategories are properly nested.
        
        Expected behavior:
        - Parent categories include subcategories
        - Or subcategories include parent info
        """
        from tests.factories import CategoryFactory
        
        # Arrange: Parent and child
        parent = CategoryFactory(name='Electronics', parent=None)
        child = CategoryFactory(name='Laptops', parent=parent)
        
        # Act
        response = api_client.get(self.url)
        
        # Assert: Both categories returned
        assert response.status_code == status.HTTP_200_OK
        
        # Handle pagination
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data
        
        assert len(results) == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCategoryDetail:
    """
    Test suite for Category Detail endpoint.
    
    Endpoint: GET /api/products/categories/{id}/
    Permission: AllowAny (public)
    """
    
    def test_retrieve_category(self, api_client):
        """
        Test retrieving a single category.
        
        Expected behavior:
        - Returns 200 OK
        - Returns category details
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory(
            name='Electronics',
            description='Electronic devices'
        )
        
        url = reverse('products:category-detail', kwargs={'pk': category.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Electronics'
        assert response.data['description'] == 'Electronic devices'
    
    def test_retrieve_nonexistent_category(self, api_client):
        """
        Test retrieving a category that doesn't exist.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        import uuid
        
        url = reverse('products:category-detail', kwargs={'pk': uuid.uuid4()})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_retrieve_category_with_products(self, api_client):
        """
        Test that category detail includes associated products.
        
        Expected behavior:
        - Category includes products list or count
        - Only active products shown
        """
        from tests.factories import CategoryFactory, ProductFactory
        
        # Arrange
        category = CategoryFactory(name='Electronics')
        product1 = ProductFactory(category=category, name='iPhone', is_active=True)
        product2 = ProductFactory(category=category, name='iPad', is_active=True)
        inactive = ProductFactory(category=category, name='Old Product', is_active=False)
        
        url = reverse('products:category-detail', kwargs={'pk': category.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Either products list or product_count
        if 'products' in response.data:
            assert len(response.data['products']) == 2
        elif 'product_count' in response.data:
            assert response.data['product_count'] == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCategoryCreate:
    """
    Test suite for Category Create endpoint.
    
    Endpoint: POST /api/products/categories/
    Permission: IsAdminUser (staff only)
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:category-list')
    
    def test_create_category_as_admin(self, admin_client):
        """
        Test creating category as admin.
        
        Expected behavior:
        - Returns 201 Created
        - Category is created in database
        - Slug is auto-generated
        """
        # Arrange
        data = {
            'name': 'Electronics',
            'description': 'Electronic devices',
        }
        
        # Act
        response = admin_client.post(self.url, data, format='json')
        
        # Assert: Response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Electronics'
        assert response.data['slug'] == 'electronics'
        
        # Assert: Database
        from apps.products.models import Category
        assert Category.objects.filter(name='Electronics').exists()
    
    def test_create_category_unauthenticated(self, api_client):
        """
        Test creating category without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        - Category is not created
        """
        # Arrange
        data = {
            'name': 'Electronics',
        }
        
        # Act
        response = api_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_category_as_regular_user(self, authenticated_client):
        """
        Test creating category as regular user (not admin).
        
        Expected behavior:
        - Returns 403 Forbidden
        - Category is not created
        """
        # Arrange
        data = {
            'name': 'Electronics',
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_create_category_with_parent(self, admin_client):
        """
        Test creating subcategory with parent.
        
        Expected behavior:
        - Returns 201 Created
        - Parent relationship is established
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        parent = CategoryFactory(name='Electronics')
        
        data = {
            'name': 'Laptops',
            'parent': str(parent.id)
        }
        
        # Act
        response = admin_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert str(response.data['parent']) == str(parent.id)


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCategoryUpdate:
    """
    Test suite for Category Update endpoint.
    
    Endpoint: PUT/PATCH /api/products/categories/{id}/
    Permission: IsAdminUser (staff only)
    """
    
    def test_update_category_as_admin(self, admin_client):
        """
        Test updating category as admin.
        
        Expected behavior:
        - Returns 200 OK
        - Category is updated
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory(name='Old Name')
        
        url = reverse('products:category-detail', kwargs={'pk': category.id})
        data = {
            'name': 'New Name',
            'description': 'Updated description'
        }
        
        # Act
        response = admin_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'New Name'
        
        # Database check
        category.refresh_from_db()
        assert category.name == 'New Name'
    
    def test_update_category_unauthenticated(self, api_client):
        """
        Test updating category without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory(name='Electronics')
        
        url = reverse('products:category-detail', kwargs={'pk': category.id})
        data = {'name': 'New Name'}
        
        # Act
        response = api_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCategoryDelete:
    """
    Test suite for Category Delete endpoint.
    
    Endpoint: DELETE /api/products/categories/{id}/
    Permission: IsAdminUser (staff only)
    """
    
    def test_delete_category_as_admin(self, admin_client):
        """
        Test deleting category as admin.
        
        Expected behavior:
        - Returns 204 No Content
        - Category is deleted
        - Products are also deleted (CASCADE)
        """
        from tests.factories import CategoryFactory, ProductFactory
        
        # Arrange
        category = CategoryFactory(name='Electronics')
        product = ProductFactory(category=category)
        
        url = reverse('products:category-detail', kwargs={'pk': category.id})
        
        # Act
        response = admin_client.delete(url)
        
        # Assert: Response
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Assert: Database
        from apps.products.models import Category, Product
        assert not Category.objects.filter(id=category.id).exists()
        assert not Product.objects.filter(id=product.id).exists()  # CASCADE
    
    def test_delete_category_unauthenticated(self, api_client):
        """
        Test deleting category without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        - Category is not deleted
        """
        from tests.factories import CategoryFactory
        
        # Arrange
        category = CategoryFactory(name='Electronics')
        
        url = reverse('products:category-detail', kwargs={'pk': category.id})
        
        # Act
        response = api_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Category still exists
        from apps.products.models import Category
        assert Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.integration
class TestCategoryAPIIntegration:
    """
    Integration tests for complete Category CRUD flows.
    """
    
    def test_complete_category_crud_flow(self, admin_client, api_client):
        """
        Test complete CRUD flow: Create → Read → Update → Delete
        
        Steps:
        1. Admin creates category
        2. Public can view category
        3. Admin updates category
        4. Admin deletes category
        """
        list_url = reverse('products:category-list')
        
        # Step 1: Create
        create_data = {
            'name': 'Electronics',
            'description': 'Electronic devices'
        }
        
        create_response = admin_client.post(list_url, create_data, format='json')
        assert create_response.status_code == status.HTTP_201_CREATED
        category_id = create_response.data['id']
        
        # Step 2: Public can view
        detail_url = reverse('products:category-detail', kwargs={'pk': category_id})
        view_response = api_client.get(detail_url)
        assert view_response.status_code == status.HTTP_200_OK
        assert view_response.data['name'] == 'Electronics'
        
        # Step 3: Update
        update_data = {'description': 'Updated description'}
        update_response = admin_client.patch(detail_url, update_data, format='json')
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.data['description'] == 'Updated description'
        
        # Step 4: Delete
        delete_response = admin_client.delete(detail_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        verify_response = api_client.get(detail_url)
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND