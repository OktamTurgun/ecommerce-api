"""
Stripe Service Layer

Handles Stripe API integration for payment processing.
"""
import stripe
from django.conf import settings
from decimal import Decimal

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """
    Service class for Stripe API operations.
    """
    
    @staticmethod
    def create_payment_intent(amount, currency='usd', metadata=None):
        """
        Create a Stripe PaymentIntent.
        
        Args:
            amount (Decimal): Payment amount
            currency (str): Currency code (default: 'usd')
            metadata (dict): Additional metadata
        
        Returns:
            dict: PaymentIntent data
        """
        # Convert amount to cents (Stripe uses smallest currency unit)
        amount_cents = int(amount * 100)
        
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            return {
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': amount,
                'currency': currency,
                'status': payment_intent.status,
            }
        
        except stripe.error.StripeError as e:
            raise Exception(f'Stripe error: {str(e)}')
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """
        Retrieve a Stripe PaymentIntent.
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID
        
        Returns:
            stripe.PaymentIntent: PaymentIntent object
        """
        try:
            return stripe.PaymentIntent.retrieve(payment_intent_id)
        
        except stripe.error.StripeError as e:
            raise Exception(f'Stripe error: {str(e)}')
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """
        Confirm a Stripe PaymentIntent.
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID
        
        Returns:
            stripe.PaymentIntent: Confirmed PaymentIntent
        """
        try:
            return stripe.PaymentIntent.confirm(payment_intent_id)
        
        except stripe.error.StripeError as e:
            raise Exception(f'Stripe error: {str(e)}')
    
    @staticmethod
    def cancel_payment_intent(payment_intent_id):
        """
        Cancel a Stripe PaymentIntent.
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID
        
        Returns:
            stripe.PaymentIntent: Cancelled PaymentIntent
        """
        try:
            return stripe.PaymentIntent.cancel(payment_intent_id)
        
        except stripe.error.StripeError as e:
            raise Exception(f'Stripe error: {str(e)}')