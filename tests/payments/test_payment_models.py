"""
Tests for Payment Models - TDD Approach

This module tests Payment model functionality.
Payment processing for orders using Stripe.

Following TDD: Write tests FIRST, then implement models.
"""
import pytest
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone


@pytest.mark.django_db
class TestPaymentModel:
    """
    Test suite for Payment model.
    
    Tests payment creation, status tracking, and Stripe integration.
    """
    
    def test_payment_creation(self):
        """
        Test creating a payment.
        
        Expected behavior:
        - Payment created with order
        - Status defaults to PENDING
        - Stripe payment intent ID saved
        """
        from tests.factories import OrderFactory, PaymentFactory
        
        # Arrange
        order = OrderFactory()
        
        # Act
        payment = PaymentFactory(
            order=order,
            amount=Decimal('999.99'),
            stripe_payment_intent_id='pi_test123'
        )
        
        # Assert
        assert payment.order == order
        assert payment.amount == Decimal('999.99')
        assert payment.status == 'PENDING'
        assert payment.stripe_payment_intent_id == 'pi_test123'
        assert payment.currency == 'usd'
    
    def test_payment_str_representation(self):
        """
        Test string representation of payment.
        
        Expected: "Payment ID - Status - $Amount"
        """
        from tests.factories import PaymentFactory
        
        # Arrange & Act
        payment = PaymentFactory(
            amount=Decimal('100.00'),
            status='SUCCEEDED'
        )
        
        # Assert
        assert 'Payment' in str(payment)
        assert 'SUCCEEDED' in str(payment)
        assert '$100.00' in str(payment)
    
    def test_payment_status_choices(self):
        """
        Test payment status choices.
        
        Expected: PENDING, PROCESSING, SUCCEEDED, FAILED, CANCELLED, REFUNDED
        """
        from apps.payments.models import Payment
        
        # Act
        statuses = [choice[0] for choice in Payment.STATUS_CHOICES]
        
        # Assert
        assert 'PENDING' in statuses
        assert 'PROCESSING' in statuses
        assert 'SUCCEEDED' in statuses
        assert 'FAILED' in statuses
        assert 'CANCELLED' in statuses
        assert 'REFUNDED' in statuses
    
    def test_is_paid_property_true(self):
        """
        Test is_paid property when payment succeeded.
        
        Expected: True
        """
        from tests.factories import PaymentFactory
        
        # Arrange
        payment = PaymentFactory(status='SUCCEEDED')
        
        # Act & Assert
        assert payment.is_paid is True
    
    def test_is_paid_property_false(self):
        """
        Test is_paid property when payment not succeeded.
        
        Expected: False
        """
        from tests.factories import PaymentFactory
        
        # Arrange
        payment = PaymentFactory(status='PENDING')
        
        # Act & Assert
        assert payment.is_paid is False
    
    def test_payment_order_relationship(self):
        """
        Test one-to-one relationship with order.
        
        Expected: One payment per order
        """
        from tests.factories import OrderFactory, PaymentFactory
        
        # Arrange
        order = OrderFactory()
        payment = PaymentFactory(order=order)
        
        # Act & Assert
        assert order.payment == payment
        assert payment.order == order
    
    def test_payment_cascade_delete_on_order_delete(self):
        """
        Test payment deleted when order deleted.
        
        Expected: CASCADE delete
        """
        from tests.factories import OrderFactory, PaymentFactory
        from apps.payments.models import Payment
        
        # Arrange
        order = OrderFactory()
        payment = PaymentFactory(order=order)
        payment_id = payment.id
        
        # Act
        order.delete()
        
        # Assert
        assert not Payment.objects.filter(id=payment_id).exists()
    
    def test_payment_with_payment_method_details(self):
        """
        Test payment with payment method details.
        
        Expected: Payment method type and last4 saved
        """
        from tests.factories import PaymentFactory
        
        # Arrange & Act
        payment = PaymentFactory(
            payment_method_type='card',
            payment_method_last4='4242'
        )
        
        # Assert
        assert payment.payment_method_type == 'card'
        assert payment.payment_method_last4 == '4242'
    
    def test_payment_status_update(self):
        """
        Test updating payment status.
        
        Expected: Status changes, updated_at changes
        """
        from tests.factories import PaymentFactory
        import time
        
        # Arrange
        payment = PaymentFactory(status='PENDING')
        old_updated_at = payment.updated_at
        
        time.sleep(0.01)
        
        # Act
        payment.status = 'SUCCEEDED'
        payment.paid_at = timezone.now()
        payment.save()
        
        # Assert
        payment.refresh_from_db()
        assert payment.status == 'SUCCEEDED'
        assert payment.paid_at is not None
        assert payment.updated_at > old_updated_at
    
    def test_payment_failure_message(self):
        """
        Test payment with failure message.
        
        Expected: Failure message saved when payment fails
        """
        from tests.factories import PaymentFactory
        
        # Arrange & Act
        payment = PaymentFactory(
            status='FAILED',
            failure_message='Insufficient funds'
        )
        
        # Assert
        assert payment.status == 'FAILED'
        assert payment.failure_message == 'Insufficient funds'


@pytest.mark.django_db
class TestPaymentBusinessLogic:
    """
    Test payment business logic and workflows.
    """
    
    def test_payment_workflow_pending_to_succeeded(self):
        """
        Test payment workflow from pending to succeeded.
        
        Expected: PENDING → PROCESSING → SUCCEEDED
        """
        from tests.factories import PaymentFactory
        
        # Arrange
        payment = PaymentFactory(status='PENDING')
        
        # Act & Assert: Workflow
        assert payment.status == 'PENDING'
        assert payment.is_paid is False
        
        payment.status = 'PROCESSING'
        payment.save()
        assert payment.status == 'PROCESSING'
        assert payment.is_paid is False
        
        payment.status = 'SUCCEEDED'
        payment.paid_at = timezone.now()
        payment.save()
        assert payment.status == 'SUCCEEDED'
        assert payment.is_paid is True
        assert payment.paid_at is not None
    
    def test_payment_failed_workflow(self):
        """
        Test payment failure workflow.
        
        Expected: PENDING → PROCESSING → FAILED
        """
        from tests.factories import PaymentFactory
        
        # Arrange
        payment = PaymentFactory(status='PENDING')
        
        # Act
        payment.status = 'PROCESSING'
        payment.save()
        
        payment.status = 'FAILED'
        payment.failure_message = 'Card declined'
        payment.save()
        
        # Assert
        assert payment.status == 'FAILED'
        assert payment.is_paid is False
        assert payment.failure_message == 'Card declined'
    
    def test_unique_stripe_payment_intent_id(self):
        """
        Test stripe_payment_intent_id is unique.
        
        Expected: Cannot create two payments with same intent ID
        """
        from tests.factories import PaymentFactory
        
        # Arrange
        PaymentFactory(stripe_payment_intent_id='pi_unique123')
        
        # Act & Assert
        with pytest.raises(Exception):  # IntegrityError
            PaymentFactory(stripe_payment_intent_id='pi_unique123')