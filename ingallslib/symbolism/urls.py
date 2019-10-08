from django.urls import path
from . import views


urlpatterns = [

    path('', views.home, name="symbolism-home"),
    path('discover/', views.discover, name="symbolism-results")
]
