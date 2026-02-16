"""
Django Admin Configuration for Payments App

Provides admin interface for managing payments.
Useful for payment tracking, debugging, and customer support.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin interface for Payment model.
    
    Features:
    - View all payments
    - Filter by status
    - Search by order, user, payment intent
    - Payment details display
    - Stripe integration info
    - No manual add/delete
    """
    
    list_display = [
        'payment_id',
        'order_link',
        'user_email',
        'amount_display',
        'status_badge',
        'payment_method_display',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'payment_method_type',
        'created_at',
        'paid_at',
    ]
    
    search_fields = [
        'stripe_payment_intent_id',
        'order__id',
        'order__user__email',
        'order__user__first_name',
        'order__user__last_name',
    ]
    
    readonly_fields = [
        'id',
        'order',
        'stripe_payment_intent_id',
        'stripe_client_secret',
        'amount',
        'currency',
        'status',
        'payment_method_type',
        'payment_method_last4',
        'failure_message',
        'metadata',
        'created_at',
        'updated_at',
        'paid_at',
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'id',
                'order',
                'status',
                'amount',
                'currency',
            )
        }),
        ('Stripe Information', {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_client_secret',
            )
        }),
        ('Payment Method', {
            'fields': (
                'payment_method_type',
                'payment_method_last4',
            )
        }),
        ('Additional Information', {
            'fields': (
                'failure_message',
                'metadata',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'paid_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def payment_id(self, obj):
        """Display short payment ID."""
        return format_html(
            '<code style="color: #0066cc;">{}</code>',
            str(obj.id)[:8]
        )

    def order_link(self, obj):
        """Display order with link."""
        return format_html(
            '<a href="/admin/orders/order/{}/change/">Order {}</a>',
            obj.order.id,
            str(obj.order.id)[:8]
        )

    def user_email(self, obj):
        """Display user email with link."""
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.order.user.id,
            obj.order.user.email
        )

    def amount_display(self, obj):
        """Display amount with currency."""
        return format_html(
            '<strong style="color: #28A745; font-size: 14px;">${}</strong>',
            obj.amount
        )

    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'PENDING': '#FFA500',
            'PROCESSING': '#0066CC',
            'SUCCEEDED': '#28A745',
            'FAILED': '#DC3545',
            'CANCELLED': '#6C757D',
            'REFUNDED': '#9966FF',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.status
        )

    def payment_method_display(self, obj):
        """Display payment method with icon safely."""
        if not obj.payment_method_type:
            # format_html uchun kamida bitta formatlash argumenti kerak
            return format_html('<span style="color: gray;">{}</span>', '-')
        
        icons = {
            'card': '💳',
            'bank': '🏦',
            'wallet': '👛',
        }
        icon = icons.get(obj.payment_method_type, '💰')
        last4 = obj.payment_method_last4 or ''
        
        if last4:
            return format_html('{} •••• {}', icon, last4)
        
        method_title = str(obj.payment_method_type).title()
        return format_html('{} {}', icon, method_title)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('order__user')
        return queryset
    
    def has_add_permission(self, request):
        """Disable manual payment creation in admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable payment deletion."""
        return False