from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_password_reset_email(user, reset_url):
    """
    Password reset email yuborish

    Args:
        user: User instance
        reset_url: Full reset URL with token

    Example:
        reset_url = "http://localhost:3000/reset-password?token=abc&uid=MQ"
    """
    subject = 'Parolni tiklash - E-commerce'

    # HTML message
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>Salom, {user.get_full_name() or user.email}!</h2>
            
            <p>Siz parolni tiklash so'rovini yubordingiz.</p>
            
            <p>Yangi parol o'rnatish uchun quyidagi tugmani bosing:</p>
            
            <p style="margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #007bff; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px;
                          display: inline-block;">
                    Parolni tiklash
                </a>
            </p>
            
            <p>Yoki quyidagi linkni nusxalang:</p>
            <p style="color: #666; word-break: break-all;">{reset_url}</p>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                <strong>Muhim:</strong> Bu link 24 soat amal qiladi.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                Agar siz bu so‘rovni yubormagan bo‘lsangiz, 
                bu emailni e’tiborsiz qoldiring.
            </p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #999; font-size: 12px;">
                E-commerce Team<br>
                Bu avtomatik email, javob bermang.
            </p>
        </body>
    </html>
    """
    # Plain text version
    plain_message = f"""
    Salom, {user.get_full_name() or user.email}!
    
    Siz parolni tiklash so'rovini yubordingiz.
    
    Yangi parol o'rnatish uchun quyidagi linkni oching:
    {reset_url}
    
    Bu link 24 soat amal qiladi.
    
    Agar siz bu so'rovni yubormaganingizda bo'lsa, bu emailni e'tiborsiz qoldiring.
    
    E-commerce Team
    """
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_verification_email(user, verification_url):
    """
    Email verification link yuborish
    
    Args:
        user: User instance
        verification_url: Full verification URL with token
    """
    subject = 'Email manzilni tasdiqlang - E-commerce'
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>Xush kelibsiz, {user.get_full_name() or user.email}!</h2>
            
            <p>E-commerce'ga ro'yxatdan o'tganingiz uchun rahmat!</p>
            
            <p>Akkauntingizni faollashtirish uchun email manzilingizni tasdiqlang:</p>
            
            <p style="margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #28a745; 
                          color: white; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px;
                          display: inline-block;">
                    Email'ni tasdiqlash
                </a>
            </p>
            
            <p>Yoki quyidagi linkni nusxalang:</p>
            <p style="color: #666; word-break: break-all;">{verification_url}</p>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                <strong>Muhim:</strong> Bu link 7 kun amal qiladi.
            </p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #999; font-size: 12px;">
                E-commerce Team<br>
                Bu avtomatik email, javob bermang.
            </p>
        </body>
    </html>
    """
    
    plain_message = f"""
    Xush kelibsiz, {user.get_full_name() or user.email}!
    
    E-commerce'ga ro'yxatdan o'tganingiz uchun rahmat!
    
    Akkauntingizni faollashtirish uchun quyidagi linkni oching:
    {verification_url}
    
    Bu link 7 kun amal qiladi.
    
    E-commerce Team
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_email_change_verification(user, new_email, verification_url):
    """
    Email o'zgartirish uchun tasdiqlash linki yuborish
    
    Args:
        user: User instance
        new_email: Yangi email manzil
        verification_url: Verification URL with token
    """
    subject = "Email manzilni o'zgartirish - E-commerce"

    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>Salom, {user.get_full_name() or user.email}!</h2>
            
            <p>Siz email manzilingizni o'zgartirish so'rovini yubordingiz.</p>
            
            <p><strong>Hozirgi email:</strong> {user.email}</p>
            <p><strong>Yangi email:</strong> {new_email}</p>
            
            <p>O'zgarishni tasdiqlash uchun quyidagi tugmani bosing:</p>
            
            <p style="margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #ffc107; 
                          color: #000; 
                          padding: 12px 24px; 
                          text-decoration: none; 
                          border-radius: 4px;
                          display: inline-block;">
                    Email o'zgarishini tasdiqlash
                </a>
            </p>
            
            <p>Yoki quyidagi linkni nusxalang:</p>
            <p style="color: #666; word-break: break-all;">{verification_url}</p>
            
            <p style="margin-top: 30px; color: #666; font-size: 14px;">
                <strong>Muhim:</strong> Bu link 1 soat amal qiladi.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                Agar siz bu so'rovni yubormagan bo'lsangiz, 
                bu emailni e'tiborsiz qoldiring va parolingizni o'zgartiring.
            </p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
            
            <p style="color: #999; font-size: 12px;">
                E-commerce Team<br>
                Bu avtomatik email, javob bermang.
            </p>
        </body>
    </html>
    """
    plain_message = f"""
    Salom, {user.get_full_name() or user.email}!
    
    Siz email manzilingizni o'zgartirish so'rovini yubordingiz.
    
    Hozirgi email: {user.email}
    Yangi email: {new_email}
    
    O'zgarishni tasdiqlash uchun quyidagi linkni oching:
    {verification_url}
    
    Bu link 1 soat amal qiladi.
    
    Agar siz bu so'rovni yubormaganingizda bo'lsa, 
    bu emailni e'tiborsiz qoldiring va parolingizni o'zgartiring.
    
    E-commerce Team
    """
    # Yangi email'ga yuborish (eski email emas!)
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email],  # ← Yangi email!
        html_message=html_message,
        fail_silently=False,
    )