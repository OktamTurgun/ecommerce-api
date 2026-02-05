"""
PARAMETRIZE - Real Loyihadagi Misollar

Parametrize turli test scenariolarini bir testda yozish imkonini beradi.
"""

import pytest
from rest_framework import status


# ========================================
# MISOL 1: Email Validation
# ========================================

@pytest.mark.parametrize('email, should_be_valid', [
    # Valid emails
    ('user@example.com', True),
    ('user.name@example.com', True),
    ('user+tag@example.com', True),
    ('user123@test.co.uk', True),
    
    # Invalid emails
    ('invalid', False),
    ('invalid@', False),
    ('@example.com', False),
    ('user@', False),
    ('user space@example.com', False),
    ('user@example', False),
])
def test_email_validation(api_client, email, should_be_valid):
    """Test turli xil email formatlarini"""
    data = {
        'email': email,
        'password': 'StrongPass123!',
        'password_confirm': 'StrongPass123!',
        'first_name': 'Test',
        'last_name': 'User',
    }
    
    response = api_client.post('/api/users/register/', data)
    
    if should_be_valid:
        assert response.status_code == status.HTTP_201_CREATED
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


# ========================================
# MISOL 2: Password Strength
# ========================================

@pytest.mark.parametrize('password, expected_status, error_key', [
    # Valid passwords
    ('StrongPass123!', status.HTTP_201_CREATED, None),
    ('MyP@ssw0rd', status.HTTP_201_CREATED, None),
    ('Abcd1234!@#$', status.HTTP_201_CREATED, None),
    
    # Invalid passwords
    ('weak', status.HTTP_400_BAD_REQUEST, 'password'),  # Juda qisqa
    ('12345678', status.HTTP_400_BAD_REQUEST, 'password'),  # Faqat raqam
    ('password', status.HTTP_400_BAD_REQUEST, 'password'),  # Kichik harf
    ('PASSWORD', status.HTTP_400_BAD_REQUEST, 'password'),  # Katta harf
    ('Pass123', status.HTTP_400_BAD_REQUEST, 'password'),  # Juda qisqa
])
def test_password_strength(api_client, password, expected_status, error_key):
    """Test turli xil parol kuchlari"""
    data = {
        'email': 'test@example.com',
        'password': password,
        'password_confirm': password,
        'first_name': 'Test',
        'last_name': 'User',
    }
    
    response = api_client.post('/api/users/register/', data)
    assert response.status_code == expected_status
    
    if error_key:
        assert error_key in response.data


# ========================================
# MISOL 3: HTTP Metodlar va Permissionlar
# ========================================

@pytest.mark.parametrize('endpoint, method, requires_auth', [
    ('/api/users/register/', 'POST', False),
    ('/api/users/login/', 'POST', False),
    ('/api/users/profile/', 'GET', True),
    ('/api/users/profile/', 'PATCH', True),
    ('/api/users/logout/', 'POST', True),
    ('/api/users/change-password/', 'POST', True),
])
def test_endpoint_authentication(api_client, authenticated_client, 
                                  endpoint, method, requires_auth):
    """Test qaysi endpoint authentication talab qiladi"""
    
    # Authenticated bo'lmagan client
    if method == 'GET':
        response = api_client.get(endpoint)
    elif method == 'POST':
        response = api_client.post(endpoint, {})
    elif method == 'PATCH':
        response = api_client.patch(endpoint, {})
    
    if requires_auth:
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    else:
        # 401 bo'lmasligi kerak (400 yoki 200 bo'lishi mumkin)
        assert response.status_code != status.HTTP_401_UNAUTHORIZED


# ========================================
# MISOL 4: Status Code bo'yicha test
# ========================================

@pytest.mark.parametrize('user_data, expected_status', [
    # Success cases
    (
        {
            'email': 'valid@test.com',
            'password': 'ValidPass123!',
            'password_confirm': 'ValidPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
        },
        status.HTTP_201_CREATED
    ),
    
    # Missing email
    (
        {
            'password': 'ValidPass123!',
            'password_confirm': 'ValidPass123!',
            'first_name': 'John',
        },
        status.HTTP_400_BAD_REQUEST
    ),
    
    # Missing password
    (
        {
            'email': 'valid@test.com',
            'first_name': 'John',
        },
        status.HTTP_400_BAD_REQUEST
    ),
    
    # Password mismatch
    (
        {
            'email': 'valid@test.com',
            'password': 'ValidPass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'John',
        },
        status.HTTP_400_BAD_REQUEST
    ),
])
def test_registration_scenarios(api_client, user_data, expected_status, mocker):
    """Test turli registration scenariolar"""
    mocker.patch('apps.users.services.email_service.send_mail')
    
    response = api_client.post('/api/users/register/', user_data)
    assert response.status_code == expected_status


# ========================================
# MISOL 5: Multiple parametrlar
# ========================================

@pytest.mark.parametrize('field_name', ['first_name', 'last_name', 'phone_number'])
@pytest.mark.parametrize('field_value', ['', '   ', None])
def test_empty_optional_fields(api_client, field_name, field_value, mocker):
    """Test optional field'larni bo'sh qoldirish"""
    mocker.patch('apps.users.services.email_service.send_mail')
    
    data = {
        'email': 'test@example.com',
        'password': 'ValidPass123!',
        'password_confirm': 'ValidPass123!',
        field_name: field_value,
    }
    
    response = api_client.post('/api/users/register/', data)
    
    # Optional field bo'lsa - success
    # Required field bo'lsa - error
    # Bu yerda biz optional/required'ni aniqlashimiz mumkin


# ========================================
# MISOL 6: IDs bilan ishlash (kelajak uchun)
# ========================================

@pytest.mark.parametrize('product_id, expected_status', [
    (1, status.HTTP_200_OK),           # Mavjud product
    (9999, status.HTTP_404_NOT_FOUND), # Mavjud emas
    (-1, status.HTTP_404_NOT_FOUND),   # Noto'g'ri ID
    (0, status.HTTP_404_NOT_FOUND),    # Nol ID
])
def test_product_detail_scenarios(api_client, product_id, expected_status):
    """Test product detail turli ID'lar bilan"""
    pytest.skip("Products app hali yaratilmagan")
    
    response = api_client.get(f'/api/products/{product_id}/')
    assert response.status_code == expected_status


# ========================================
# AFZALLIKLAR
# ========================================

"""
✅ PARAMETRIZE AFZALLIKLARI:

1. Kod takrorlanmaydi
   - Bir test, ko'p scenariolar
   
2. Yangi scenario qo'shish oson
   - Faqat list'ga qo'shish kifoya
   
3. Test natijalarini ko'rish oson
   - Har bir scenario alohida ko'rinadi
   
4. Maintain qilish oson
   - Bitta joyda barcha scenariolar
   
5. Coverage oshiradi
   - Ko'proq edge case'larni test qilish

📊 NATIJA:
   test_email_validation[user@example.com-True] ✅ PASSED
   test_email_validation[invalid-False] ✅ PASSED
   test_email_validation[invalid@-False] ✅ PASSED
   ...
"""