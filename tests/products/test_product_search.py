"""
Tests for Product Search & Filtering - TDD Approach

This module tests product search and filtering functionality.

Query Parameters:
- search: Full-text search in name and description
- category: Filter by category ID
- min_price: Minimum price
- max_price: Maximum price
- min_rating: Minimum average rating
- ordering: Sort results (price, -price, name, -created_at)

Following TDD: Write tests FIRST, then implement filters.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal


@pytest.mark.django_db
class TestProductSearch:
    """
    Test suite for product search functionality.
    
    Endpoint: GET /api/products/products/?search=query
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:product-list')
    
    def test_search_by_name(self, api_client):
        """
        Test searching products by name.
        
        Expected behavior:
        - Returns products matching search query in name
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        product1 = ProductFactory(name='iPhone 15 Pro', category=category)
        product2 = ProductFactory(name='iPhone 14', category=category)
        product3 = ProductFactory(name='Samsung Galaxy', category=category)
        
        # Act
        response = api_client.get(self.url, {'search': 'iPhone'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        names = [p['name'] for p in response.data['results']]
        assert 'iPhone 15 Pro' in names
        assert 'iPhone 14' in names
        assert 'Samsung Galaxy' not in names
    
    def test_search_by_description(self, api_client):
        """
        Test searching products by description.
        
        Expected behavior:
        - Returns products matching search query in description
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        product1 = ProductFactory(
            name='Phone A',
            description='Amazing smartphone with great camera',
            category=category
        )
        product2 = ProductFactory(
            name='Phone B',
            description='Basic phone for calls',
            category=category
        )
        
        # Act
        response = api_client.get(self.url, {'search': 'smartphone'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Phone A'
    
    def test_search_case_insensitive(self, api_client):
        """
        Test search is case-insensitive.
        
        Expected behavior:
        - Returns results regardless of case
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        ProductFactory(name='MacBook Pro', category=category)
        
        # Act
        response1 = api_client.get(self.url, {'search': 'macbook'})
        response2 = api_client.get(self.url, {'search': 'MACBOOK'})
        response3 = api_client.get(self.url, {'search': 'MacBook'})
        
        # Assert
        assert len(response1.data['results']) == 1
        assert len(response2.data['results']) == 1
        assert len(response3.data['results']) == 1


@pytest.mark.django_db
class TestProductFilters:
    """
    Test suite for product filtering.
    
    Filters: category, price range, rating
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:product-list')
    
    def test_filter_by_category(self, api_client):
        """
        Test filtering products by category.
        
        Expected behavior:
        - Returns only products in specified category
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        electronics = CategoryFactory(name='Electronics')
        books = CategoryFactory(name='Books')
        
        product1 = ProductFactory(category=electronics, name='Laptop')
        product2 = ProductFactory(category=electronics, name='Phone')
        product3 = ProductFactory(category=books, name='Novel')
        
        # Act
        response = api_client.get(self.url, {'category': electronics.id})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        names = [p['name'] for p in response.data['results']]
        assert 'Laptop' in names
        assert 'Phone' in names
        assert 'Novel' not in names
    
    def test_filter_by_min_price(self, api_client):
        """
        Test filtering products by minimum price.
        
        Expected behavior:
        - Returns products with price >= min_price
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        product1 = ProductFactory(price=Decimal('500.00'), category=category)
        product2 = ProductFactory(price=Decimal('1000.00'), category=category)
        product3 = ProductFactory(price=Decimal('1500.00'), category=category)
        
        # Act
        response = api_client.get(self.url, {'min_price': '1000'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        prices = [Decimal(p['price']) for p in response.data['results']]
        assert all(price >= Decimal('1000') for price in prices)
    
    def test_filter_by_max_price(self, api_client):
        """
        Test filtering products by maximum price.
        
        Expected behavior:
        - Returns products with price <= max_price
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        product1 = ProductFactory(price=Decimal('500.00'), category=category)
        product2 = ProductFactory(price=Decimal('1000.00'), category=category)
        product3 = ProductFactory(price=Decimal('1500.00'), category=category)
        
        # Act
        response = api_client.get(self.url, {'max_price': '1000'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        prices = [Decimal(p['price']) for p in response.data['results']]
        assert all(price <= Decimal('1000') for price in prices)
    
    def test_filter_by_price_range(self, api_client):
        """
        Test filtering products by price range.
        
        Expected behavior:
        - Returns products within price range
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        product1 = ProductFactory(price=Decimal('500.00'), category=category)
        product2 = ProductFactory(price=Decimal('1000.00'), category=category)
        product3 = ProductFactory(price=Decimal('1500.00'), category=category)
        
        # Act
        response = api_client.get(self.url, {'min_price': '800', 'max_price': '1200'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert Decimal(response.data['results'][0]['price']) == Decimal('1000.00')
    
    def test_filter_by_min_rating(self, api_client):
        """
        Test filtering products by minimum rating.
        
        Expected behavior:
        - Returns products with avg rating >= min_rating
        """
        from tests.factories import ProductFactory, CategoryFactory, ReviewFactory, UserFactory
        
        # Arrange
        category = CategoryFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()
        
        product1 = ProductFactory(category=category, name='Product A')
        product2 = ProductFactory(category=category, name='Product B')
        product3 = ProductFactory(category=category, name='Product C')
        
        # Product 1: 5 stars
        ReviewFactory(product=product1, user=user1, rating=5)
        
        # Product 2: 3 stars
        ReviewFactory(product=product2, user=user2, rating=3)
        
        # Product 3: 4.5 average
        ReviewFactory(product=product3, user=user1, rating=5)
        ReviewFactory(product=product3, user=user2, rating=4)
        
        # Act
        response = api_client.get(self.url, {'min_rating': '4'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        names = [p['name'] for p in response.data['results']]
        assert 'Product A' in names
        assert 'Product C' in names
        assert 'Product B' not in names


@pytest.mark.django_db
class TestProductSorting:
    """
    Test suite for product sorting.
    
    Sort options: price, -price, name, -created_at
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:product-list')
    
    def test_sort_by_price_ascending(self, api_client):
        """
        Test sorting products by price (low to high).
        
        Expected behavior:
        - Returns products ordered by price ascending
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        ProductFactory(name='Expensive', price=Decimal('1500.00'), category=category)
        ProductFactory(name='Cheap', price=Decimal('500.00'), category=category)
        ProductFactory(name='Medium', price=Decimal('1000.00'), category=category)
        
        # Act
        response = api_client.get(self.url, {'ordering': 'price'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        prices = [Decimal(p['price']) for p in response.data['results']]
        assert prices == sorted(prices)
        assert response.data['results'][0]['name'] == 'Cheap'
    
    def test_sort_by_price_descending(self, api_client):
        """
        Test sorting products by price (high to low).
        
        Expected behavior:
        - Returns products ordered by price descending
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        ProductFactory(name='Expensive', price=Decimal('1500.00'), category=category)
        ProductFactory(name='Cheap', price=Decimal('500.00'), category=category)
        ProductFactory(name='Medium', price=Decimal('1000.00'), category=category)
        
        # Act
        response = api_client.get(self.url, {'ordering': '-price'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        prices = [Decimal(p['price']) for p in response.data['results']]
        assert prices == sorted(prices, reverse=True)
        assert response.data['results'][0]['name'] == 'Expensive'
    
    def test_sort_by_name(self, api_client):
        """
        Test sorting products by name (A-Z).
        
        Expected behavior:
        - Returns products ordered alphabetically
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        category = CategoryFactory()
        ProductFactory(name='Zebra', category=category)
        ProductFactory(name='Apple', category=category)
        ProductFactory(name='Mango', category=category)
        
        # Act
        response = api_client.get(self.url, {'ordering': 'name'})
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        names = [p['name'] for p in response.data['results']]
        assert names == sorted(names)
        assert names[0] == 'Apple'


@pytest.mark.django_db
class TestCombinedFilters:
    """
    Test suite for combined search and filters.
    
    Tests multiple filters working together.
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('products:product-list')
    
    def test_search_and_category_filter(self, api_client):
        """
        Test search combined with category filter.
        
        Expected behavior:
        - Returns products matching search AND in category
        """
        from tests.factories import ProductFactory, CategoryFactory
        
        # Arrange
        electronics = CategoryFactory(name='Electronics')
        books = CategoryFactory(name='Books')
        
        ProductFactory(name='iPhone 15', category=electronics)
        ProductFactory(name='iPhone Case', category=electronics)
        ProductFactory(name='iPhone Guide Book', category=books)
        
        # Act
        response = api_client.get(self.url, {
            'search': 'iPhone',
            'category': electronics.id
        })
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        # Verify all results contain search term
        for product in response.data['results']:
            assert 'iPhone' in product['name']
        # Category filter is working (we got 2 results, not 3)
        # If category filter wasn't working, we'd get 3 results (including book)
    
    def test_all_filters_combined(self, api_client):
        """
        Test all filters working together.
        
        Expected behavior:
        - Returns products matching all criteria
        """
        from tests.factories import (
            ProductFactory, CategoryFactory, 
            ReviewFactory, UserFactory
        )
        
        # Arrange
        electronics = CategoryFactory(name='Electronics')
        user1 = UserFactory()
        user2 = UserFactory()
        
        # Product matching all criteria
        product1 = ProductFactory(
            name='Premium Laptop',
            price=Decimal('1200.00'),
            category=electronics
        )
        ReviewFactory(product=product1, user=user1, rating=5)
        
        # Product: wrong category
        product2 = ProductFactory(
            name='Premium Tablet',
            price=Decimal('1100.00'),
            category=CategoryFactory(name='Other')
        )
        ReviewFactory(product=product2, user=user1, rating=5)
        
        # Product: too expensive
        product3 = ProductFactory(
            name='Premium Phone',
            price=Decimal('2000.00'),
            category=electronics
        )
        ReviewFactory(product=product3, user=user2, rating=5)
        
        # Product: low rating
        product4 = ProductFactory(
            name='Premium Watch',
            price=Decimal('1000.00'),
            category=electronics
        )
        ReviewFactory(product=product4, user=user1, rating=2)
        
        # Act
        response = api_client.get(self.url, {
            'search': 'Premium',
            'category': electronics.id,
            'min_price': '1000',
            'max_price': '1500',
            'min_rating': '4',
            'ordering': 'price'
        })
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Premium Laptop'