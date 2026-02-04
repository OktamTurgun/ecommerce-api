# core/emails.py
"""
Email Service
-------------
Email yuborish uchun helper functions
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings


def send_verification_code_email(user, code):
    """
    Email verification code yuborish
    
    Args:
        user: User instance
        code: 6 raqamli kod
    
    Returns:
        bool: Success
    """
    subject = '🔐 Email Tasdiqlash Kodi - E-commerce'
    
    plain_message = f"""
Assalomu alaykum {user.get_full_name()}!

E-commerce platformamizga xush kelibsiz! 🎉

Emailingizni tasdiqlash uchun quyidagi kodni kiriting:

┌─────────────────┐
│  KOD: {code}  │
└─────────────────┘

⏰ Bu kod 15 daqiqa amal qiladi.
🔒 Kodni hech kim bilan baham ko'rmang!

Hurmat bilan,
E-commerce Jamoasi
    """.strip()
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; padding: 20px; }}
        .code-box {{ background: #667eea; color: white; font-size: 36px; font-weight: bold; 
                     padding: 20px; text-align: center; border-radius: 8px; margin: 30px 0; 
                     letter-spacing: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Assalomu alaykum, {user.get_full_name()}!</h2>
        <p>E-commerce platformamizga xush kelibsiz! 🎉</p>
        <p>Emailingizni tasdiqlash uchun quyidagi kodni kiriting:</p>
        <div class="code-box">{code}</div>
        <p>⏰ Bu kod <strong>15 daqiqa</strong> amal qiladi.</p>
        <p>🔒 Kodni hech kim bilan baham ko'rmang!</p>
    </div>
</body>
</html>
    """.strip()
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")
        return False


def send_password_reset_code_email(user, code):
    """
    Password reset code yuborish
    
    Args:
        user: User instance
        code: 6 raqamli kod
    
    Returns:
        bool: Success
    """
    subject = '🔑 Parolni Tiklash Kodi - E-commerce'
    
    plain_message = f"""
Assalomu alaykum {user.get_full_name()}!

Parolni tiklash so'rovi qabul qilindi.

Yangi parol o'rnatish uchun quyidagi kodni kiriting:

┌─────────────────┐
│  KOD: {code}  │
└─────────────────┘

⏰ Bu kod 15 daqiqa amal qiladi.

⚠️ Agar siz bu so'rovni yubormagan bo'lsangiz, 
akkauntingiz xavf ostida bo'lishi mumkin!

Hurmat bilan,
E-commerce Jamoasi
    """.strip()
    
    html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 10px; padding: 20px; }}
        .code-box {{ background: #f5576c; color: white; font-size: 36px; font-weight: bold; 
                     padding: 20px; text-align: center; border-radius: 8px; margin: 30px 0; 
                     letter-spacing: 8px; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Assalomu alaykum, {user.get_full_name()}!</h2>
        <p>Parolni tiklash so'rovi qabul qilindi.</p>
        <p>Yangi parol o'rnatish uchun quyidagi kodni kiriting:</p>
        <div class="code-box">{code}</div>
        <div class="warning">
            <strong>⚠️ XAVFSIZLIK:</strong><br>
            Agar siz bu so'rovni yubormagan bo'lsangiz, 
            akkauntingiz xavf ostida bo'lishi mumkin!
        </div>
    </div>
</body>
</html>
    """.strip()
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")
        return False


def send_email_change_code(user, new_email, code):
    """
    Email change verification code yuborish
    
    Args:
        user: User instance
        new_email: Yangi email
        code: 6 raqamli kod
    
    Returns:
        bool: Success
    """
    subject = '📧 Email O\'zgartirish Kodi - E-commerce'
    
    plain_message = f"""
Assalomu alaykum {user.get_full_name()}!

Email o'zgartirish so'rovi qabul qilindi.

Eski email: {user.email}
Yangi email: {new_email}

O'zgarishni tasdiqlash uchun quyidagi kodni kiriting:

┌─────────────────┐
│  KOD: {code}  │
└─────────────────┘

⏰ Bu kod 15 daqiqa amal qiladi.

Hurmat bilan,
E-commerce Jamoasi
    """.strip()
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],  # Yangi email'ga yuboriladi!
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")
        return False
    
def send_password_reset_link_email(user, reset_url):
    """
    Parolni tiklash linkini yuborish
    Args:
        user: User instance
        reset_url: Frontend URL + uidb64 + token
    Returns:
        bool: success
    """
    subject = "🔑 Parolni Tiklash - E-commerce"

    plain_message = f"""
Assalomu alaykum {user.get_full_name()}!

Parolingizni tiklash so'rovi qabul qilindi.
Quyidagi link orqali yangi parol o'rnating:

{reset_url}

⏰ Link 30 daqiqa davomida amal qiladi.

Agar bu so'rovni siz yubormagan bo'lsangiz, uni e'tiborsiz qoldiring.

Hurmat bilan,
E-commerce Jamoasi
    """.strip()

    html_message = f"""
<html>
<body>
<h2>Assalomu alaykum, {user.get_full_name()}!</h2>
<p>Parolingizni tiklash so'rovi qabul qilindi.</p>
<p><a href="{reset_url}">Parolni tiklash uchun shu yerni bosing</a></p>
<p>⏰ Link 30 daqiqa davomida amal qiladi.</p>
<p>Agar siz bu so'rovni yubormagan bo'lsangiz, e'tiborsiz qoldiring.</p>
</body>
</html>
    """.strip()

    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"❌ Email yuborishda xatolik: {e}")
        return False
