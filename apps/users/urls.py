from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    ChangePasswordView,
    UserListView,
    ForgotPasswordView,
    ResetPasswordView,
    VerifyEmailView,
    ResendVerificationView,
    ChangeEmailView,
    VerifyEmailChangeView,
)

app_name = "users"

urlpatterns = [
    # ============ AUTHENTICATION ============
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    # ============ EMAIL VERIFICATION ============
    path("verify-email/", VerifyEmailView.as_view(), name='verify-email'),
    path("resend-verification/", ResendVerificationView.as_view(), name='sesend-verification'),

    # ============ PROFILE ============
    path("profile/", UserProfileView.as_view(), name="profile"),

    # =========== PASSWORD MANAGEMENT ============
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name='forgot-password'),
    path("reset-password/", ResetPasswordView.as_view(), name='reset-password'),

    # ============ EMAIL MANAGEMENT ============
    path("change-email/",ChangeEmailView.as_view(), name='change-email'),
    path("verify-email-change/", VerifyEmailChangeView.as_view(), name='verify-email-change'),

    # ============ ADMIN ============
    path("", UserListView.as_view(), name="list-view"),
]
