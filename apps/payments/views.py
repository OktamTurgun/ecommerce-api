"""
Payment Views

API ViewSets for Payment operations and Stripe integration.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.payments.models import Payment
from apps.payments.serializers import (
    PaymentSerializer,
    CreatePaymentIntentSerializer,
    ConfirmPaymentSerializer
)
from apps.payments.services import StripeService
from apps.orders.models import Order


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Payment operations.
    
    Endpoints:
    - GET  /api/payments/                    - List user's payments
    - GET  /api/payments/{id}/               - Get payment detail
    - POST /api/payments/create-intent/      - Create payment intent
    - POST /api/payments/confirm/            - Confirm payment
    
    Permissions:
    - IsAuthenticated (users can only see/manage their own payments)
    
    Features:
    - List user's payments
    - Create Stripe payment intent
    - Confirm payment
    - View payment details
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        """
        Get payments for current user's orders only.
        
        Returns:
            QuerySet: User's payments
        """
        return Payment.objects.filter(
            order__user=self.request.user
        ).select_related('order').order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def create_intent(self, request):
        """
        Create Stripe payment intent for an order.
        
        Endpoint: POST /api/payments/create-intent/
        
        Body:
            {
                "order_id": "uuid"
            }
        
        Returns:
            201 Created with payment intent details
        """
        serializer = CreatePaymentIntentSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Check if payment already exists
        if hasattr(order, 'payment'):
            payment = order.payment
            if payment.is_paid:
                return Response(
                    {'error': 'Order already paid'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Return existing payment intent
            return Response({
                'payment_intent_id': payment.stripe_payment_intent_id,
                'client_secret': payment.stripe_client_secret,
                'amount': str(payment.amount),
                'currency': payment.currency,
            })
        
        # Create Stripe payment intent
        try:
            payment_intent_data = StripeService.create_payment_intent(
                amount=order.total_amount,
                currency='usd',
                metadata={
                    'order_id': str(order.id),
                    'user_id': str(request.user.id),
                }
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Payment record
        payment = Payment.objects.create(
            order=order,
            stripe_payment_intent_id=payment_intent_data['id'],
            stripe_client_secret=payment_intent_data['client_secret'],
            amount=order.total_amount,
            currency='usd',
            status='PENDING'
        )
        
        return Response({
            'payment_intent_id': payment.stripe_payment_intent_id,
            'client_secret': payment.stripe_client_secret,
            'amount': str(payment.amount),
            'currency': payment.currency,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def confirm(self, request):
        """
        Confirm payment after Stripe processing.
        
        Endpoint: POST /api/payments/confirm/
        
        Body:
            {
                "payment_intent_id": "pi_xxx"
            }
        
        Returns:
            200 OK with payment details
        """
        serializer = ConfirmPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        # Get payment
        payment = get_object_or_404(
            Payment,
            stripe_payment_intent_id=payment_intent_id,
            order__user=request.user
        )
        
        # Retrieve payment intent from Stripe
        try:
            stripe_payment_intent = StripeService.retrieve_payment_intent(
                payment_intent_id
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update payment status based on Stripe status
        if stripe_payment_intent.status == 'succeeded':
            payment.status = 'SUCCEEDED'
            payment.paid_at = timezone.now()
            
            # Extract payment method details
            if stripe_payment_intent.charges.data:
                charge = stripe_payment_intent.charges.data[0]
                payment_method = charge.payment_method_details
                
                payment.payment_method_type = payment_method.type
                if payment_method.type == 'card':
                    payment.payment_method_last4 = payment_method.card.last4
            
            payment.save()
            
            # Update order status
            order = payment.order
            if order.status == 'PENDING':
                order.status = 'PROCESSING'
                order.save()
        
        elif stripe_payment_intent.status == 'processing':
            payment.status = 'PROCESSING'
            payment.save()
        
        elif stripe_payment_intent.status in ['requires_payment_method', 'canceled']:
            payment.status = 'FAILED'
            payment.failure_message = 'Payment failed or cancelled'
            payment.save()
        
        # Return payment details
        response_serializer = self.get_serializer(payment)
        return Response(response_serializer.data)
