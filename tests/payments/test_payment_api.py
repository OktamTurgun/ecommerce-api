"""
Tests for Payment API Endpoints - TDD Approach

This module tests Payment API operations via REST API.

Endpoints:
- POST /api/payments/create-intent/     - Create Stripe payment intent
- POST /api/payments/confirm/           - Confirm payment
- GET  /api/payments/                   - List user's payments
- GET  /api/payments/{id}/              - Get payment detail

Following TDD: Write tests FIRST, then implement API.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestCreatePaymentIntent:
    """
    Test suite for Create Payment Intent endpoint.
    
    Endpoint: POST /api/payments/create-intent/
    Permission: IsAuthenticated
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('payments:payment-create-intent')
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_stripe, authenticated_client):
        """
        Test creating payment intent successfully.
        
        Expected behavior:
        - Returns 201 Created
        - Stripe PaymentIntent created
        - Payment record created
        - Client secret returned
        """
        from tests.factories import OrderFactory, OrderItemFactory, ProductFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user)
        product = ProductFactory(price=Decimal('999.99'))
        OrderItemFactory(order=order, product=product, quantity=1, price=Decimal('999.99'))
        
        # Mock Stripe response
        mock_stripe.return_value = MagicMock(
            id='pi_test123',
            client_secret='pi_test123_secret',
            amount=99999,  # Stripe uses cents
            currency='usd',
            status='requires_payment_method'
        )
        
        data = {
            'order_id': str(order.id)
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert 'client_secret' in response.data
        assert 'payment_intent_id' in response.data
        assert response.data['amount'] == '999.99'
        
        # Verify Payment created
        from apps.payments.models import Payment
        payment = Payment.objects.get(order=order)
        assert payment.stripe_payment_intent_id == 'pi_test123'
        assert payment.status == 'PENDING'
    
    def test_create_payment_intent_order_not_found(self, authenticated_client):
        """
        Test creating payment intent for non-existent order.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        import uuid
        
        # Act
        data = {'order_id': str(uuid.uuid4())}
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_payment_intent_other_user_order(self, authenticated_client):
        """
        Test creating payment intent for another user's order.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        from tests.factories import UserFactory, OrderFactory
        
        # Arrange
        other_user = UserFactory()
        other_order = OrderFactory(user=other_user)
        
        data = {'order_id': str(other_order.id)}
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_payment_intent_already_paid(self, authenticated_client):
        """
        Test creating payment intent for already paid order.
        
        Expected behavior:
        - Returns 400 Bad Request
        """
        from tests.factories import OrderFactory, PaymentFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user)
        PaymentFactory(order=order, status='SUCCEEDED')
        
        data = {'order_id': str(order.id)}
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestConfirmPayment:
    """
    Test suite for Confirm Payment endpoint.
    
    Endpoint: POST /api/payments/confirm/
    Permission: IsAuthenticated
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('payments:payment-confirm')
    
    @patch('stripe.PaymentIntent.retrieve')
    def test_confirm_payment_success(self, mock_stripe, authenticated_client):
        """
        Test confirming payment successfully.
        
        Expected behavior:
        - Returns 200 OK
        - Payment status updated to SUCCEEDED
        - Order status updated
        """
        from tests.factories import OrderFactory, PaymentFactory
        from apps.users.models import User
        from django.utils import timezone
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user, status='PENDING')
        payment = PaymentFactory(
            order=order,
            status='PROCESSING',
            stripe_payment_intent_id='pi_test123'
        )
        
        # Mock Stripe response
        mock_stripe.return_value = MagicMock(
            id='pi_test123',
            status='succeeded',
            charges=MagicMock(
                data=[
                    MagicMock(
                        payment_method_details=MagicMock(
                            type='card',
                            card=MagicMock(last4='4242')
                        )
                    )
                ]
            )
        )
        
        data = {
            'payment_intent_id': 'pi_test123'
        }
        
        # Act
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'SUCCEEDED'
        
        # Verify Payment updated
        payment.refresh_from_db()
        assert payment.status == 'SUCCEEDED'
        assert payment.payment_method_type == 'card'
        assert payment.payment_method_last4 == '4242'
        assert payment.paid_at is not None
        
        # Verify Order updated
        order.refresh_from_db()
        assert order.status == 'PROCESSING'
    
    def test_confirm_payment_not_found(self, authenticated_client):
        """
        Test confirming non-existent payment.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        # Act
        data = {'payment_intent_id': 'pi_nonexistent'}
        response = authenticated_client.post(self.url, data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestPaymentList:
    """
    Test suite for Payment List endpoint.
    
    Endpoint: GET /api/payments/
    Permission: IsAuthenticated
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup that runs before each test."""
        self.url = reverse('payments:payment-list')
    
    def test_list_payments_unauthenticated(self, api_client):
        """
        Test listing payments without authentication.
        
        Expected behavior:
        - Returns 401 Unauthorized
        """
        # Act
        response = api_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_payments_authenticated(self, authenticated_client):
        """
        Test listing user's payments.
        
        Expected behavior:
        - Returns 200 OK
        - Only user's payments
        """
        from tests.factories import OrderFactory, PaymentFactory, UserFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        other_user = UserFactory()
        
        order1 = OrderFactory(user=user)
        order2 = OrderFactory(user=user)
        other_order = OrderFactory(user=other_user)
        
        payment1 = PaymentFactory(order=order1, status='SUCCEEDED')
        payment2 = PaymentFactory(order=order2, status='PENDING')
        PaymentFactory(order=other_order)  # Other user's payment
        
        # Act
        response = authenticated_client.get(self.url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.api
class TestPaymentDetail:
    """
    Test suite for Payment Detail endpoint.
    
    Endpoint: GET /api/payments/{id}/
    Permission: IsAuthenticated (own payments only)
    """
    
    def test_get_payment_detail(self, authenticated_client):
        """
        Test getting payment detail.
        
        Expected behavior:
        - Returns 200 OK
        - Payment details
        """
        from tests.factories import OrderFactory, PaymentFactory
        from apps.users.models import User
        
        # Arrange
        user = User.objects.first()
        order = OrderFactory(user=user)
        payment = PaymentFactory(order=order, status='SUCCEEDED', amount=Decimal('999.99'))
        
        url = reverse('payments:payment-detail', kwargs={'pk': payment.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(payment.id)
        assert response.data['status'] == 'SUCCEEDED'
        assert float(response.data['amount']) == 999.99
    
    def test_get_other_user_payment(self, authenticated_client):
        """
        Test accessing another user's payment.
        
        Expected behavior:
        - Returns 404 Not Found
        """
        from tests.factories import UserFactory, OrderFactory, PaymentFactory
        
        # Arrange
        other_user = UserFactory()
        other_order = OrderFactory(user=other_user)
        other_payment = PaymentFactory(order=other_order)
        
        url = reverse('payments:payment-detail', kwargs={'pk': other_payment.id})
        
        # Act
        response = authenticated_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND