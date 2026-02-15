"""
Django Admin Configuration for Orders App
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    
    fields = [
        'product',
        'product_name',
        'product_sku',
        'quantity',
        'price',
        'subtotal_display',
    ]
    
    readonly_fields = [
        'product',
        'product_name',
        'product_sku',
        'price',
        'subtotal_display',
    ]
    
    def subtotal_display(self, obj):
        """Display subtotal with currency."""
        if obj.id:
            return format_html('<strong>${}</strong>', obj.subtotal)
        return "-"
    
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'user_email',
        'status_badge',
        'total_items_display',
        'total_amount_display',
        'shipping_city',
        'created_at',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'tracking_number',
        'id',
    ]
    
    readonly_fields = [
        'id',
        'user',
        'created_at',
        'updated_at',
        'total_amount_display',
        'total_items_display',
    ]
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'id',
                'user',
                'status',
                'total_items_display',
                'total_amount_display',
            )
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_address',
                'shipping_city',
                'shipping_postal_code',
                'shipping_country',
            )
        }),
        ('Additional Information', {
            'fields': (
                'tracking_number',
                'notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    actions = [
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled',
    ]
    
    def order_number(self, obj):
        return format_html(
            '<code style="color: #0066cc;">{}</code>',
            str(obj.id)[:8]
        )
    
    order_number.short_description = 'Order #'
    order_number.admin_order_field = 'id'
    
    def user_email(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.email
        )
    
    user_email.short_description = 'Customer'
    user_email.admin_order_field = 'user__email'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'PROCESSING': '#0066CC',
            'SHIPPED': '#9966FF',
            'DELIVERED': '#28A745',
            'CANCELLED': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.status
        )
    
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def total_items_display(self, obj):
        count = obj.total_items
        if count == 0:
            return mark_safe('<span style="color: gray;">0 items</span>')
        elif count == 1:
            return '1 item'
        else:
            return format_html('<strong>{} items</strong>', count)
    
    total_items_display.short_description = 'Items'
    
    def total_amount_display(self, obj):
        amount = obj.total_amount
        if amount == 0:
            return mark_safe('<span style="color: gray;">$0.00</span>')
        else:
            return format_html(
                '<strong style="color: #28A745; font-size: 14px;">${}</strong>',
                amount
            )
    
    total_amount_display.short_description = 'Total'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        queryset = queryset.prefetch_related('items__product')
        return queryset
    
    # Bulk Actions
    def mark_as_processing(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='PROCESSING')
        self.message_user(request, f'{updated} order(s) marked as PROCESSING.')
    mark_as_processing.short_description = 'Mark as PROCESSING'
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(status='PROCESSING').update(status='SHIPPED')
        self.message_user(request, f'{updated} order(s) marked as SHIPPED.')
    mark_as_shipped.short_description = 'Mark as SHIPPED'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='SHIPPED').update(status='DELIVERED')
        self.message_user(request, f'{updated} order(s) marked as DELIVERED.')
    mark_as_delivered.short_description = 'Mark as DELIVERED'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.exclude(status__in=['SHIPPED', 'DELIVERED']).update(status='CANCELLED')
        self.message_user(request, f'{updated} order(s) marked as CANCELLED.')
    mark_as_cancelled.short_description = 'Mark as CANCELLED'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id_short',
        'order_link',
        'product_name',
        'product_sku',
        'quantity',
        'price',
        'subtotal_display',
        'created_at',
    ]
    
    list_filter = ['created_at']
    search_fields = ['order__id', 'product_name', 'product_sku']
    
    readonly_fields = [
        'id', 'order', 'product', 'product_name', 'product_sku',
        'price', 'quantity', 'subtotal_display', 'created_at', 'updated_at',
    ]
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def order_link(self, obj):
        return format_html(
            '<a href="/admin/orders/order/{}/change/">Order {}</a>',
            obj.order.id,
            str(obj.order.id)[:8]
        )
    order_link.short_description = 'Order'
    
    def subtotal_display(self, obj):
        return format_html('<strong>${}</strong>', obj.subtotal)
    subtotal_display.short_description = 'Subtotal'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False