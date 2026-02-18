"""
Tests for Review API Endpoints - TDD Approach

This module tests Review CRUD operations via REST API.

Endpoints:
- GET    /api/products/{id}/reviews/     - List product reviews
- POST   /api/products/{id}/reviews/     - Create review
- GET    /api/reviews/{id}/              - Get review detail
- PATCH  /api/reviews/{id}/              - Update own review
- DELETE /api/reviews/{id}/              - Delete own review

Following TDD: Write tests FIRST, then implement API.
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestProductReviewsList:
    """
    Test suite for Product Reviews List endpoint.
    
    Endpoint: GET /api/products/{id}/reviews/
    Permission: AllowAny
    """
    
    def test_list_product_reviews(self, api_client):
        """
        Test listing reviews for a product.
        
        Expected behavior:
        - Returns 200 OK
        - Shows all reviews for product
        """
        from tests.factories import ProductFactory, ReviewFactory, UserFactory
        
        # Arrange
        product = ProductFactory()
        user1 = UserFactory()
        user2 = UserFactory()
        
        review1 = ReviewFactory(product=product, user=user1, rating=5, comment='Great!')
        review2 = ReviewFactory(product=product, user=user2, rating=4, comment='Good')
        
        url = reverse('products:product-reviews-list', kwargs={'product_pk': product.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_list_product_reviews_with_average_rating(self, api_client):
        """
        Test product reviews include average rating.
        
        Expected behavior:
        - Response includes average_rating
        - Response includes review_count
        """
        from tests.factories import ProductFactory, ReviewFactory
        
        # Arrange
        product = ProductFactory()
        ReviewFactory(product=product, rating=5)
        ReviewFactory(product=product, rating=3)
        
        url = reverse('products:product-reviews-list', kwargs={'product_pk': product.id})
        
        # Act
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'average_rating' in response.data
        assert 'review_count' in response.data
        assert response.data['average_rating'] == 4.0
        assert response.data['review_count'] == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCreateReview:
    """
    Test suite for Create Review endpoint.
    
    Endpoint: POST /api/products/{id}/reviews/
    Permission: IsAuthenticated
    """
    
    def test_create_review_success(self, authenticated_client):
        """
        Test creating a review successfully.
        
        Expected behavior:
        - Returns 201 Created
        - Review created in database
        """
        from tests.factories import ProductFactory
        from apps.users.models import User
        from apps.reviews.models import Review
        
        # Arrange
        user = User.objects.first()
        product = ProductFactory()
        
        url = reverse('products:product-reviews-list', kwargs={'product_pk': product.id})
        data = {
            'rating': 5,
            'comment': 'Excellent product!'
        }
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == 5
        assert response.data['comment'] == 'Excellent product!'
        
        # Verify created
        assert Review.objects.filter(user=user, product=product).exists()
    
    def test_create_review_unauthenticated(self, api_client):
        """
        Test creating review without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory()
        url = reverse('products:product-reviews-list', kwargs={'product_pk': product.id})
        data = {'rating': 5, 'comment': 'Great!'}
        
        # Act
        response = api_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_review_duplicate(self, authenticated_client):
        """
        Test creating duplicate review (same user, same product).
        
        Expected behavior:
        - Returns 400 Bad Request
        - Error message
        """
        from tests.factories import ProductFactory, ReviewFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        product = ProductFactory()
        ReviewFactory(user=user, product=product, rating=4)  # Already reviewed
        
        url = reverse('products:product-reviews-list', kwargs={'product_pk': product.id})
        data = {'rating': 5, 'comment': 'New review'}
        
        # Act
        response = authenticated_client.post(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_create_review_invalid_rating(self, authenticated_client):
        """
        Test creating review with invalid rating.
        
        Expected behavior:
        - Returns 400 Bad Request
        """
        from tests.factories import ProductFactory
        
        # Arrange
        product = ProductFactory()
        url = reverse('products:product-reviews-list', kwargs={'product_pk': product.id})
        
        # Test rating too high
        response = authenticated_client.post(url, {'rating': 6}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test rating too low
        response = authenticated_client.post(url, {'rating': 0}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestUpdateReview:
    """
    Test suite for Update Review endpoint.
    
    Endpoint: PATCH /api/reviews/{id}/
    Permission: IsAuthenticated (own reviews only)
    """
    
    def test_update_own_review(self, authenticated_client):
        """
        Test updating own review.
        
        Expected behavior:
        - Returns 200 OK
        - Review updated
        """
        from tests.factories import ProductFactory, ReviewFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        product = ProductFactory()
        review = ReviewFactory(user=user, product=product, rating=3, comment='OK')
        
        url = reverse('reviews:review-detail', kwargs={'pk': review.id})
        data = {'rating': 5, 'comment': 'Actually great!'}
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['rating'] == 5
        assert response.data['comment'] == 'Actually great!'
        
        review.refresh_from_db()
        assert review.rating == 5
    
    def test_update_other_user_review(self, authenticated_client):
        """
        Test updating another user's review.
        
        Expected behavior:
        - Returns 404 Not Found (or 403 Forbidden)
        """
        from tests.factories import UserFactory, ReviewFactory
        
        # Arrange
        other_user = UserFactory()
        review = ReviewFactory(user=other_user, rating=5)
        
        url = reverse('reviews:review-detail', kwargs={'pk': review.id})
        data = {'rating': 1}
        
        # Act
        response = authenticated_client.patch(url, data, format='json')
        
        # Assert
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestDeleteReview:
    """
    Test suite for Delete Review endpoint.
    
    Endpoint: DELETE /api/reviews/{id}/
    Permission: IsAuthenticated (own reviews only)
    """
    
    def test_delete_own_review(self, authenticated_client):
        """
        Test deleting own review.
        
        Expected behavior:
        - Returns 204 No Content
        - Review deleted
        """
        from tests.factories import ReviewFactory
        from apps.users.models import User
        from apps.reviews.models import Review
        
        # Arrange
        user = User.objects.first()
        review = ReviewFactory(user=user, rating=5)
        review_id = review.id
        
        url = reverse('reviews:review-detail', kwargs={'pk': review.id})
        
        # Act
        response = authenticated_client.delete(url)
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(id=review_id).exists()
    
    def test_delete_other_user_review(self, authenticated_client):
        """
        Test deleting another user's review.
        
        Expected behavior:
        - Returns 404 Not Found (or 403 Forbidden)
        """
        from tests.factories import UserFactory, ReviewFactory
        
        # Arrange
        other_user = UserFactory()
        review = ReviewFactory(user=other_user, rating=5)
        
        url = reverse('reviews:review-detail', kwargs={'pk': review.id})
        
        # Act
        response = authenticated_client.delete(url)
        
        # Assert
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]