# 🛍️ E-commerce API

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![Tests](https://img.shields.io/badge/Tests-10%20passing-success.svg)](./tests/)
[![Coverage](https://img.shields.io/badge/Coverage-62%25-yellow.svg)](./htmlcov/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

Professional RESTful API for e-commerce platform built with Django REST Framework. Features include user authentication, email verification, password management, and comprehensive testing infrastructure.

---

## ✨ Features

### 🔐 Authentication & Authorization
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Email Verification** - Link and code-based email confirmation
- ✅ **Password Management** - Change, reset, and recovery
- ✅ **Email Management** - Update and verify email changes
- ✅ **User Profiles** - Complete CRUD operations

### 📧 Email System
- ✅ **HTML Email Templates** - Beautiful, responsive emails
- ✅ **Verification Codes** - 6-digit secure codes with expiration
- ✅ **Password Reset Links** - Secure token-based reset flow
- ✅ **Email Change Verification** - Confirm new email addresses

### 🧪 Testing Infrastructure
- ✅ **Pytest** - Modern testing framework
- ✅ **62% Code Coverage** - Baseline established
- ✅ **Factory Pattern** - Clean test data generation
- ✅ **Mock Services** - Isolated unit tests
- ✅ **Integration Tests** - End-to-end flow validation

### 📚 API Documentation
- ✅ **Swagger UI** - Interactive API explorer
- ✅ **ReDoc** - Beautiful API documentation
- ✅ **OpenAPI 3.0** - Industry-standard schema

### 🏗️ Architecture
- ✅ **Service Layer Pattern** - Clean business logic separation
- ✅ **Modular Apps** - Scalable project structure
- ✅ **Custom User Model** - Extensible authentication
- ✅ **UUID Primary Keys** - Enhanced security

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip
- virtualenv (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file in project root
cp .env.example .env

# Edit .env with your settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

🎉 **API is now running at:** `http://localhost:8000/`

---

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### Main Endpoints

#### Authentication
```http
POST   /api/users/register/          # Register new user
POST   /api/users/login/             # Login user
POST   /api/users/logout/            # Logout user
POST   /api/token/refresh/           # Refresh access token
```

#### Email Verification
```http
GET    /api/users/verify-email/      # Verify via link
POST   /api/users/verify-email/      # Verify via code
POST   /api/users/resend-verification/ # Resend code
```

#### Password Management
```http
POST   /api/users/change-password/   # Change password
POST   /api/users/forgot-password/   # Request reset
POST   /api/users/reset-password/    # Reset password
```

#### Profile Management
```http
GET    /api/users/profile/           # Get profile
PUT    /api/users/profile/           # Update profile
PATCH  /api/users/profile/           # Partial update
```

#### Email Management
```http
POST   /api/users/change-email/      # Request email change
POST   /api/users/verify-email-change/ # Confirm new email
```

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific test file
pytest tests/users/test_registration.py

# Run with coverage
pytest --cov=apps --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Test Structure
```
tests/
├── conftest.py              # Shared fixtures
├── factories.py             # Test data factories
└── users/
    └── test_registration.py # Registration tests
```

### Current Coverage: 62%
- `users/models.py`: 89%
- `users/verification_service.py`: 73%
- `users/serializers.py`: 60%
- `users/auth_service.py`: 61%

---

## 📁 Project Structure

```
ecommerce-api/
├── apps/                    # Application modules
│   ├── users/              # ✅ User authentication (Complete)
│   ├── products/           # 🚧 Products (Planned)
│   ├── cart/               # 🚧 Shopping cart (Planned)
│   ├── orders/             # 🚧 Order management (Planned)
│   ├── payments/           # 🚧 Payment processing (Planned)
│   └── reviews/            # 🚧 Product reviews (Planned)
│
├── core/                   # Shared utilities
│   ├── emails.py          # Email templates
│   └── utils.py           # Helper functions
│
├── ecommerce_api/         # Project settings
│   ├── settings/          # Environment-specific settings
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── tests/                 # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── factories.py      # Test data factories
│   └── users/            # User app tests
│
├── docs/                  # Documentation
│   ├── README.md         # Docs overview
│   └── testing/          # Testing guides
│
├── pytest.ini            # Pytest configuration
├── requirements.txt      # Python dependencies
├── manage.py            # Django management
└── README.md            # This file
```

---

## 🏗️ Architecture

### Service Layer Pattern
Business logic is separated from views using service classes:

```
View (API Layer)
    ↓
Serializer (Validation)
    ↓
Service (Business Logic)
    ↓
Model (Data Layer)
```

### Example Flow
```python
# View
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = auth_service.register_user(serializer.validated_data)
    return Response(user_data, status=201)

# Service
def register_user(data):
    user = User.objects.create_user(**data)
    verification_service.send_email_verification(user)
    return user
```

---

## 🔐 Security Features

- ✅ **JWT Token Authentication** with rotation and blacklisting
- ✅ **Password Validation** - Django's built-in validators
- ✅ **Email Normalization** - Lowercase storage
- ✅ **UUID Primary Keys** - Difficult to enumerate
- ✅ **CORS Configuration** - Controlled cross-origin access
- ✅ **CSRF Protection** - Django's CSRF middleware
- ✅ **Secure Password Hashing** - Argon2/PBKDF2

---

## 🛠️ Technologies Used

### Core Framework
- **Django 6.0.1** - Web framework
- **Django REST Framework 3.16.1** - REST API toolkit
- **djangorestframework-simplejwt 5.5.1** - JWT authentication

### Database
- **SQLite** - Development
- **PostgreSQL** - Production (planned)

### Testing
- **pytest 8.0.0** - Testing framework
- **pytest-django 4.7.0** - Django integration
- **pytest-cov 4.1.0** - Coverage reporting
- **factory-boy 3.3.0** - Test data generation
- **faker 22.6.0** - Fake data

### API Documentation
- **drf-spectacular 0.29.0** - OpenAPI 3.0 schema generation

### Code Quality
- **flake8 7.0.0** - Linting
- **black 24.1.1** - Code formatting
- **isort 5.13.2** - Import sorting

---

## 📊 Development Status

### Completed Modules ✅
- [x] User Authentication
- [x] Email Verification
- [x] Password Management
- [x] User Profile CRUD
- [x] Testing Infrastructure
- [x] API Documentation

### In Progress 🚧
- [ ] Products Management
- [ ] Shopping Cart
- [ ] Order Processing
- [ ] Payment Integration
- [ ] Product Reviews

### Planned 📋
- [ ] Admin Dashboard
- [ ] Analytics & Reporting
- [ ] Notifications System
- [ ] Wishlist Feature
- [ ] Discount/Coupon System
- [ ] Multi-language Support
- [ ] Image Optimization
- [ ] Caching (Redis)
- [ ] Background Tasks (Celery)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write/update tests
5. Ensure tests pass (`pytest`)
6. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Commit Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Oktam Turgunov (Uktam)**

- GitHub: [@OktamTurgun](https://github.com/OktamTurgun)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

---

## 📞 Support

If you have any questions or issues:

1. Check the [Documentation](./docs/)
2. Search [existing issues](https://github.com/OktamTurgun/ecommerce-api/issues)
3. Open a [new issue](https://github.com/OktamTurgun/ecommerce-api/issues/new)

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ User Authentication & Management
- ✅ Testing Infrastructure
- ✅ API Documentation

### Version 2.0 (Q2 2026)
- 🚧 Products & Categories
- 🚧 Shopping Cart
- 🚧 Order Management

### Version 3.0 (Q3 2026)
- 📋 Payment Integration
- 📋 Reviews & Ratings
- 📋 Admin Dashboard

### Version 4.0 (Q4 2026)
- 📋 Advanced Features
- 📋 Performance Optimization
- 📋 Scalability Improvements

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/OktamTurgun">Oktam Turgunov</a>
</p>

<p align="center">
  ⭐ Star this repo if you find it helpful!
</p>