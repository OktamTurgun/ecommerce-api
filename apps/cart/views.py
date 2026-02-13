"""
Cart Views

API ViewSets for Cart and CartItem models.
Provides cart management for both authenticated and anonymous users.
"""
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.cart.models import Cart, CartItem
from apps.cart.serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet for Cart operations.
    
    Endpoints:
    - GET    /api/cart/       - Get current cart
    - POST   /api/cart/clear/ - Clear cart
    
    Permissions:
    - AllowAny (works for authenticated and anonymous users)
    
    Features:
    - Session-based cart for anonymous users
    - User-based cart for authenticated users
    - Auto cart creation
    """
    
    permission_classes = [AllowAny]
    
    def retrieve(self, request):
        """
        Get current user's cart.
        
        Endpoint: GET /api/cart/
        
        Returns:
            Cart with all items, totals
        """
        # Get or create cart for current request
        cart = Cart.get_or_create_for_request(request)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Clear all items from cart.
        
        Endpoint: POST /api/cart/clear/
        
        Returns:
            Empty cart
        """
        # Get cart
        cart = Cart.get_or_create_for_request(request)
        
        # Delete all items
        cart.items.all().delete()
        
        # Return updated cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CartItem CRUD operations.
    
    Endpoints:
    - GET    /api/cart/items/        - List cart items
    - POST   /api/cart/items/        - Add item to cart
    - GET    /api/cart/items/{id}/   - Get item detail
    - PATCH  /api/cart/items/{id}/   - Update quantity
    - DELETE /api/cart/items/{id}/   - Remove item
    
    Permissions:
    - AllowAny (but users can only modify their own cart)
    
    Features:
    - Add to cart with stock validation
    - Update quantity (if same product added twice, increase quantity)
    - Remove from cart
    - Price snapshot on add
    """
    
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Get cart items for current user's cart.
        """
        cart = Cart.get_or_create_for_request(self.request)
        return CartItem.objects.filter(cart=cart).select_related('product')
    
    def create(self, request, *args, **kwargs):
        """
        Add item to cart.
        
        If product already in cart, increase quantity instead of creating new item.
        
        Endpoint: POST /api/cart/items/
        
        Body:
            {
                "product": "uuid",
                "quantity": 2
            }
        
        Returns:
            201 Created (new item) or 200 OK (quantity updated)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get cart
        cart = Cart.get_or_create_for_request(request)
        
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        
        # Check if product already in cart
        existing_item = cart.items.filter(product=product).first()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += quantity
            
            # Validate stock
            if existing_item.product.stock < existing_item.quantity:
                return Response(
                    {'quantity': f'Only {existing_item.product.stock} items in stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            existing_item.save()
            
            # Return updated item
            serializer = self.get_serializer(existing_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new cart item
        cart_item = serializer.save(
            cart=cart,
            price_at_add=product.get_price()  # Snapshot current price
        )
        
        return Response(
            self.get_serializer(cart_item).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update cart item quantity.
        
        Endpoint: PATCH /api/cart/items/{id}/
        
        Body:
            {
                "quantity": 5
            }
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Validate stock
        new_quantity = serializer.validated_data.get('quantity', instance.quantity)
        if instance.product.stock < new_quantity:
            return Response(
                {'quantity': f'Only {instance.product.stock} items in stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove item from cart.
        
        Endpoint: DELETE /api/cart/items/{id}/
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)