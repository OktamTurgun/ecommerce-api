"""
Order Models

Order management system for e-commerce.
Handles order creation, status tracking, and order items.
"""
import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class Order(models.Model):
    """
    Order model.
    
    Represents a customer order with status tracking.
    
    Features:
    - User reference
    - Order status workflow
    - Shipping information
    - Total amount calculation
    - Order items
    - Timestamps
    
    Examples:
        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address='123 Main St',
            shipping_city='New York',
            shipping_postal_code='10001',
            shipping_country='USA'
        )
    """
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text='Customer who placed the order'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Current order status'
    )
    
    # Shipping Information
    shipping_address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Shipping street address'
    )
    
    shipping_city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Shipping city'
    )
    
    shipping_postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Shipping postal/ZIP code'
    )
    
    shipping_country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Shipping country'
    )
    
    # Additional Information
    notes = models.TextField(
        blank=True,
        help_text='Order notes or special instructions'
    )
    
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Shipping tracking number'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def __str__(self):
        """String representation."""
        return f'Order {str(self.id)[:8]} - {self.status}'
    
    @property
    def total_amount(self):
        """
        Calculate total order amount.
        
        Returns:
            Decimal: Sum of all order item subtotals
        """
        return sum(item.subtotal for item in self.items.all()) or Decimal('0.00')
    
    @property
    def total_items(self):
        """
        Calculate total number of items.
        
        Returns:
            int: Sum of all item quantities
        """
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Order item model.
    
    Represents a product in an order with snapshot data.
    
    Features:
    - Order reference
    - Product reference (can be null if product deleted)
    - Product snapshot (name, SKU, price at order time)
    - Quantity
    - Subtotal calculation
    - Timestamps
    
    Examples:
        # Add item to order
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            price=product.get_price(),
            quantity=2
        )
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Order this item belongs to'
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Product reference (can be null if product deleted)'
    )
    
    # Product Snapshot (saved at order time)
    product_name = models.CharField(
        max_length=200,
        help_text='Product name at order time'
    )
    
    product_sku = models.CharField(
        max_length=100,
        blank=True,
        null=True, # Bazada NULL bo'lishiga ruxsat beramiz
        help_text='Product SKU at order time'
    )
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Price at order time'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        help_text='Quantity ordered'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        """String representation."""
        return f'{self.quantity}x {self.product_name}'
    
    def save(self, *args, **kwargs):
        if self.product and not self.product_name:
            self.product_name = self.product.name
        if self.product and not self.product_sku:
            self.product_sku = getattr(self.product, 'sku', None)
        if self.product and (self.price == Decimal('0.00') or self.price is None):
            # Mahsulotning joriy narxini snapshot sifatida olamiz
            self.price = getattr(self.product, 'price', Decimal('0.00'))
        
        super().save(*args, **kwargs)
    
    
    @property
    def subtotal(self):
        # Endi bu yerda price har doim kamida 0.00 bo'lishi kafolatlanadi
        return (self.quantity or 0) * self.price