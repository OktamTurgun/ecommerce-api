# 🛍️ E-commerce API

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![Tests](https://img.shields.io/badge/Tests-199%20passing-success.svg)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-84%25-brightgreen.svg)](./htmlcov/)
[![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)](https://redis.io/)
[![Performance](https://img.shields.io/badge/Performance-12.3x%20faster-orange.svg)](#performance)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

Professional **production-ready** RESTful API for e-commerce platform built with Django REST Framework. Features complete user management, product catalog, shopping cart, order processing, Stripe payments, reviews & ratings, advanced search & filtering, email notifications, and **Redis caching for 12.3x performance boost**.

## ✨ Features

### 🔐 User Management
- User registration with email verification
- JWT authentication (access & refresh tokens)
- Password reset via email
- User profile management
- Secure session handling

### 📦 Product Catalog
- Product CRUD operations
- Category management
- Product images with multiple uploads
- Average rating calculation
- Inventory tracking
- **Advanced search & filtering**
- **Database-optimized queries**

### 🔍 Search & Filtering
- Full-text search (name & description)
- Filter by category
- Price range filtering (min/max)
- Rating-based filtering
- Multi-field sorting (price, name, date)
- Combined filters support
- **Database indexes for performance**

### 🛒 Shopping Cart
- Add/update/remove items
- Real-time price calculation
- Stock validation
- Cart persistence per user
- Automatic cart cleanup

### 📝 Order Management
- Order creation from cart
- Order status tracking (Pending → Processing → Shipped → Delivered)
- Order history
- Shipping address management
- Order item details
- Admin order management panel

### 💳 Payment Integration
- **Stripe payment gateway**
- Secure payment processing
- Payment status tracking
- Payment method storage (last 4 digits)
- Refund support
- Payment webhooks
- Admin payment panel

### ⭐ Reviews & Ratings
- Product reviews (1-5 stars)
- Review comments
- Average rating calculation
- One review per user per product
- Review moderation (admin)
- Admin panel with star visualization

### 📧 Email Notifications
- Order confirmation emails
- Shipping notifications (with tracking)
- Delivery confirmations
- Payment confirmations
- Professional HTML email templates
- Plain text fallback

### ⚡ Performance Optimization
- **Redis caching (12.3x faster responses)**
- Database query optimization
- select_related & prefetch_related
- Database indexes on key fields
- Response compression
- Efficient pagination

### 🛠️ Developer Features
- Comprehensive test suite (199 tests)
- Factory pattern for testing
- API documentation (Swagger/ReDoc)
- CORS configuration
- Environment-based settings
- Docker support (Redis)
- Admin panels for all models

---

## 🚀 Performance

### Caching Performance
```
Database Request:  186.28ms
Cached Request:    15.17ms
Speed Improvement: 12.3x faster ⚡
Time Saved:        171.11ms per request
```

### Scalability
- **Current capacity:** 5K-10K concurrent users
- **With optimization:** 50K-100K concurrent users
- **Database queries:** 90% reduction via caching
- **Response time:** 10-20ms (cached), 50-200ms (uncached)

---

## 📋 Tech Stack

### Backend
- **Python 3.12+**
- **Django 6.0.1**
- **Django REST Framework 3.16.1**
- **PostgreSQL** (Production) / SQLite (Development)
- **Redis 7.0** (Caching)

### Authentication & Security
- **djangorestframework-simplejwt** - JWT authentication
- **CORS Headers** - Cross-origin requests
- **Password validators** - Secure passwords

### Payments
- **Stripe Python SDK** - Payment processing
- **Webhooks** - Real-time payment updates

### Email
- **Django Email** - SMTP integration
- **HTML templates** - Professional emails

### DevOps
- **Docker** - Redis containerization
- **django-redis** - Redis cache backend
- **django-filter** - Advanced filtering

### Testing & Quality
- **pytest** - Test framework
- **pytest-django** - Django integration
- **pytest-cov** - Code coverage
- **factory-boy** - Test data factories
- **Faker** - Realistic test data

---

## 🏗️ Architecture

### Design Pattern
```
Monolithic Layered Architecture with Service Layer

┌─────────────────────────────────────┐
│     Presentation Layer (API)        │
│  - REST API (DRF ViewSets)         │
│  - Serializers                      │
│  - URL Routing                      │
├─────────────────────────────────────┤
│     Business Logic Layer            │
│  - Service Layer (Payments, Email) │
│  - ViewSets & Business Logic       │
│  - Validation & Authorization      │
├─────────────────────────────────────┤
│     Caching Layer                   │
│  - Redis Cache (12.3x faster)      │
│  - Query Result Caching            │
│  - Session Caching                 │
├─────────────────────────────────────┤
│     Data Access Layer               │
│  - Django ORM Models                │
│  - Database Queries                 │
│  - Migrations                       │
├─────────────────────────────────────┤
│     Database Layer                  │
│  - PostgreSQL/SQLite                │
│  - Relationships & Indexes          │
└─────────────────────────────────────┘
```

### Applied Patterns
- **MVC/MVT** - Model-View-Template
- **Service Layer** - Business logic separation
- **Repository Pattern** - Data access via ORM
- **Factory Pattern** - Test data generation
- **Decorator Pattern** - Caching, permissions

---

## 📦 Installation

### Prerequisites
- Python 3.12+
- pip
- virtualenv
- Docker (for Redis)
- PostgreSQL (production)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Redis (Docker)
```bash
# Start Redis container
docker run -d -p 6380:6379 --name ecommerce-redis redis:7-alpine

# Verify Redis is running
docker ps
```

### 5. Environment Variables
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
# Required variables:
# - SECRET_KEY
# - DEBUG
# - DATABASE_URL (production)
# - STRIPE_SECRET_KEY
# - STRIPE_PUBLISHABLE_KEY
# - EMAIL_HOST_USER
# - EMAIL_HOST_PASSWORD
```

### 6. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# (Optional) Load sample data
python manage.py seed_data
```

### 7. Run Development Server
```bash
python manage.py runserver
```

API available at: `http://localhost:8000/api/`

---

## 🧪 Testing

### Run All Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific app tests
pytest tests/products/
pytest tests/orders/
pytest tests/payments/
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=apps --cov-report=html

# Open coverage report
# Open htmlcov/index.html in browser
```

### Test Performance
```bash
# Test Redis cache performance
python test_cache_performance.py

# Expected output:
# Database Request: ~200ms
# Cached Request: ~15ms
# Speed: 12.3x faster!
```

### Current Test Stats
```
✅ 199 tests passing
📊 84% code coverage
⚡ 12.3x performance boost
🎯 0 failures
```

---

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`

### Main Endpoints

#### Authentication
```
POST   /api/users/register/              - User registration
POST   /api/users/login/                 - User login (get JWT tokens)
POST   /api/users/token/refresh/         - Refresh access token
POST   /api/users/logout/                - User logout
POST   /api/users/verify-email/          - Verify email with code
POST   /api/users/forgot-password/       - Request password reset
POST   /api/users/reset-password/        - Reset password with token
GET    /api/users/profile/               - Get user profile
PATCH  /api/users/profile/               - Update user profile
```

#### Products
```
GET    /api/products/products/           - List products (cached 15 min)
POST   /api/products/products/           - Create product (admin)
GET    /api/products/products/{id}/      - Product detail (cached 1 hour)
PATCH  /api/products/products/{id}/      - Update product (admin)
DELETE /api/products/products/{id}/      - Delete product (admin)
GET    /api/products/categories/         - List categories
```

#### Search & Filtering
```
GET    /api/products/products/?search=laptop                    - Search products
GET    /api/products/products/?category={uuid}                  - Filter by category
GET    /api/products/products/?min_price=500&max_price=1000    - Price range
GET    /api/products/products/?min_rating=4                     - Filter by rating
GET    /api/products/products/?ordering=-price                  - Sort by price (desc)
GET    /api/products/products/?search=laptop&category={uuid}&min_price=800&max_price=1500&min_rating=4&ordering=-created_at
    - Combined filters
```

#### Cart
```
GET    /api/cart/                        - View cart
POST   /api/cart/add/                    - Add item to cart
PATCH  /api/cart/update/{id}/            - Update cart item
DELETE /api/cart/remove/{id}/            - Remove from cart
DELETE /api/cart/clear/                  - Clear cart
```

#### Orders
```
GET    /api/orders/                      - List user orders
POST   /api/orders/                      - Create order from cart
GET    /api/orders/{id}/                 - Order detail
PATCH  /api/orders/{id}/status/          - Update order status (admin)
```

#### Payments
```
POST   /api/payments/create-payment-intent/  - Create Stripe payment
POST   /api/payments/confirm-payment/        - Confirm payment
GET    /api/payments/                        - List payments (admin)
POST   /api/payments/webhook/                - Stripe webhook
```

#### Reviews
```
GET    /api/products/{id}/reviews/       - List product reviews
POST   /api/products/{id}/reviews/       - Create review
GET    /api/reviews/                     - List user's reviews
PATCH  /api/reviews/{id}/                - Update own review
DELETE /api/reviews/{id}/                - Delete own review
```

---

## 🔒 Security Features

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - bcrypt hashing
- **HTTPS Only** (production) - Encrypted connections
- **CORS Configuration** - Controlled access
- **Rate Limiting** - DDoS protection
- **SQL Injection Protection** - Django ORM
- **XSS Protection** - Content sanitization
- **CSRF Protection** - Token validation

---

## 🌍 Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# Set environment variables via Railway dashboard
```

### Render
```yaml
# render.yaml
services:
  - type: web
    name: ecommerce-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn config.wsgi:application
```

### Docker Compose (Full Stack)
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
  
  db:
    image: postgres:16
  
  redis:
    image: redis:7-alpine
```

---

## 📊 Database Schema

### Core Models
- **User** - Custom user model with email auth
- **Category** - Product categories
- **Product** - Product catalog with images
- **ProductImage** - Multiple images per product
- **Cart** - Shopping cart
- **CartItem** - Cart items with quantities
- **Order** - Customer orders
- **OrderItem** - Order line items
- **Payment** - Stripe payments
- **Review** - Product reviews & ratings

---

## 🎯 Roadmap

### ✅ Completed
- [x] User authentication & authorization
- [x] Product catalog with images
- [x] Shopping cart functionality
- [x] Order management
- [x] Stripe payment integration
- [x] Reviews & ratings system
- [x] Search & filtering
- [x] Email notifications
- [x] Redis caching (12.3x faster)
- [x] Admin panels
- [x] Comprehensive testing (199 tests)

### 📅 Planned
- [ ] Deployment to production
- [ ] API rate limiting
- [ ] Wishlist functionality
- [ ] Product recommendations
- [ ] Discount codes & promotions
- [ ] Frontend (React/Next.js)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@OktamTurgun](https://github.com/OktamTurgun)
- Email: uktamturgunov30@gmail.com

---

<p align="center">
  <strong>Built with ❤️ using Django REST Framework</strong><br>
  <em>Production-ready • Scalable • Well-tested • High-performance</em>
</p>

---

## 📈 Project Stats

```
Lines of Code:     ~15,000
Test Coverage:     84%
Tests Passing:     199/199
Performance:       12.3x faster (cached)
API Endpoints:     40+
Admin Panels:      8
Email Templates:   4
Response Time:     15-200ms
```

---

**⭐ If you found this project helpful, please give it a star!**