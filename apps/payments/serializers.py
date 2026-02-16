"""
Payment Serializers

Serializers for Payment model and Stripe integration.
"""
from rest_framework import serializers
from apps.payments.models import Payment
from apps.orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment model.
    
    Features:
    - Payment details
    - Order information
    - Stripe payment intent ID
    """
    
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'stripe_payment_intent_id',
            'amount',
            'currency',
            'status',
            'payment_method_type',
            'payment_method_last4',
            'failure_message',
            'created_at',
            'updated_at',
            'paid_at',
        ]
        read_only_fields = fields


class CreatePaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for creating Stripe payment intent.
    
    Input: order_id
    Output: client_secret, payment_intent_id
    """
    
    order_id = serializers.UUIDField(required=True)
    
    def validate_order_id(self, value):
        """
        Just validate UUID format.
        Order existence and ownership checked in view (for proper 404).
        """
        return value


class ConfirmPaymentSerializer(serializers.Serializer):
    """
    Serializer for confirming payment.
    
    Input: payment_intent_id
    Output: payment details
    """
    
    payment_intent_id = serializers.CharField(required=True)
    
    def validate_payment_intent_id(self, value):
        """
        Just validate format.
        Payment existence checked in view (for proper 404).
        """
        return value