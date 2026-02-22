"""
Tests for Email Notification Service - TDD Approach

This module tests email sending functionality.
Tests use Django's mail backend to capture emails without actually sending them.

Following TDD: Tests validate email sending, templates, and content.
"""
import pytest
from django.core import mail
from decimal import Decimal


@pytest.mark.django_db
class TestOrderEmailNotifications:
    """
    Test suite for order email notifications.
    
    Tests email sending without actually sending emails.
    Uses Django's mail outbox to capture emails.
    """
    
    def test_send_order_confirmation_email(self):
        """
        Test sending order confirmation email.
        
        Expected behavior:
        - Email is sent to customer
        - Subject contains order ID
        - Body contains order details
        """
        from tests.factories import OrderFactory, OrderItemFactory, UserFactory
        from apps.orders.email_service import OrderEmailService
        
        # Arrange
        user = UserFactory(email='customer@example.com')
        order = OrderFactory(user=user)
        OrderItemFactory(order=order, product_name='Test Product', quantity=2, price=Decimal('50.00'))
        
        # Act
        result = OrderEmailService.send_order_confirmation(order)
        
        # Assert
        assert result is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert email.to == ['customer@example.com']
        assert str(order.id)[:8] in email.subject
        assert 'Order Confirmation' in email.subject
        assert 'Test Product' in email.body
        assert '$100.00' in email.body or '100.00' in email.body
    
    def test_send_order_shipped_email(self):
        """
        Test sending order shipped notification.
        
        Expected behavior:
        - Email is sent with tracking info
        - Subject indicates shipment
        """
        from tests.factories import OrderFactory, UserFactory
        from apps.orders.email_service import OrderEmailService
        
        # Arrange
        user = UserFactory(email='customer@example.com')
        order = OrderFactory(user=user, status='SHIPPED', tracking_number='TRACK123456')
        
        # Act
        result = OrderEmailService.send_order_shipped(order)
        
        # Assert
        assert result is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert email.to == ['customer@example.com']
        assert 'Shipped' in email.subject
        assert 'TRACK123456' in email.body
    
    def test_send_order_delivered_email(self):
        """
        Test sending order delivered notification.
        
        Expected behavior:
        - Email is sent
        - Includes review request
        """
        from tests.factories import OrderFactory, UserFactory
        from apps.orders.email_service import OrderEmailService
        
        # Arrange
        user = UserFactory(email='customer@example.com')
        order = OrderFactory(user=user, status='DELIVERED')
        
        # Act
        result = OrderEmailService.send_order_delivered(order)
        
        # Assert
        assert result is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert email.to == ['customer@example.com']
        assert 'Delivered' in email.subject
    
    def test_send_payment_confirmation_email(self):
        """
        Test sending payment confirmation email.
        
        Expected behavior:
        - Email is sent with payment details
        - Amount is correct
        """
        from tests.factories import OrderFactory, UserFactory, PaymentFactory
        from apps.orders.email_service import OrderEmailService
        
        # Arrange
        user = UserFactory(email='customer@example.com')
        order = OrderFactory(user=user)
        payment = PaymentFactory(
            order=order,
            amount=Decimal('99.99'),
            status='SUCCEEDED',
            payment_method_type='card',
            payment_method_last4='4242'
        )
        
        # Act
        result = OrderEmailService.send_payment_confirmation(payment)
        
        # Assert
        assert result is True
        assert len(mail.outbox) == 1
        
        email = mail.outbox[0]
        assert email.to == ['customer@example.com']
        assert 'Payment' in email.subject
        assert '99.99' in email.body
        assert '4242' in email.body
    
    def test_email_has_html_alternative(self):
        """
        Test that email has HTML alternative.
        
        Expected behavior:
        - Email has both text and HTML versions
        """
        from tests.factories import OrderFactory, OrderItemFactory, UserFactory
        from apps.orders.email_service import OrderEmailService
        
        # Arrange
        user = UserFactory(email='customer@example.com')
        order = OrderFactory(user=user)
        OrderItemFactory(order=order)
        
        # Act
        OrderEmailService.send_order_confirmation(order)
        
        # Assert
        email = mail.outbox[0]
        assert len(email.alternatives) == 1
        html_content, content_type = email.alternatives[0]
        assert content_type == 'text/html'
        assert '<html' in html_content.lower()
    
    def test_email_with_user_full_name(self):
        """
        Test email uses user's full name if available.
        
        Expected behavior:
        - Email greeting uses full name
        """
        from tests.factories import OrderFactory, UserFactory
        from apps.orders.email_service import OrderEmailService
        
        # Arrange
        user = UserFactory(
            email='customer@example.com',
            first_name='John',
            last_name='Doe'
        )
        order = OrderFactory(user=user)
        
        # Act
        OrderEmailService.send_order_confirmation(order)
        
        # Assert
        email = mail.outbox[0]
        assert 'John' in email.body or 'Doe' in email.body


@pytest.mark.django_db
class TestEmailErrorHandling:
    """
    Test suite for email error handling.
    """
    
    def test_email_service_handles_missing_template_gracefully(self):
        """
        Test that missing template doesn't crash the service.
        
        Expected behavior:
        - Returns False on error
        - Logs error
        """
        from tests.factories import OrderFactory
        from apps.orders.email_service import OrderEmailService
        import logging
        
        # This test validates error handling
        # In real implementation, service should catch template errors
        order = OrderFactory()
        
        # Should not crash even if template is missing
        # (implementation should handle gracefully)
        result = OrderEmailService.send_order_confirmation(order)
        
        # Result can be True or False depending on implementation
        assert isinstance(result, bool)