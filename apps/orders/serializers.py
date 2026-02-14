"""
Order Serializers

Serializers for Order and OrderItem models.
Handles order creation, display, and updates.
"""
from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem.
    
    Features:
    - Product snapshot data (read-only)
    - Subtotal calculation
    """
    
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_sku',
            'price',
            'quantity',
            'subtotal',
            'created_at',
        ]
        read_only_fields = fields  # All fields read-only in responses


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order.
    
    Features:
    - Order items (nested, read-only)
    - Total amount
    - Total items
    - User info
    """
    
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'user_email',
            'status',
            'items',
            'total_amount',
            'total_items',
            'shipping_address',
            'shipping_city',
            'shipping_postal_code',
            'shipping_country',
            'notes',
            'tracking_number',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'user_email',
            'status',
            'items',
            'total_amount',
            'total_items',
            'tracking_number',
            'created_at',
            'updated_at',
        ]


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating order from cart.
    
    Features:
    - Shipping information (required)
    - Notes (optional)
    - Validates cart not empty
    - Validates stock availability
    - Creates order and order items
    - Clears cart
    """
    
    shipping_address = serializers.CharField(max_length=255, required=True)
    shipping_city = serializers.CharField(max_length=100, required=True)
    shipping_postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    shipping_country = serializers.CharField(max_length=100, required=False, default='USA')
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validate order creation.
        
        Checks:
        - Cart is not empty
        - All items have sufficient stock
        """
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context required")
        
        # Get user's cart
        from apps.cart.models import Cart
        cart = Cart.get_or_create_for_request(request)
        
        # Check cart not empty
        if cart.items.count() == 0:
            raise serializers.ValidationError({
                'cart': 'Cart is empty. Add items before creating order.'
            })
        
        # Validate stock for all items
        for cart_item in cart.items.all():
            if cart_item.product.stock < cart_item.quantity:
                raise serializers.ValidationError({
                    'stock': f'Insufficient stock for {cart_item.product.name}. '
                            f'Available: {cart_item.product.stock}, Requested: {cart_item.quantity}'
                })
            
            if not cart_item.product.is_active:
                raise serializers.ValidationError({
                    'product': f'Product {cart_item.product.name} is no longer available.'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Create order from cart.
        
        Steps:
        1. Create order
        2. Create order items from cart items (with snapshots)
        3. Reduce product stock
        4. Clear cart
        """
        request = self.context.get('request')
        
        # Get cart
        from apps.cart.models import Cart
        cart = Cart.get_or_create_for_request(request)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=validated_data.get('shipping_address'),
            shipping_city=validated_data.get('shipping_city'),
            shipping_postal_code=validated_data.get('shipping_postal_code', ''),
            shipping_country=validated_data.get('shipping_country', 'USA'),
            notes=validated_data.get('notes', '')
        )
        
        # Create order items and reduce stock
        for cart_item in cart.items.all():
            # Create order item with product snapshot
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                price=cart_item.price_at_add,
                quantity=cart_item.quantity
            )
            
            # Reduce stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
        
        # Clear cart
        cart.items.all().delete()
        
        return order