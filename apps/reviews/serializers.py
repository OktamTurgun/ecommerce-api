"""
Review Serializers

Serializers for Review model and product reviews.
"""
from rest_framework import serializers
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    
    Features:
    - Review details
    - User information
    - Product information
    """
    
    user_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'user_name',
            'product',
            'product_name',
            'rating',
            'comment',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'product', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get user's full name or email."""
        return obj.user.get_full_name() or obj.user.email


class CreateReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a review.
    
    Input: rating, comment
    Validates: duplicate review
    """
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    def validate(self, data):
        """
        Validate review creation.
        
        Checks:
        - User hasn't already reviewed this product
        """
        request = self.context.get('request')
        product = self.context.get('product')
        
        if Review.objects.filter(user=request.user, product=product).exists():
            raise serializers.ValidationError(
                'You have already reviewed this product.'
            )
        
        return data
    
    def create(self, validated_data):
        """
        Create review with user and product from context.
        """
        request = self.context.get('request')
        product = self.context.get('product')
        
        review = Review.objects.create(
            user=request.user,
            product=product,
            **validated_data
        )
        
        return review


class ProductReviewsSerializer(serializers.Serializer):
    """
    Serializer for product reviews list with metadata.
    
    Includes:
    - Reviews list
    - Average rating
    - Review count
    """
    
    reviews = ReviewSerializer(many=True)
    average_rating = serializers.FloatField()
    review_count = serializers.IntegerField()