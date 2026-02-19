"""
Django Admin Configuration for Reviews App

Provides admin interface for managing product reviews.
Useful for moderation, quality control, and customer support.
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for Review model.
    
    Features:
    - View all reviews with star ratings
    - Filter by rating, product, and timestamps
    - Search by user, product, and comment content
    - Review moderation (delete allowed, add disabled)
    """
    
    list_display = [
        'id_short',
        'product_link',
        'user_email',
        'rating_stars',
        'comment_preview',
        'created_at',
    ]
    
    list_filter = [
        'rating',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'product__name',
        'comment',
    ]
    
    readonly_fields = [
        'id',
        'user',
        'product',
        'rating',
        'comment',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Review Information', {
            'fields': (
                'id',
                'user',
                'product',
                'rating',
            )
        }),
        ('Review Content', {
            'fields': (
                'comment',
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
    
    # --- Custom Display Methods ---

    def id_short(self, obj):
        """Display short ID with styling."""
        return format_html(
            '<code style="color: #0066cc;">{}</code>',
            str(obj.id)[:8]
        )
    id_short.short_description = 'ID'
    id_short.admin_order_field = 'id'
    
    def product_link(self, obj):
        """Display product with link to its admin page."""
        return format_html(
            '<a href="/admin/products/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def user_email(self, obj):
        """Display user email with link to its admin page."""
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.email
        )
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def rating_stars(self, obj):
        """Display rating as visual stars with color coding."""
        stars = '⭐' * obj.rating
        empty = '☆' * (5 - obj.rating)
        
        colors = {
            5: '#28A745',  # Green
            4: '#17A2B8',  # Cyan
            3: '#FFC107',  # Yellow
            2: '#FD7E14',  # Orange
            1: '#DC3545',  # Red
        }
        color = colors.get(obj.rating, '#6C757D')
        
        return format_html(
            '<span style="color: {}; font-size: 14px;">{}{}</span> '
            '<span style="color: #6C757D; font-size: 11px;">({}/5)</span>',
            color,
            stars,
            empty,
            obj.rating
        )
    rating_stars.short_description = 'Rating'
    rating_stars.admin_order_field = 'rating'
    
    def comment_preview(self, obj):
        """Display truncated comment with a tooltip."""
        if not obj.comment:
            return format_html('<span style="color: gray; font-style: italic;">{}</span>', 'No comment')
        
        preview = (obj.comment[:50] + '...') if len(obj.comment) > 50 else obj.comment
        return format_html('<span title="{}">{}</span>', obj.comment, preview)
    comment_preview.short_description = 'Comment'
    
    # --- Logic & Permissions ---

    def get_queryset(self, request):
        """Optimization: use select_related to reduce SQL queries."""
        return super().get_queryset(request).select_related('user', 'product')
    
    def has_add_permission(self, request):
        """Reviews should be created via API/Storefront, not manually in Admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for moderation purposes."""
        return True