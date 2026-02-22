"""
Email Service for Order Notifications

Handles sending order-related emails with HTML templates.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OrderEmailService:
    """
    Service for sending order-related emails.
    
    Features:
    - HTML email templates
    - Plain text fallback
    - Error handling
    - Logging
    """
    
    @staticmethod
    def send_order_confirmation(order) -> bool:
        """
        Send order confirmation email to customer.
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Email context
            context = {
                'order': order,
                'user': order.user,
                'items': order.items.all(),
                'total': order.total_amount,
                'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}" if hasattr(settings, 'FRONTEND_URL') else '#',
            }
            
            # Render HTML email
            html_content = render_to_string('emails/order_confirmation.html', context)
            
            # Plain text fallback
            text_content = f"""
Order Confirmation

Thank you for your order, {order.user.get_full_name() or order.user.email}!

Order ID: {order.id}
Order Date: {order.created_at.strftime('%B %d, %Y')}
Total: ${order.total_amount}

Items:
{chr(10).join([f"- {item.product_name} x{item.quantity}: ${item.subtotal}" for item in order.items.all()])}

Shipping Address:
{order.shipping_address}
{order.shipping_city}, {order.shipping_postal_code}
{order.shipping_country}

You can track your order status at any time.

Thank you for shopping with us!
            """
            
            # Create email
            subject = f'Order Confirmation - #{str(order.id)[:8]}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [order.user.email]
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Order confirmation email sent to {order.user.email} for order {order.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation email: {str(e)}")
            return False
    
    @staticmethod
    def send_order_shipped(order) -> bool:
        """
        Send order shipped notification to customer.
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            context = {
                'order': order,
                'user': order.user,
                'tracking_number': order.tracking_number,
                'tracking_url': f"https://track.example.com/{order.tracking_number}" if order.tracking_number else None,
                'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}" if hasattr(settings, 'FRONTEND_URL') else '#',
            }
            
            html_content = render_to_string('emails/order_shipped.html', context)
            
            text_content = f"""
Your Order Has Been Shipped!

Hello {order.user.get_full_name() or order.user.email},

Great news! Your order #{str(order.id)[:8]} has been shipped.

{f'Tracking Number: {order.tracking_number}' if order.tracking_number else ''}

Shipping Address:
{order.shipping_address}
{order.shipping_city}, {order.shipping_postal_code}
{order.shipping_country}

You can track your package and view order details at any time.

Thank you for shopping with us!
            """
            
            subject = f'Order Shipped - #{str(order.id)[:8]}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [order.user.email]
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Order shipped email sent to {order.user.email} for order {order.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order shipped email: {str(e)}")
            return False
    
    @staticmethod
    def send_order_delivered(order) -> bool:
        """
        Send order delivered notification to customer.
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            context = {
                'order': order,
                'user': order.user,
                'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}" if hasattr(settings, 'FRONTEND_URL') else '#',
                'review_url': f"{settings.FRONTEND_URL}/orders/{order.id}/review" if hasattr(settings, 'FRONTEND_URL') else '#',
            }
            
            html_content = render_to_string('emails/order_delivered.html', context)
            
            text_content = f"""
Your Order Has Been Delivered!

Hello {order.user.get_full_name() or order.user.email},

Your order #{str(order.id)[:8]} has been delivered successfully!

We hope you're happy with your purchase. If you have a moment, we'd love to hear your feedback.

Would you like to review your products?

Thank you for shopping with us!
            """
            
            subject = f'Order Delivered - #{str(order.id)[:8]}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [order.user.email]
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Order delivered email sent to {order.user.email} for order {order.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order delivered email: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_confirmation(payment) -> bool:
        """
        Send payment confirmation email to customer.
        
        Args:
            payment: Payment instance
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            order = payment.order
            
            context = {
                'payment': payment,
                'order': order,
                'user': order.user,
                'order_url': f"{settings.FRONTEND_URL}/orders/{order.id}" if hasattr(settings, 'FRONTEND_URL') else '#',
            }
            
            html_content = render_to_string('emails/payment_confirmation.html', context)
            
            text_content = f"""
Payment Confirmation

Hello {order.user.get_full_name() or order.user.email},

Your payment of ${payment.amount} has been successfully processed.

Order ID: {order.id}
Payment ID: {str(payment.id)[:8]}
Amount: ${payment.amount}
Payment Method: {payment.payment_method_type or 'Card'} ending in {payment.payment_method_last4 or '****'}

Your order is now being processed and will be shipped soon.

Thank you for your payment!
            """
            
            subject = f'Payment Confirmed - ${payment.amount}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [order.user.email]
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Payment confirmation email sent to {order.user.email} for payment {payment.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send payment confirmation email: {str(e)}")
            return False