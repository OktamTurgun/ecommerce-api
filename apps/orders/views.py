"""
Order Views

API ViewSets for Order model.
Provides order management and creation from cart.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.orders.models import Order
from apps.orders.serializers import (
    OrderSerializer,
    CreateOrderSerializer
)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Order operations.
    
    Endpoints:
    - GET    /api/orders/         - List user's orders
    - POST   /api/orders/         - Create order from cart
    - GET    /api/orders/{id}/    - Get order detail
    - POST   /api/orders/{id}/cancel/ - Cancel order
    
    Permissions:
    - IsAuthenticated (users can only see/manage their own orders)
    
    Features:
    - List user's orders (newest first)
    - Create order from cart
    - View order details
    - Cancel pending orders
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        """
        Get orders for current user only.
        
        Returns:
            QuerySet: User's orders with related items
        """
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Create order from cart.
        
        Endpoint: POST /api/orders/
        
        Body:
            {
                "shipping_address": "123 Main St",
                "shipping_city": "New York",
                "shipping_postal_code": "10001",
                "shipping_country": "USA",
                "notes": "Leave at door"
            }
        
        Returns:
            201 Created with order details
        """
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Create order
        order = serializer.save()
        
        # Return order details
        order_serializer = self.get_serializer(order)
        return Response(
            order_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order.
        
        Endpoint: POST /api/orders/{id}/cancel/
        
        Rules:
        - Only PENDING or PROCESSING orders can be cancelled
        - SHIPPED or DELIVERED orders cannot be cancelled
        
        Returns:
            200 OK with updated order
        """
        order = self.get_object()
        
        # Check if order can be cancelled
        if order.status in ['SHIPPED', 'DELIVERED']:
            return Response(
                {
                    'error': f'Cannot cancel order with status {order.status}. '
                            'Only PENDING or PROCESSING orders can be cancelled.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already cancelled
        if order.status == 'CANCELLED':
            return Response(
                {'error': 'Order is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel order
        order.status = 'CANCELLED'
        order.save()
        
        # Return updated order
        serializer = self.get_serializer(order)
        return Response(serializer.data)