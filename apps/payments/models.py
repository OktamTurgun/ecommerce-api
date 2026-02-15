"""
Payment Models

Payment processing for orders using Stripe.
Tracks payment intents, confirmations, and status.
"""
import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class Payment(models.Model):
    """
    Payment model.
    
    Tracks payment transactions for orders.
    
    Features:
    - Order reference
    - Stripe payment intent ID
    - Payment amount
    - Payment status
    - Payment method details
    - Timestamps
    
    Examples:
        # Create payment
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            currency='usd',
            stripe_payment_intent_id='pi_xxx'
        )
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCEEDED', 'Succeeded'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payment',
        help_text='Order associated with this payment'
    )
    
    # Stripe Information
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='Stripe Payment Intent ID'
    )
    
    stripe_client_secret = models.CharField(
        max_length=255,
        blank=True,
        help_text='Stripe client secret for frontend'
    )
    
    # Payment Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Payment amount'
    )
    
    currency = models.CharField(
        max_length=3,
        default='usd',
        help_text='Payment currency (ISO code)'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Payment status'
    )
    
    # Payment Method (optional)
    payment_method_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Payment method type (card, bank, etc.)'
    )
    
    payment_method_last4 = models.CharField(
        max_length=4,
        blank=True,
        help_text='Last 4 digits of card/account'
    )
    
    # Metadata
    failure_message = models.TextField(
        blank=True,
        help_text='Error message if payment failed'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional payment metadata'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when payment succeeded'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        """String representation."""
        return f'Payment {str(self.id)[:8]} - {self.status} - ${self.amount}'
    
    @property
    def is_paid(self):
        """Check if payment is successful."""
        return self.status == 'SUCCEEDED'