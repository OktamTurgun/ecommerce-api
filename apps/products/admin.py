"""
Django Admin Configuration for Products App

Customizes the admin interface for Category and Product models.
Provides user-friendly management interface with search, filters, and bulk actions.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count
from apps.products.models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    """
    Inline admin for ProductImage.
    
    Allows managing product images directly from Product admin page.
    Features:
    - Image preview
    - Primary image selection
    - Order management
    - Alt text editing
    """
    
    model = ProductImage
    extra = 1  # Show 1 empty form by default
    fields = ['image_preview', 'image', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """
        Display thumbnail preview of image.
        
        Shows 100x100 preview if image exists.
        """
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    
    image_preview.short_description = 'Preview'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    
    Features:
    - List display with product count
    - Hierarchical parent-child display
    - Search by name and description
    - Filter by active status and parent
    - Auto-generate slug from name
    - Inline subcategories view
    """
    
    list_display = [
        'name',
        'slug',
        'parent',
        'product_count',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'is_active',
        'parent',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
        'slug',
    ]
    
    prepopulated_fields = {
        'slug': ('name',)  # Auto-generate slug from name
    }
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'product_count',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent',),
            'description': 'Set parent category to create subcategory'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'product_count'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
    
    ordering = ['name']
    
    def product_count(self, obj):
        """
        Display count of active products in category.
        
        Uses annotated queryset for efficiency.
        """
        return obj.products.filter(is_active=True).count()
    
    product_count.short_description = 'Products'
    product_count.admin_order_field = 'products__count'
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related and prefetch_related.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('parent')
        queryset = queryset.prefetch_related('products')
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model.
    
    Features:
    - List display with pricing and stock info
    - Color-coded stock status
    - Search by name, description, SKU
    - Filter by category, status, featured
    - Bulk actions (activate/deactivate)
    - Inline editing for stock and status
    - Auto-generate slug from name
    """
    inlines = [ProductImageInline]
    
    list_display = [
        'name',
        'category',
        'price_display',
        'discount_display',
        'stock',
        'stock_status',
        'is_featured',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'category',
        'is_active',
        'is_featured',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
        'sku',
        'slug',
    ]
    
    prepopulated_fields = {
        'slug': ('name',)
    }
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'has_discount',
        'savings_display',
        'discount_percentage_display',
    ]
    
    list_editable = [
        'stock',
        'is_active',
        'is_featured',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'has_discount', 'savings_display', 'discount_percentage_display'),
            'description': 'Set regular price and optional discount price'
        }),
        ('Inventory', {
            'fields': ('stock', 'sku'),
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured'),
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'activate_products',
        'deactivate_products',
        'mark_as_featured',
        'unmark_as_featured',
    ]
    
    ordering = ['-created_at']
    
    # Custom display methods
    
    def price_display(self, obj):
        """Display price with currency symbol."""
        return f"${obj.price}"
    
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def discount_display(self, obj):
        """Display discount with badge style."""
        if obj.has_discount and obj.discount_price:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; '
                'border-radius: 10px; font-size: 11px; font-weight: bold;">'
                '-{}% ${}</span>',
                obj.discount_percentage,
                obj.discount_price
            )
        return mark_safe('<span style="color: #6c757d;">—</span>')

    discount_display.short_description = 'Discount'
    
    def stock_status(self, obj):
        """
        Display stock with color coding.
        
        Red: Out of stock (0)
        Orange: Low stock (1-10)
        Green: In stock (11+)
        """
        if obj.stock == 0:
            color = 'red'
            status = 'Out of Stock'
        elif obj.stock <= 10:
            color = 'orange'
            status = f'{obj.stock} (Low)'
        else:
            color = 'green'
            status = f'{obj.stock}'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    
    stock_status.short_description = 'Stock'
    stock_status.admin_order_field = 'stock'
    
    def savings_display(self, obj):
        """Display savings amount."""
        if obj.has_discount:
            return f"${obj.savings}"
        return "N/A"
    
    savings_display.short_description = 'Savings'
    
    def discount_percentage_display(self, obj):
        """Display discount percentage."""
        if obj.has_discount:
            return f"{obj.discount_percentage}%"
        return "N/A"
    
    discount_percentage_display.short_description = 'Discount %'
    
    # Custom actions
    
    @admin.action(description='Activate selected products')
    def activate_products(self, request, queryset):
        """Bulk activate products."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} product(s) successfully activated.'
        )
    
    @admin.action(description='Deactivate selected products')
    def deactivate_products(self, request, queryset):
        """Bulk deactivate products."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} product(s) successfully deactivated.'
        )
    
    @admin.action(description='Mark as featured')
    def mark_as_featured(self, request, queryset):
        """Bulk mark products as featured."""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            f'{updated} product(s) marked as featured.'
        )
    
    @admin.action(description='Remove from featured')
    def unmark_as_featured(self, request, queryset):
        """Bulk remove products from featured."""
        updated = queryset.update(is_featured=False)
        self.message_user(
            request,
            f'{updated} product(s) removed from featured.'
        )
    
    def get_queryset(self, request):
        """
        Optimize queryset with select_related.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('category')
        return queryset


# Optional: Customize admin site header and title
admin.site.site_header = 'E-commerce Admin Panel'
admin.site.site_title = 'E-commerce Admin'
admin.site.index_title = 'Welcome to E-commerce Admin Panel'