"""
Review Models

Product review and rating system.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Review model.
    
    Represents a product review with rating and comment.
    
    Features:
    - User reference
    - Product reference
    - Rating (1-5 stars)
    - Comment (optional)
    - Timestamps
    - Unique constraint (one review per user per product)
    
    Examples:
        # Create review
        review = Review.objects.create(
            user=user,
            product=product,
            rating=5,
            comment='Excellent product!'
        )
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='User who wrote the review'
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Product being reviewed'
    )
    
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ],
        help_text='Rating from 1 to 5 stars'
    )
    
    comment = models.TextField(
        blank=True,
        help_text='Review comment (optional)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'product']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['rating']),
        ]
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        """String representation."""
        return f'{self.rating}★ by {self.user.get_full_name() or self.user.email} - {self.product.name}'