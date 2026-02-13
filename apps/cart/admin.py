"""
Django Admin Configuration for Cart App
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    can_delete = True
    
    fields = [
        'product',
        'quantity',
        'price_at_add',
        'subtotal_display',
        'created_at',
    ]
    
    readonly_fields = [
        'subtotal_display',
        'created_at',
    ]
    
    def subtotal_display(self, obj):
        """Display subtotal with currency."""
        if obj.id and obj.price_at_add: # Narx borligini tekshiramiz
            return f"${obj.subtotal}"
        return "$0.00"
    
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_display',
        'total_items_display',
        'total_price_display',
        'cart_type',
        'created_at',
        'updated_at',
    ]
    
    list_filter = [
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'user__email',
        'session_key',
        'id',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'total_items_display',
        'total_price_display',
    ]
    
    inlines = [CartItemInline]
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('id', 'user', 'session_key')
        }),
        ('Totals', {
            'fields': ('total_items_display', 'total_price_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-updated_at']
    
    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="/admin/users/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.email
            )
        
        session_display = obj.session_key[:8] if obj.session_key else 'N/A'
        return format_html(
            '<span style="color: gray;">Anonymous ({})</span>',
            session_display
        )
    
    user_display.short_description = 'User'
    user_display.admin_order_field = 'user'
    
    def total_items_display(self, obj):
        count = obj.total_items
        if count == 0:
            return mark_safe('<span style="color: gray;">Empty</span>')
        elif count == 1:
            return mark_safe('<span style="color: green;">1 item</span>')
        else:
            return format_html(
                '<span style="color: green;">{} items</span>',
                count
            )
    
    total_items_display.short_description = 'Total Items'
    
    def total_price_display(self, obj):
        total = obj.total_price
        if total == 0:
            return mark_safe('<span style="color: gray;">$0.00</span>')
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">${}</span>',
                total
            )
    
    total_price_display.short_description = 'Total Price'
    
    def cart_type(self, obj):
        if obj.user:
            return mark_safe('<span style="color: blue;">User</span>')
        else:
            return mark_safe('<span style="color: orange;">Anonymous</span>')
    
    cart_type.short_description = 'Type'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user')
        queryset = queryset.prefetch_related('items__product')
        return queryset
    
    def has_add_permission(self, request):
        return False


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'cart_display',
        'product',
        'quantity',
        'price_at_add',
        'subtotal_display',
        'created_at',
    ]
    
    list_filter = ['created_at']
    
    search_fields = [
        'cart__user__email',
        'product__name',
        'product__sku',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'subtotal_display',
    ]
    
    fieldsets = (
        ('Cart Item Information', {
            'fields': ('cart', 'product', 'quantity', 'price_at_add')
        }),
        ('Calculated', {
            'fields': ('subtotal_display',)
        }),
        ('Timestamps', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cart_display(self, obj):
        if obj.cart.user:
            return format_html(
                '<a href="/admin/cart/cart/{}/change/">Cart: {}</a>',
                obj.cart.id,
                obj.cart.user.email
            )
        else:
            return format_html(
                '<a href="/admin/cart/cart/{}/change/">Anonymous Cart</a>',
                obj.cart.id
            )
    
    cart_display.short_description = 'Cart'
    
    def subtotal_display(self, obj):
        return f"${obj.subtotal}"
    
    subtotal_display.short_description = 'Subtotal'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('cart__user', 'product')
        return queryset
    
    def has_add_permission(self, request):
        return False


# Admin sozlamalari
admin.site.site_header = 'E-commerce Admin Panel'
admin.site.site_title = 'E-commerce Admin'
admin.site.index_title = 'Welcome to E-commerce Admin'