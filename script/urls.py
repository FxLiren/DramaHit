from django.urls import path
from . import views

urlpatterns = [

    path('script-list/', views.script_list, name='script-list'),

    path(
        'script-detail/<int:script_id>/',
        views.script_detail,
        name='script-detail'
    ),

    path('script-detail-2/', views.script_detail_2, name='script-detail-2'),

    path(
        'my-favorite/',
        views.my_favorite,
        name='my-favorite'
    ),

    path(
        'favorite/<int:script_id>/',
        views.toggle_favorite,
        name='toggle-favorite'
    ),

]