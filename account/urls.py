from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomSetPasswordForm


urlpatterns = [
    path('', views.account, name='account'),

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'verify-email/<int:user_id>/<str:token>/',
        views.verify_email,
        name='verify-email'
    ),

    # 忘記密碼
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='account/password_reset.html',
            email_template_name='account/password_reset_email.html'
        ),
        name='password-reset'
    ),

    # 忘記密碼 Email 寄送完成
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='account/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # 設定新密碼
    path(
        'password-reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='account/password_reset_confirm.html',
            form_class=CustomSetPasswordForm
        ),
        name='password-reset-confirm'
    ),

    # 密碼重設完成
    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='account/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'member-center/',
        views.member_center,
        name='member-center'
    ),
]