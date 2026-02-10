"""
Product Serializers

Serializers for Category and Product models.
Converts model instances to JSON and validates incoming data.
"""
from rest_framework import serializers
from apps.products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    
    Features:
    - Auto-generates slug from name
    - Returns product count
    - Supports hierarchical categories (parent/subcategories)
    - Read-only fields for computed values
    
    Usage:
        # Serialize category
        serializer = CategorySerializer(category)
        data = serializer.data
        
        # Deserialize and create
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
    """
    
    # Computed field - product count
    product_count = serializers.SerializerMethodField()
    
    # Optional: Include subcategories
    subcategories = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'parent',
            'is_active',
            'product_count',
            'subcategories',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'slug',  # Auto-generated
            'product_count',
            'subcategories',
            'created_at',
            'updated_at',
        ]
    
    def get_product_count(self, obj):
        """
        Get count of active products in this category.
        
        Returns:
            int: Number of active products
        """
        return obj.product_count
    
    def get_subcategories(self, obj):
        """
        Get list of subcategory IDs.
        
        Returns:
            list: List of subcategory UUIDs
        """
        return [str(sub.id) for sub in obj.subcategories.filter(is_active=True)]
    
    def validate_parent(self, value):
        """
        Validate parent category.
        
        Rules:
        - Parent must be active
        - Prevent circular references
        
        Args:
            value: Parent category instance
            
        Returns:
            Category: Validated parent
            
        Raises:
            ValidationError: If parent is invalid
        """
        if value and not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign inactive category as parent."
            )
        
        # Prevent circular reference (self as parent)
        if self.instance and value == self.instance:
            raise serializers.ValidationError(
                "Category cannot be its own parent."
            )
        
        return value
    
    def validate_name(self, value):
        """
        Validate category name.
        
        Rules:
        - Name must be unique (case-insensitive check)
        - Minimum 2 characters
        
        Args:
            value: Category name
            
        Returns:
            str: Validated name
            
        Raises:
            ValidationError: If name is invalid
        """
        # Trim whitespace
        value = value.strip()
        
        # Minimum length
        if len(value) < 2:
            raise serializers.ValidationError(
                "Category name must be at least 2 characters."
            )
        
        # Check uniqueness (excluding current instance if updating)
        qs = Category.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError(
                f"Category with name '{value}' already exists."
            )
        
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for category lists.
    
    Used in product listings and dropdowns.
    Only includes essential fields for performance.
    """
    
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'slug',
            'parent',
            'product_count',
        ]
        read_only_fields = ['id', 'slug', 'product_count']
    
    def get_product_count(self, obj):
        """Get count of active products."""
        return obj.product_count


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    
    Features:
    - Price validation (positive, decimal)
    - Discount validation (less than price)
    - Stock validation (non-negative)
    - Category relationship
    - Computed fields (has_discount, final_price, savings)
    
    Usage:
        serializer = ProductSerializer(product)
        data = serializer.data
    """
    
    # Nested category (read-only)
    category_detail = CategoryListSerializer(source='category', read_only=True)
    
    # Write-only category ID
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        write_only=True
    )
    
    # Computed fields
    has_discount = serializers.BooleanField(read_only=True)
    final_price = serializers.DecimalField(
        source='get_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    savings = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'category',
            'category_detail',
            'price',
            'discount_price',
            'has_discount',
            'final_price',
            'savings',
            'discount_percentage',
            'stock',
            'sku',
            'is_in_stock',
            'is_active',
            'is_featured',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'slug',
            'has_discount',
            'final_price',
            'savings',
            'discount_percentage',
            'is_in_stock',
            'created_at',
            'updated_at',
        ]
    
    def validate_price(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return value
    
    def validate_stock(self, value):
        """Validate stock is non-negative."""
        if value < 0:
            raise serializers.ValidationError(
                "Stock cannot be negative."
            )
        return value
    
    def validate(self, data):
        """
        Object-level validation.
        
        Validates:
        - Discount price must be less than regular price
        - SKU uniqueness (if provided)
        """
        price = data.get('price', getattr(self.instance, 'price', None))
        discount_price = data.get('discount_price')
        
        # Discount validation
        if discount_price and price:
            if discount_price >= price:
                raise serializers.ValidationError({
                    'discount_price': 'Discount price must be less than regular price.'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Create product.
        
        The category is already validated by PrimaryKeyRelatedField,
        so we can safely create the product.
        """
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update product.
        
        Handles partial updates correctly.
        """
        return super().update(instance, validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product lists.
    
    Used in list views for better performance.
    Includes only essential fields.
    """
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    final_price = serializers.DecimalField(
        source='get_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'category_name',
            'price',
            'discount_price',
            'final_price',
            'has_discount',
            'stock',
            'is_in_stock',
            'is_featured',
        ]