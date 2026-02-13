"""
Cart Serializers

Serializers for Cart and CartItem models.
Handles cart display and item management.
"""
from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.products.models import Product


class CartItemProductSerializer(serializers.ModelSerializer):
    """
    Lightweight product serializer for cart items.
    """
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'stock', 'is_active']
        read_only_fields = fields


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem.
    
    Features:
    - Product details (nested, read-only)
    - Subtotal calculation
    - Stock validation
    """
    
    product_detail = CartItemProductSerializer(source='product', read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True)
    )
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_detail',
            'quantity',
            'price_at_add',
            'subtotal',
            'created_at',
        ]
        read_only_fields = ['id', 'price_at_add', 'subtotal', 'created_at']
        extra_kwargs = {
            'product': {'write_only': False}  # Show in response
        }
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
    
    def validate(self, data):
        """
        Validate cart item.
        
        Checks:
        - Product is active
        - Enough stock available
        """
        # Get product from data or instance (for updates)
        product = data.get('product')
        if not product and self.instance:
            product = self.instance.product
        
        quantity = data.get('quantity', 1)
        
        # Validate product if provided
        if product:
            # Check product is active
            if not product.is_active:
                raise serializers.ValidationError({
                    'product': 'This product is not available'
                })
            
            # Check stock
            if product.stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {product.stock} items in stock'
                })
        
        return data


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart.
    
    Features:
    - Items list (nested)
    - Total items count
    - Total price
    """
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total_items',
            'total_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields