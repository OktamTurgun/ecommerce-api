"""
Tests for Review Models - TDD Approach

This module tests Review model functionality.
Product review and rating system.

Following TDD: Write tests FIRST, then implement models.
"""

import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal


@pytest.mark.django_db
class TestReviewModel:
    """
    Test suite for Review model.

    Tests review creation, ratings, and validations.
    """

    def test_review_creation(self):
        """
        Test creating a review.

        Expected behavior:
        - Review created with user and product
        - Rating saved
        - Comment saved
        """
        from tests.factories import UserFactory, ProductFactory, ReviewFactory

        # Arrange
        user = UserFactory()
        product = ProductFactory()

        # Act
        review = ReviewFactory(
            user=user, product=product, rating=5, comment="Great product!"
        )

        # Assert
        assert review.user == user
        assert review.product == product
        assert review.rating == 5
        assert review.comment == "Great product!"
        assert review.created_at is not None

    def test_review_str_representation(self):
        """
        Test string representation of review.

        Expected: "Rating by User - Product"
        """
        from tests.factories import ReviewFactory, UserFactory, ProductFactory

        # Arrange
        user = UserFactory(first_name="John")
        product = ProductFactory(name="iPhone")
        review = ReviewFactory(user=user, product=product, rating=5)

        # Act & Assert
        assert "John" in str(review) or user.email in str(review)
        assert "iPhone" in str(review)

    def test_review_rating_choices(self):
        """
        Test rating is within 1-5 range.

        Expected: Rating between 1 and 5
        """
        from tests.factories import ReviewFactory

        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            review = ReviewFactory(rating=rating)
            assert review.rating == rating

    def test_review_rating_validation_too_low(self):
        """
        Test rating validation for values below 1.

        Expected: ValidationError
        """
        from tests.factories import ReviewFactory
        from apps.reviews.models import Review

        # Act & Assert
        with pytest.raises(ValidationError):
            review = Review(rating=0, comment="Test")  # Invalid!
            review.full_clean()

    def test_review_rating_validation_too_high(self):
        """
        Test rating validation for values above 5.

        Expected: ValidationError
        """
        from tests.factories import ReviewFactory
        from apps.reviews.models import Review

        # Act & Assert
        with pytest.raises(ValidationError):
            review = Review(rating=6, comment="Test")  # Invalid!
            review.full_clean()

    def test_one_review_per_user_per_product(self):
        """
        Test unique constraint: one review per user per product.

        Expected: Cannot create duplicate review
        """
        from tests.factories import UserFactory, ProductFactory, ReviewFactory

        # Arrange
        user = UserFactory()
        product = ProductFactory()
        ReviewFactory(user=user, product=product, rating=5)

        # Act & Assert
        with pytest.raises(Exception):  # IntegrityError
            ReviewFactory(user=user, product=product, rating=3)

    def test_cascade_delete_on_user_delete(self):
        """
        Test review deleted when user deleted.

        Expected: CASCADE delete
        """
        from tests.factories import UserFactory, ReviewFactory
        from apps.reviews.models import Review

        # Arrange
        user = UserFactory()
        review = ReviewFactory(user=user)
        review_id = review.id

        # Act
        user.delete()

        # Assert
        assert not Review.objects.filter(id=review_id).exists()

    def test_cascade_delete_on_product_delete(self):
        """
        Test review deleted when product deleted.

        Expected: CASCADE delete
        """
        from tests.factories import ProductFactory, ReviewFactory
        from apps.reviews.models import Review

        # Arrange
        product = ProductFactory()
        review = ReviewFactory(product=product)
        review_id = review.id

        # Act
        product.delete()

        # Assert
        assert not Review.objects.filter(id=review_id).exists()

    def test_review_comment_optional(self):
        """
        Test comment is optional.

        Expected: Review can be created without comment
        """
        from tests.factories import ReviewFactory

        # Act
        review = ReviewFactory(rating=5, comment="")

        # Assert
        assert review.comment == ""
        assert review.rating == 5


@pytest.mark.django_db
class TestProductRatingCalculation:
    """
    Test product rating calculations.
    """

    def test_product_average_rating_single_review(self):
        """
        Test average rating with single review.

        Expected: Average = review rating
        """
        from tests.factories import ProductFactory, ReviewFactory

        # Arrange
        product = ProductFactory()
        ReviewFactory(product=product, rating=4)

        # Act
        average = product.average_rating

        # Assert
        assert average == 4.0

    def test_product_average_rating_multiple_reviews(self):
        """
        Test average rating with multiple reviews.

        Expected: Correct average calculation
        """
        from tests.factories import ProductFactory, ReviewFactory

        # Arrange
        product = ProductFactory()
        ReviewFactory(product=product, rating=5)
        ReviewFactory(product=product, rating=4)
        ReviewFactory(product=product, rating=3)

        # Act
        average = product.average_rating

        # Assert
        assert average == 4.0  # (5 + 4 + 3) / 3 = 4.0

    def test_product_review_count(self):
        """
        Test review count for product.

        Expected: Correct count
        """
        from tests.factories import ProductFactory, ReviewFactory

        # Arrange
        product = ProductFactory()
        ReviewFactory(product=product, rating=5)
        ReviewFactory(product=product, rating=4)
        ReviewFactory(product=product, rating=3)

        # Act
        count = product.review_count

        # Assert
        assert count == 3

    def test_product_no_reviews(self):
        """
        Test product with no reviews.

        Expected: Average = 0, Count = 0
        """
        from tests.factories import ProductFactory

        # Arrange
        product = ProductFactory()

        # Act & Assert
        assert product.average_rating == 0
        assert product.review_count == 0
