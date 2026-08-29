from django.urls import path
from . import views

urlpatterns = [
    path('', views.account, name='account'),
    path('register/', views.register, name='register'),
    path(
        'verify-email/<int:user_id>/<str:token>/',
        views.verify_email,
        name='verify-email'
    ),
    path('logout/', views.logout_view, name='logout'),
]