"""
Test Data Factories using Factory Boy.

Factories help create test data quickly and consistently.
Instead of manually creating objects, we use factories.

Example:
    # Old way (tedious):
    user = User.objects.create(
        email='test@example.com',
        first_name='John',
        last_name='Doe',
        ...
    )
    
    # New way (simple):
    user = UserFactory()
"""
from decimal import Decimal
import factory
from factory.django import DjangoModelFactory
from faker import Faker

fake = Faker()


class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances for testing.
    
    Usage:
        # Create a user with default values
        user = UserFactory()
        
        # Create a user with custom email
        user = UserFactory(email='custom@example.com')
        
        # Create multiple users
        users = UserFactory.create_batch(5)
        
        # Create user without saving to DB (for unit tests)
        user = UserFactory.build()
    """
    class Meta:
        model = 'users.User'
        django_get_or_create = ('email',)
    
    # Basic fields
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    
    # Phone number
    phone_number = factory.Faker('phone_number')
    
    # Address fields
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    country = 'Uzbekistan'
    postal_code = factory.Faker('postcode')
    
    # Status fields
    is_active = True
    is_staff = False
    is_superuser = False
    
    # Password
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """
        Set password after user is generated.
        Default password: TestPass123!
        
        Usage:
            user = UserFactory(password='custom_password')
        """
        password = extracted if extracted else 'TestPass123!'
        obj.set_password(password)
        if create:
            obj.save()


class AdminUserFactory(UserFactory):
    """
    Factory for creating admin users.
    
    Usage:
        admin = AdminUserFactory()
    """
    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f'admin{n}@example.com')


class UserConfirmationFactory(DjangoModelFactory):
    """
    Factory for creating UserConfirmation instances.
    
    Usage:
        # Email verification code
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='email_verification'
        )
        
        # Password reset code
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='password_reset'
        )
    """
    class Meta:
        model = 'users.UserConfirmation'
    
    user = factory.SubFactory(UserFactory)
    confirmation_type = 'email_verification'
    code = factory.Sequence(lambda n: f'{100000 + n}')  # 6-digit code
    is_used = False
    
    # Expiry: 15 minutes from now
    @factory.lazy_attribute
    def expires_at(self):
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() + timedelta(minutes=15)


# Additional factories for future use
# These are commented out until Products app is implemented

# class ProductFactory(DjangoModelFactory):
#     """
#     Factory for Product model (to be implemented).
#     
#     This is a placeholder for when we implement Products app.
#     """
#     class Meta:
#         model = 'products.Product'
#     
#     name = factory.Faker('word')
#     description = factory.Faker('text')
#     price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
#     stock = factory.Faker('random_int', min=0, max=1000)


# class CategoryFactory(DjangoModelFactory):
#     """
#     Factory for Category model (to be implemented).
#     """
#     class Meta:
#         model = 'products.Category'
#     
#     name = factory.Faker('word')
#     description = factory.Faker('sentence')


# Helper functions for common test scenarios

def create_user_with_verification(email=None, verified=False):
    """
    Helper function to create a user with verification code.
    
    Args:
        email: Custom email (optional)
        verified: Whether user is verified (default: False)
    
    Returns:
        tuple: (user, confirmation_code)
    
    Usage:
        user, code = create_user_with_verification()
        user, code = create_user_with_verification(verified=True)
    """
    user = UserFactory(email=email) if email else UserFactory()
    
    if verified:
        user.is_active = True
        user.save()
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='email_verification',
            is_used=True
        )
    else:
        confirmation = UserConfirmationFactory(
            user=user,
            confirmation_type='email_verification'
        )
    
    return user, confirmation.code


def create_authenticated_client(user=None):
    """
    Helper function to create an authenticated API client.
    
    Args:
        user: Custom user (optional, creates new user if not provided)
    
    Returns:
        tuple: (api_client, user)
    
    Usage:
        client, user = create_authenticated_client()
    """
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    if user is None:
        user = UserFactory()
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client, user


# ==================== CATEGORY FACTORY ====================
class CategoryFactory(DjangoModelFactory):
    """
    Factory for creating test Category instances.
    
    Usage:
        category = CategoryFactory()
        category = CategoryFactory(name='Electronics')
        root = CategoryFactory(parent=None)
        child = CategoryFactory(parent=root)
    """
    
    class Meta:
        model = 'products.Category'
    
    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.LazyAttribute(lambda obj: factory.Faker('slug').evaluate(None, None, {'locale': None}))
    description = factory.Faker('text', max_nb_chars=200)
    parent = None
    is_active = True


# ==================== PRODUCT FACTORY ====================
class ProductFactory(DjangoModelFactory):
    """
    Factory for creating test Product instances.
    
    Usage:
        product = ProductFactory()
        product = ProductFactory(name='iPhone 15', price=Decimal('999.99'))
        product = ProductFactory(category=my_category, stock=100)
    """
    
    class Meta:
        model = 'products.Product'
    
    name = factory.Sequence(lambda n: f'Product {n}')
    slug = factory.LazyAttribute(lambda obj: factory.Faker('slug').evaluate(None, None, {'locale': None}))
    description = factory.Faker('text', max_nb_chars=500)
    category = factory.SubFactory(CategoryFactory)
    price = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True, min_value=1)
    discount_price = None
    stock = factory.Faker('random_int', min=0, max=100)
    sku = factory.Sequence(lambda n: f'SKU-{n:05d}')
    is_active = True
    is_featured = False


# ==================== PRODUCT IMAGE FACTORY ====================
class ProductImageFactory(DjangoModelFactory):
    """
    Factory for creating test ProductImage instances.
    
    Usage:
        image = ProductImageFactory()
        image = ProductImageFactory(product=my_product, is_primary=True)
        image = ProductImageFactory(order=1)
    """
    
    class Meta:
        model = 'products.ProductImage'
    
    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(
        filename='product_image.jpg',
        width=800,
        height=600,
        color='blue'
    )
    alt_text = factory.LazyAttribute(
        lambda obj: f'{obj.product.name} image'
    )
    is_primary = False
    order = factory.Sequence(lambda n: n)

# ==================== CART FACTORIES ====================
class CartFactory(DjangoModelFactory):
    """
    Factory for creating test Cart instances.
    
    Usage:
        cart = CartFactory()  # Anonymous cart
        cart = CartFactory(user=my_user)  # User cart
        cart = CartFactory(session_key='abc123')  # Session cart
    """
    
    class Meta:
        model = 'cart.Cart'
    
    user = None
    session_key = factory.Sequence(lambda n: f'session_{n}')


class CartItemFactory(DjangoModelFactory):
    """
    Factory for creating test CartItem instances.
    
    Usage:
        item = CartItemFactory()
        item = CartItemFactory(cart=my_cart, product=my_product)
        item = CartItemFactory(quantity=5, price_at_add=Decimal('99.99'))
    """
    
    class Meta:
        model = 'cart.CartItem'
    
    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    price_at_add = factory.LazyAttribute(
        lambda obj: obj.product.price
    )

class OrderFactory(DjangoModelFactory):
    """
    Factory for creating test Order instances.
    
    Usage:
        order = OrderFactory()
        order = OrderFactory(user=my_user)
        order = OrderFactory(status='PROCESSING')
    """
    
    class Meta:
        model = 'orders.Order'
    
    user = factory.SubFactory(UserFactory)
    status = 'PENDING'
    shipping_address = factory.Faker('street_address')
    shipping_city = factory.Faker('city')
    shipping_postal_code = factory.Faker('postcode')
    shipping_country = 'USA'
    notes = ''
    tracking_number = ''


class OrderItemFactory(DjangoModelFactory):
    """
    Factory for creating test OrderItem instances.
    
    Usage:
        item = OrderItemFactory()
        item = OrderItemFactory(order=my_order, product=my_product)
        item = OrderItemFactory(quantity=5, price=Decimal('99.99'))
    """
    
    class Meta:
        model = 'orders.OrderItem'
    
    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    product_name = factory.LazyAttribute(lambda obj: obj.product.name)
    product_sku = factory.LazyAttribute(lambda obj: obj.product.sku)
    price = factory.LazyAttribute(lambda obj: obj.product.price)
    quantity = 1

class PaymentFactory(DjangoModelFactory):
    """
    Factory for creating test Payment instances.
    
    Usage:
        payment = PaymentFactory()
        payment = PaymentFactory(order=my_order)
        payment = PaymentFactory(status='SUCCEEDED', amount=Decimal('999.99'))
    """
    
    class Meta:
        model = 'payments.Payment'
    
    order = factory.SubFactory(OrderFactory)
    stripe_payment_intent_id = factory.Sequence(lambda n: f'pi_test_{n}')
    stripe_client_secret = factory.Sequence(lambda n: f'pi_test_{n}_secret')
    amount = factory.LazyAttribute(lambda obj: obj.order.total_amount if hasattr(obj, 'order') else Decimal('100.00'))
    currency = 'usd'
    status = 'PENDING'
    payment_method_type = ''
    payment_method_last4 = ''
    failure_message = ''