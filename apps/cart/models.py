"""
Cart Models

Shopping cart for authenticated and anonymous users.
Supports session-based carts for anonymous users and user-based carts for authenticated users.
"""
import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


class Cart(models.Model):
    """
    Shopping cart model.
    
    Supports both authenticated users and anonymous users (session-based).
    
    Features:
    - User-based cart (for authenticated users)
    - Session-based cart (for anonymous users)
    - Total items count
    - Total price calculation
    - Auto timestamps
    
    Examples:
        # Authenticated user cart
        cart = Cart.objects.create(user=request.user)
        
        # Anonymous user cart
        cart = Cart.objects.create(session_key=request.session.session_key)
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
        help_text='Cart owner (null for anonymous users)'
    )
    
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text='Session key for anonymous users'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
    
    def __str__(self):
        """String representation."""
        if self.user:
            return f'Cart for {self.user.email}'
        return f'Anonymous Cart ({self.session_key[:8]}...)'
    
    @property
    def total_items(self):
        """
        Calculate total number of items in cart.
        
        Returns:
            int: Sum of all item quantities
        """
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """
        Calculate total price of all items in cart.
        
        Returns:
            Decimal: Sum of all item subtotals
        """
        return sum(item.subtotal for item in self.items.all()) or Decimal('0.00')
    
    @classmethod
    def get_or_create_for_request(cls, request):
        """
        Get or create cart for current request.
        
        Works for both authenticated and anonymous users.
        
        Args:
            request: Django request object
            
        Returns:
            Cart: Cart instance
        """
        if request.user.is_authenticated:
            # Get or create user cart
            cart, created = cls.objects.get_or_create(user=request.user)
        else:
            # Get or create session cart
            if not request.session.session_key:
                request.session.create()
            
            cart, created = cls.objects.get_or_create(
                session_key=request.session.session_key
            )
        
        return cart
    
    def merge_with(self, other_cart):
        """
        Merge another cart into this cart.
        
        Used when anonymous user logs in - merge session cart into user cart.
        
        Args:
            other_cart: Cart to merge from
        """
        for item in other_cart.items.all():
            # Check if product already in this cart
            existing_item = self.items.filter(product=item.product).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                # Move item to this cart
                item.cart = self
                item.save()
        
        # Delete the other cart
        other_cart.delete()


class CartItem(models.Model):
    """
    Cart item model.
    
    Represents a product in the shopping cart with quantity and price snapshot.
    
    Features:
    - Product reference
    - Quantity
    - Price snapshot (price at time of adding)
    - Subtotal calculation
    - Auto timestamps
    
    Examples:
        # Add item to cart
        item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2,
            price_at_add=product.get_price()
        )
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Cart this item belongs to'
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        help_text='Product in cart'
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        help_text='Quantity of this product'
    )
    
    price_at_add = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price when added to cart (snapshot)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        unique_together = ['cart', 'product']  # One product per cart
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
    
    def __str__(self):
        """String representation."""
        return f'{self.quantity}x {self.product.name}'
    
    @property
    def subtotal(self):
        """
        Calculate subtotal for this item.
        
        Returns:
            Decimal: quantity × price_at_add
        """
        return self.quantity * self.price_at_add
    
    def clean(self):
        """
        Validate cart item before saving.
        
        Checks:
        - Quantity is positive (>= 1)
        - Product has enough stock
        """
        from django.core.exceptions import ValidationError
        
        # Validate quantity
        if self.quantity < 1:
            raise ValidationError({
                'quantity': 'Quantity must be at least 1'
            })
        
        # Validate stock availability
        if self.product.stock < self.quantity:
            raise ValidationError({
                'quantity': f'Only {self.product.stock} items in stock'
            })
    
    def save(self, *args, **kwargs):
        """
        Override save to set price_at_add if not provided.
        """
        if not self.price_at_add:
            self.price_at_add = self.product.get_price()
        
        super().save(*args, **kwargs)