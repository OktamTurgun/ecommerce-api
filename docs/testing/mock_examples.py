"""
MOCK - Detailed Explanation and Examples

Mock = "Soxta" obyekt, real funksiyani almashtiradi.
"""

import requests
from django.core.mail import send_mail
from django.test import Client

# ========================================
# MISOL 1: Email yuborishni mock qilish
# ========================================

# Real kod (apps/users/services/email_service.py)
def send_verification_email(user_email, code):
    """Real email yuboradi"""
    send_mail(
        subject='Email Verification',
        message=f'Your code: {code}',
        from_email='noreply@example.com',
        recipient_list=[user_email],
    )
    print(f"📧 Email sent to {user_email}")


# ❌ YOMON: Mock'siz test
def test_registration_sends_email_BAD():
    """Bu test REAL email yuboradi! (yomon)"""
    client = Client()
    response = client.post('/api/register/', {
        'email': 'test@test.com',
        'password': 'Test123!'
    })
    
    # Muammo: Real email ketdi! 
    # - Gmail serveriga ulanish kerak
    # - Internet kerak
    # - Sekin ishlaydi
    # - Har test uchun spam email yuboriladi


# ✅ YAXSHI: Mock bilan test
def test_registration_sends_email_GOOD(mocker):
    """Bu test SOXTA email yuboradi (yaxshi)"""
    # Mock yaratamiz
    mock_send_email = mocker.patch('apps.users.services.email_service.send_mail')
    
    client = Client()
    response = client.post('/api/register/', {
        'email': 'test@test.com',
        'password': 'Test123!'
    })
    
    # Tekshiramiz: Email funksiyasi chaqirilganmi?
    mock_send_email.assert_called_once()
    
    # Tekshiramiz: To'g'ri parametrlar berilganmi?
    assert mock_send_email.call_args[1]['recipient_list'] == ['test@test.com']
    
    # Afzallik: Real email yuborilmadi, test tez ishladi!


# ========================================
# MISOL 2: To'lovni mock qilish
# ========================================

# Real kod
def process_payment(card_number, amount):
    """Real to'lov qiladi"""
    response = requests.post('https://payment-gateway.com/charge', {
        'card': card_number,
        'amount': amount
    })
    return response.json()


# ✅ Mock bilan test
def test_payment_processing(mocker):
    """To'lovni soxta qilamiz"""
    # Mock: Real API ga so'rov yubormaslik
    mock_payment = mocker.patch('requests.post')
    
    # Mock javob qaytarsin
    mock_payment.return_value.json.return_value = {
        'status': 'success',
        'transaction_id': '12345'
    }
    
    # Test qilamiz
    result = process_payment('4111111111111111', 100.00)
    
    # Tekshiramiz
    assert result['status'] == 'success'
    assert result['transaction_id'] == '12345'
    
    # Real to'lov qilinmadi! ✅


# ========================================
# MISOL 3: Vaqtni mock qilish
# ========================================

from django.utils import timezone
from datetime import timedelta

def is_code_expired(code_created_at):
    """Kod 15 daqiqadan keyin eskiradi"""
    now = timezone.now()
    expiry = code_created_at + timedelta(minutes=15)
    return now > expiry


# ✅ Vaqtni mock qilish
def test_code_expiration(mocker):
    """Vaqtni boshqaramiz"""
    
    # 1. Kod yaratildi (hozir)
    code_created = timezone.now()
    
    # 2. Vaqtni 20 daqiqaga o'tkazamiz (mock)
    future_time = code_created + timedelta(minutes=20)
    mocker.patch('django.utils.timezone.now', return_value=future_time)
    
    # 3. Tekshiramiz
    assert is_code_expired(code_created) == True
    
    # Real vaqtda 20 daqiqa kutmadik! ✅


# ========================================
# MOCK METODLARI
# ========================================

def test_mock_methods(mocker):
    """Mock'ning muhim metodlari"""
    
    # 1. patch - funksiyani almashtirish
    mock = mocker.patch('module.function')
    
    # 2. return_value - qaytaradigan qiymat
    mock.return_value = "Hello"
    assert function() == "Hello"
    
    # 3. side_effect - exception yoki dynamic qiymat
    mock.side_effect = ValueError("Error!")
    # function() → ValueError raise bo'ladi
    
    # 4. assert_called_once - bir marta chaqirilganmi?
    function()
    mock.assert_called_once()
    
    # 5. assert_called_with - qanday parametr bilan?
    function('test')
    mock.assert_called_with('test')
    
    # 6. call_count - necha marta chaqirilgan?
    function()
    function()
    assert mock.call_count == 3


# ========================================
# QACHON MOCK ISHLATISH KERAK?
# ========================================

"""
✅ MOCK ISHLATING:
- Email/SMS yuborish
- To'lov gateway
- Tashqi API (Google, Facebook, va h.k.)
- File system (fayl o'qish/yozish)
- Vaqt (timezone.now, datetime.now)
- Random qiymatlar (uuid, random numbers)
- Sekin operatsiyalar

❌ MOCK ISHLATMANG:
- Database operatsiyalari (real DB ishlatiladi)
- Django ORM
- Serializer validation
- O'zingizning business logic
- Model metodlari
"""