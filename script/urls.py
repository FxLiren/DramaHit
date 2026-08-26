from django.urls import path
from . import views

urlpatterns = [
    path('script-list/', views.script_list, name='script-list'),
    path('script-detail/', views.script_detail, name='script-detail'),
    path('script-detail-2/', views.script_detail_2, name='script-detail-2'),
]