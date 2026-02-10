from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.products.models import Category, Product
from decimal import Decimal
import random
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Seed database with demo data for development and testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete existing data before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of products to create (default: 50)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        flush = options['flush']
        count = options['count']
        
        if flush:
            self.stdout.write(self.style.WARNING('⚠️  Deleting existing data...'))
            Product.objects.all().delete()
            Category.objects.all().delete()
        
        self.stdout.write(self.style.HTTP_INFO('🌱 Seeding categories...'))
        categories = self._create_categories()
        
        self.stdout.write(self.style.HTTP_INFO(f'🌱 Seeding {count} products...'))
        products = self._create_products(categories, count)
        
        self._print_summary(categories, products)
        self.stdout.write(self.style.SUCCESS('✅ Done!'))

    def _create_categories(self):
        """Create category hierarchy."""
        tree = {
            'Electronics': ['Phones', 'Laptops', 'Accessories'],
            'Clothing': ['Men', 'Women', 'Kids'],
            'Home': ['Furniture', 'Decor', 'Kitchen'],
            'Books': ['Fiction', 'Tech', 'Business'],
        }
        
        categories = []
        for parent_name, children in tree.items():
            parent, _ = Category.objects.get_or_create(
                name=parent_name,
                defaults={
                    'description': f'{parent_name} category',
                    'is_active': True,
                }
            )
            categories.append(parent)
            
            for child_name in children:
                child, _ = Category.objects.get_or_create(
                    name=f'{parent_name} - {child_name}',
                    parent=parent,
                    defaults={
                        'description': f'{child_name} in {parent_name}',
                        'is_active': True,
                    }
                )
                categories.append(child)
        
        return categories

    def _create_products(self, categories, count):
        """Create products with realistic data."""
        adjectives = ['Premium', 'Pro', 'Ultra', 'Smart', 'Wireless', 'Portable']
        nouns = ['Device', 'Gadget', 'Tool', 'Kit', 'System', 'Solution']
        
        products = []
        for i in range(count):
            category = random.choice(categories)
            name = f'{random.choice(adjectives)} {random.choice(nouns)} {i+1}'
            
            # Stock distribution: 10% out, 20% low, 70% normal
            stock_random = random.random()
            if stock_random < 0.1:
                stock = 0
            elif stock_random < 0.3:
                stock = random.randint(1, 10)
            else:
                stock = random.randint(11, 100)
            
            price = Decimal(random.randint(10, 2000))
            
            # 30% discount
            has_discount = random.random() < 0.3
            discount_price = price * Decimal('0.8') if has_discount else None
            
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'price': price,
                    'discount_price': discount_price,
                    'stock': stock,
                    'sku': f'SKU-{random.randint(10000, 99999)}',
                    'is_active': True,
                    'is_featured': random.random() < 0.2,
                    'description': f'High-quality {name.lower()} for professionals',
                }
            )
            products.append((product, created))
        
        return products

    def _print_summary(self, categories, products):
        """Print seeding summary."""
        created_products = sum(1 for _, created in products if created)
        existing_products = len(products) - created_products
        
        # Stock stats
        all_products = Product.objects.all()
        out_stock = all_products.filter(stock=0).count()
        low_stock = all_products.filter(stock__range=(1, 10)).count()
        ok_stock = all_products.filter(stock__gt=10).count()
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.HTTP_INFO("📊 SEEDING SUMMARY"))
        self.stdout.write("="*50)
        self.stdout.write(f"Categories: {len(categories)}")
        self.stdout.write(f"Products: {len(products)} (new: {created_products}, existing: {existing_products})")
        self.stdout.write(f"\nStock distribution:")
        self.stdout.write(f"  🔴 Out of stock: {out_stock}")
        self.stdout.write(f"  🟠 Low stock (1-10): {low_stock}")
        self.stdout.write(f"  🟢 In stock (11+): {ok_stock}")
        self.stdout.write(f"\nFeatured: {all_products.filter(is_featured=True).count()}")
        self.stdout.write(f"With discount: {all_products.filter(discount_price__isnull=False).count()}")