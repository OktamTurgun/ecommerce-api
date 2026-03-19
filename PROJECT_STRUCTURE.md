# Project Structure (E-commerce API)

This document summarizes the key folders and files in the **ecommerce-api** repository and provides a concise directory tree view.

---

## ✅ High-level Architecture

- `manage.py` – Django management entry point used for local development, running migrations, tests, etc.
- `config/` – Django project configuration (settings, URLs, ASGI/WGI entry points).
- `apps/` – Core Django apps (cart, orders, payments, products, reviews, users) that implement the API functionality.
- `core/` – Shared utilities, helpers, common services, permissions and email helpers used by multiple apps.
- `templates/` – HTML templates used for email notifications.
- `tests/` – Test suite (unit + integration tests) organized per app.
- `docs/` – Documentation and testing examples.

---

## 📦 Main Application Apps (in `apps/`)

Each app follows a standard Django REST structure:

- `models.py` – database model definitions
- `serializers.py` – DRF serializers for JSON input/output
- `views.py` – API view logic
- `urls.py` – app-specific URL routing
- `tests.py` – unit and integration tests
- `migrations/` – Django database migrations

Key apps:
- `products` – product catalog, images, categories, and seed data utilities.
- `cart` – shopping cart management.
- `orders` – order placement, status, and notifications (has `email_service.py`).
- `payments` – payment processing, including service layer.
- `reviews` – product reviews and ratings.
- `users` – authentication, registration, email verification, password management.

---

## 🔧 Configuration

- `config/settings/base.py` – shared Django settings.
- `config/settings/development.py` – development-specific settings.
- `config/settings/production.py` – production-specific settings.
- `config/urls.py` – root URL router.

---

## 🧪 Testing

- `tests/` – contains test packages organized by app.
- `pytest.ini` – pytest configuration.

---

## 📄 Project Tree

Below is the current directory structure captured from the repository (depth limited for readability):

```text
C:\Users\User\Documents\GitHub\ecommerce-api
├── .pytest_cache
│   ├── v
│   │   └── cache
│   │       ├── lastfailed
│   │       └── nodeids
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── README.md
├── apps
│   ├── cart
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── orders
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_alter_orderitem_price_alter_orderitem_product_sku.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── email_service.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── payments
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── products
│   │   ├── management
│   │   │   ├── commands
│   │   │   │   ├── __init__.py
│   │   │   │   └── seed_data.py
│   │   │   └── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_product.py
│   │   │   ├── 0003_productimage.py
│   │   │   ├── 0004_remove_product_products_slug_5e91f2_idx_and_more.py
│   │   │   └── __init__.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   └── product_service.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── reviews
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── users
│       ├── migrations
│       │   ├── 0001_initial.py
│       │   ├── 0002_userconfirmation_alter_user_options_and_more.py
│       │   └── __init__.py
│       ├── services
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── email_service.py
│       │   ├── password_service.py
│       │   ├── token_service.py
│       │   └── verification_service.py
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── config
│   ├── settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── __init__.py
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── core
│   ├── services
│   │   └── __init__.py
│   ├── __init__.py
│   ├── emails.py
│   ├── permissions.py
│   └── utils.py
├── docs
│   ├── testing
│   │   ├── mock_examples.py
│   │   ├── parametrize_examples.py
│   │   ├── README.md
│   │   └── test_guide.py
│   └── README.md
├── screenshots
│   ├── bulk_action_1.png
│   ├── bulk_action_2.png
│   ├── cart_detail.png
│   ├── cart_items.png
│   ├── category_list.png
│   ├── failed_payment_detail.png
│   ├── filter_by_rating.png
│   ├── filter_by_status.png
│   ├── order_detail.png
│   ├── orders_list.png
│   ├── payment_detail.png
│   ├── payment_list.png
│   ├── product_detail.png
│   ├── product_image.png
│   ├── product_list.png
│   ├── review_detail.png
│   ├── reviews_list.png
│   ├── search_results.png
│   └── shopping_cart.png
├── scripts
│   └── dump_structure.py
├── templates
│   └── emails
│       ├── order_confirmation.html
│       ├── order_delivered.html
│       ├── order_shipped.html
│       └── payment_confirmation.html
├── tests
│   ├── cart
│   │   ├── __init__.py
│   │   ├── test_cart_api.py
│   │   └── test_cart_models.py
│   ├── orders
│   │   ├── __init__.py
│   │   ├── test_order_api.py
│   │   ├── test_order_models.py
│   │   └── test_order_notifications.py
│   ├── payments
│   │   ├── __init__.py
│   │   ├── test_payment_api.py
│   │   └── test_payment_models.py
│   ├── performance
│   │   ├── __init__.py
│   │   └── test_cache.py
│   ├── products
│   │   ├── __init__.py
│   │   ├── test_category_api.py
│   │   ├── test_category_model.py
│   │   ├── test_product_image_model.py
│   │   ├── test_product_images.py
│   │   ├── test_product_model.py
│   │   └── test_product_search.py
│   ├── reviews
│   │   ├── __init__.py
│   │   ├── test_review_api.py
│   │   └── test_review_models.py
│   ├── users
│   │   ├── __init__.py
│   │   ├── test_email_verification.py
│   │   ├── test_login_logout.py
│   │   ├── test_password_reset.py
│   │   ├── test_profile.py
│   │   └── test_registration.py
│   ├── __init__.py
│   ├── conftest.py
│   └── factories.py
├── .env
├── .gitignore
├── cleanup-merged-branches.ps1
├── db.sqlite3
├── LICENSE
├── manage.py
├── Procfile
├── pytest.ini
├── README.md
├── requirements.txt
└── runtime.txt
```
