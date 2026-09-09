from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.recommendation,
        name="recommendation"
    ),

    path(
        "random/",
        views.random_recommendation,
        name="random-recommendation"
    ),

]